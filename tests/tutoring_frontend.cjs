// Offline renderer contract checks; no DOM, CDN loading or network access.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('frontend/agents/tutoring/index.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script); // Verify syntax for the entire inline application.
const renderer = script.slice(script.indexOf('function renderReply('), script.indexOf('async function requestAnswer('));
const context = vm.createContext({window: {}});
vm.runInContext(renderer, context);
let content = {textContent: '', innerHTML: ''};
context.renderReply(content, '<img src=x onerror=alert(1)>');
assert.equal(content.innerHTML, '');
assert.match(content.textContent, /onerror/); // Plain text fallback.
const calls = [];
context.window.marked = {parse: text => { calls.push(['parse', text]); return 'untrusted HTML'; }};
context.window.DOMPurify = {sanitize: (html, options) => {
    calls.push(['sanitize', html]);
    assert.equal(options.USE_PROFILES.html, true);
    return 'sanitized HTML';
}};
context.renderReply(content, '```python\nprint(1)\n```');
assert.equal(content.innerHTML, 'sanitized HTML');
assert.deepEqual(calls.map(call => call[0]), ['parse', 'sanitize']);
context.window.DOMPurify.sanitize = () => { throw Error('unavailable'); };
content = {textContent: '', innerHTML: ''};
context.renderReply(content, 'fallback');
assert.equal(content.textContent, 'fallback');
assert.equal(content.innerHTML, '');
assert.match(script, /renderReply\(content, reply\)/);
for (const id of ['newChat', 'scrollLatest', 'characterCount', 'suggestions']) {
    assert.ok(html.includes(`id="${id}"`));
}
console.log('PASS: inline JS syntax; sanitized renderer wiring; plain-text and failure fallbacks; shared controls present');
