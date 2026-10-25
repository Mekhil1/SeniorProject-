"""Read back only this RC2 staging archive; never load its pickle."""
import io,json,tarfile,hashlib
from pathlib import Path
from google.cloud import storage
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
 d=json.loads((BASE/'career_networking_rc2_deployment.json').read_text());assert d['status']=='created'
 bucket=storage.Client(project='cosc-490').bucket(d['staging_bucket'][5:]);prefix=d['staging_prefix']
 archive=bucket.blob(prefix+'/dependencies.tar.gz').download_as_bytes()
 runtime=bucket.blob(prefix+'/requirements.txt').download_as_bytes().decode()
 with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as t:
  names=t.getnames();parity={}
  for name in ('agent.py','evidence.py','shared_evidence.py','main.py','requirements.txt'):
   p='agents/career/workflow/'+name;a=t.extractfile(p).read();b=(ROOT/p).read_bytes()
   parity[p]=dict(local_sha256=sha(b),staged_sha256=sha(a),match=a==b);assert a==b
 out=dict(prefix=prefix,archive_members=names,byte_parity=parity,runtime_requirements=runtime,pickle_downloaded=False)
 (BASE/'career_networking_rc2_staged.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Staged byte parity PASS: all five workflow source/dependency files')
if __name__=='__main__':main()
