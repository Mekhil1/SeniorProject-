// Offline executable regression checks for the existing shared hub helpers.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('frontend/chat/index.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
function fixture() {
    const elements = new Map();
    function element() {
        return {value: '', textContent: '', dataset: {}, children: [],
            classList: {add() {}, remove() {}}, focus() {}, scrollIntoView() {}, addEventListener() {},
            appendChild(child) {this.children.push(child); this.lastElementChild = child;}};
    }
    const requests = [];
    const context = vm.createContext({
        localStorage: {getItem: () => null}, location: {href: '/chat'}, window: {location: {href: '/chat'}},
        document: {body: element(), querySelectorAll: () => [], addEventListener() {}, getElementById(id) {if (!elements.has(id)) elements.set(id, element()); return elements.get(id);}, createElement: element},
        fetch: async (url, options = {}) => {if (url === '/api/adviser') requests.push({url, payload: JSON.parse(options.body), headers: options.headers}); return {ok: true, json: async () => url === '/api/auth/me' ? {user: {name: 'Synthetic Student', email: 'synthetic@example.invalid'}} : url === '/api/auth/csrf' ? {csrf: 'node-test-only'} : url === '/api/progress' ? {report: null} : {reply: 'Offline advising reply'}};}
    });
    vm.runInContext(script, context);
    return {context, elements, requests};
}
(async () => {
    let f = fixture();
    assert.equal(vm.runInContext("openAgent('CS Learning & Tutoring')", f.context), false);
    assert.equal(f.context.window.location.href, '/agents/tutoring');
    assert.equal(f.requests.length, 0);
    f = fixture();
    vm.runInContext("ask('CS topic: binary search')", f.context);
    await new Promise(setImmediate);
    assert.equal(f.context.window.location.href, '/agents/tutoring');
    assert.equal(f.requests.length, 0);
    f = fixture();
    vm.runInContext("ask('Plan my courses')", f.context);
    await new Promise(setImmediate);
    assert.equal(f.requests.length, 1);
    assert.equal(f.requests[0].url, '/api/adviser');
    assert.equal(f.requests[0].headers['X-CSRF-Token'], 'node-test-only');
    assert.equal(f.requests[0].payload.question, 'You are the Academic Advising agent. Plan my courses');
    for (const label of ['Academic Advising', 'Career & Professional', 'Student Success & Support']) {
        f = fixture();
        assert.equal(vm.runInContext(`openAgent(${JSON.stringify(label)})`, f.context), undefined);
        assert.equal(f.context.window.location.href, '/chat');
        assert.equal(f.elements.get('agentTitle').textContent, label);
    }
    for (const agent of ['academic', 'career', 'success', 'tutoring']) {
        assert.ok(html.includes(`window.location.href='/agents/${agent}'`));
    }
    console.log('PASS: legacy Tutoring navigation without advising call; unchanged Academic payload; unchanged non-Tutoring helper state and four service cards');
})().catch(error => {console.error(error); process.exitCode = 1;});
