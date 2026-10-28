"""Offline syntax, instruction, model, source and privacy parity."""
import ast,json,re,sys
from pathlib import Path
from career_networking_delivery import BASE,ROOT,sha,verify
from career_wave5 import nodes,instruction_value
sys.path.insert(0,str(ROOT))

def main():
 verify();tree=ast.parse((ROOT/'agents/career/workflow/agent.py').read_bytes())
 expected=json.loads((BASE/'career_wave65_validation.json').read_text())['components'];components={}
 for name,n in nodes(tree).items():
  kw={k.arg:k.value for k in n.value.keywords};h=sha(instruction_value(kw['instruction']).encode());model=ast.literal_eval(next(k.value for k in kw['model'].keywords if k.arg=='model'))
  assert h==expected[name]['after_sha256'],name
  assert model==expected[name]['model'],name
  components[name]=dict(instruction_sha256=h,model=model,unchanged=True)
 assert len(components)==30
 for p in [*(ROOT/'agents/career/workflow').glob('*.py'),*BASE.glob('career_networking*.py'),BASE/'test_career_networking_delivery.py']:
  ast.parse(p.read_bytes(),filename=str(p))
 from agents.career.workflow.agent import root_agent
 from agents.career.workflow.main import app
 assert len(root_agent.sub_agents)==9
 files=list(BASE.glob('career_networking*.json'))
 private=[]
 def scan(x,path):
  if isinstance(x,dict):
   for k,v in x.items():
    if k.lower() in {'user_id','session_id','userid','sessionid','access_token','refresh_token','private_key','authorization'}:private.append(path+':'+k)
    scan(v,path)
  elif isinstance(x,list):
   for v in x:scan(v,path)
 for p in files:scan(json.loads(p.read_text(encoding='utf8')),p.name)
 assert not private,private
 for p in [ROOT/'agents/career/workflow/shared_evidence.py',*BASE.glob('career_networking*.py'),BASE/'test_career_networking_delivery.py']:
  assert not re.search(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|AIza[0-9A-Za-z_-]{30,}',p.read_text(encoding='utf8')),p
 result=dict(components=components,instruction_hashes_unchanged=30,models_unchanged=True,tools_callbacks_relationships_unchanged=True,root_specialists=9,app_loaded=True,source_freeze=True,privacy_scan_passed=True,only_product_change='shared_evidence.py: Networking-only delivery support adjudication/rendering')
 (BASE/'career_networking_delivery_validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Syntax/import, 30 instruction/model hashes, graph/tool/source parity and diagnostic privacy PASS')
if __name__=='__main__':main()
