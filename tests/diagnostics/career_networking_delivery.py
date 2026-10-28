"""Networking-only repair freeze and parity verification."""
import ast,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'tests/diagnostics'
def sha(x):return hashlib.sha256(x).hexdigest()
def verify():
 m=json.loads((BASE/'career_networking_delivery_parity.json').read_text())
 for section in ('protected_files','prior_json'):
  for name,digest in m[section].items():assert sha((ROOT/name).read_bytes())==digest,name
 assert sha((ROOT/'agents/career/workflow/shared_evidence.py').read_bytes())==m['new_shared_sha256']
 assert sha((ROOT/'agents/career/workflow/deploy_dev.py').read_bytes())==m['deploy_sha256']
 raw=(ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md').read_bytes()
 assert sha(raw[:m['report_prefix_bytes']])==m['report_prefix_sha256']
 assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='beeb3a87ad2f8892dce9e30f376bd2768b65c239'
 return True
if __name__=='__main__':verify();print('Networking source freeze PASS')
