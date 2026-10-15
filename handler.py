"""RunPod queue handler. Transfer URLs are capabilities: never log input."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import urlsplit
import requests,runpod
from contract import validate

MAX_BYTES=512*1024*1024

def transfer_url(value):
 p=urlsplit(value)
 allowed=set(filter(None,os.environ.get('STORAGE_ALLOWED_HOSTS','').split(',')))
 if p.scheme!='https' or p.hostname not in allowed or p.port not in (None,443) or p.username or p.password:
  raise ValueError('Storage host not explicitly authorized')
 return value

def handler(job):
 x=validate(job['input'])
 transfer_url(x['model_url'])
 for u in x['output_urls'].values(): transfer_url(u)
 with tempfile.TemporaryDirectory(prefix='render-') as directory:
  p=Path(directory); digest=hashlib.sha256(); size=0
  with requests.get(x['model_url'],stream=True,timeout=(15,120),allow_redirects=False) as r:
   if r.status_code!=200: raise RuntimeError('Model download failed')
   with (p/'model.glb').open('wb') as f:
    for chunk in r.iter_content(1024*1024):
     size+=len(chunk)
     if size>MAX_BYTES: raise ValueError('Model exceeds 512MiB')
     digest.update(chunk); f.write(chunk)
  if digest.hexdigest()!=x['model_sha256']: raise ValueError('Model checksum mismatch')
  # Signed upload/download URLs and other caller metadata never enter the blend file.
  params={k:x[k] for k in ('camera','resolution','samples')}
  (p/'job.json').write_text(json.dumps(params))
  runpod.serverless.progress_update(job,{'stage':'rendering'})
  with (p/'blender.log').open('w') as log:
   result=subprocess.run(['/opt/blender/blender','-b','--disable-autoexec','--python-exit-code','1','--python','/worker/render.py','--',str(p/'job.json')],stdout=log,stderr=log,timeout=1740)
  if result.returncode: raise RuntimeError('Blender GPU render failed; no CPU fallback')
  report=json.loads((p/'report.json').read_text())
  runpod.serverless.progress_update(job,{'stage':'uploading'})
  for key,name,typ in [('png','render.png','image/png'),('blend','project.blend','application/octet-stream'),('report','report.json','application/json')]:
   with (p/name).open('rb') as f:
    response=requests.put(x['output_urls'][key],data=f,headers={'Content-Type':typ},timeout=(15,180),allow_redirects=False)
   if response.status_code not in (200,201,204): raise RuntimeError('Private storage upload failed: '+key)
  return {'uploaded':['png','blend','report'],'report':report}

if __name__=='__main__': runpod.serverless.start({'handler':handler})
