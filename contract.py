import math,re
from urllib.parse import urlsplit

def url(value):
 p=urlsplit(value)
 if p.scheme!='https' or not p.hostname or p.username or p.password:
  raise ValueError('HTTPS signed storage URL required')
 return value

def vector(v):
 if not isinstance(v,list) or len(v)!=3 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in v):
  raise ValueError('camera requires three finite coordinates in metres')
 return v

def validate(data):
 x=dict(data)
 q=x.get('quality','preview')
 if q not in ('preview','final'): raise ValueError('quality must be preview or final')
 # Approval and budgets MUST also be enforced by the trusted caller, not this flag.
 if q=='final' and x.get('approved') is not True: raise ValueError('final requires approval')
 x['model_url']=url(x.get('model_url',''))
 if not re.fullmatch('[0-9a-f]{64}',x.get('model_sha256','')): raise ValueError('sha256 required')
 outputs=x.get('output_urls',{})
 for name in ('png','blend','report'): url(outputs.get(name,''))
 fmt=x.get('model_format','glb')
 if fmt not in ('glb','blend'): raise ValueError('model_format must be glb or blend')
 x['model_format']=fmt
 camera=x.get('camera',{})
 if fmt=='glb':
  vector(camera.get('position')); vector(camera.get('target'))
  if camera['position']==camera['target']: raise ValueError('invalid camera')
  lens=camera.get('lens',24)
  if isinstance(lens,bool) or not isinstance(lens,(float,int)) or not 12<=lens<=100: raise ValueError('lens range 12..100mm')
 x['resolution']=x.get('resolution',[960,540] if q=='preview' else [1920,1080])
 if x['resolution'] not in ([960,540],[1920,1080],[3840,2160]): raise ValueError('unsupported resolution')
 if q=='preview' and x['resolution']!=[960,540]: raise ValueError('preview must be 960x540')
 x['samples']=32 if q=='preview' else 256
 return x
