"""Run only unattempted minimum RC2 canaries; stop on any capacity incident."""
import json
from career_networking_rc2_remote import BASE,run,plan
if __name__=='__main__':
 for name in ('rc_networking_current','rc_career_current','rc_trust_current'):
  d=json.loads((BASE/'career_networking_rc2_remote.json').read_text(encoding='utf8'))
  assert not any(r['capacity_failure'] for r in d['runs']),'429: stop this batch'
  assert all(r['status']=='completed' and r.get('route_match') for r in d['runs']),'Prior check did not pass'
  run(next(c for c in plan() if c['id']==name))
  d=json.loads((BASE/'career_networking_rc2_remote.json').read_text(encoding='utf8'))
  if d['runs'][-1]['capacity_failure'] or d['runs'][-1]['status']!='completed':break
