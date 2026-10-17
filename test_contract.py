import unittest
from contract import validate
class ContractTests(unittest.TestCase):
 def test_valid_preview(self):
  x=validate({'model_url':'https://storage.example/a','model_sha256':'a'*64,'output_urls':{'png':'https://storage.example/b','blend':'https://storage.example/c','report':'https://storage.example/d'},'camera':{'position':[1,2,1.6],'target':[2,2,1.6]}})
  self.assertEqual(x['resolution'],[960,540])
 def test_reject_private_transfer(self):
  with self.assertRaises(ValueError): validate({'model_url':'http://127.0.0.1/a'})
 def test_final_requires_approval(self):
  with self.assertRaises(ValueError): validate({'quality':'final'})
 def test_camera_not_invented(self):
  with self.assertRaises(ValueError): validate({'model_url':'https://storage.example/a','model_sha256':'a'*64,'output_urls':{'png':'https://storage.example/b','blend':'https://storage.example/c','report':'https://storage.example/d'}})
class BlendContractTests(unittest.TestCase):
 def payload(self):
  return {'model_format':'blend','model_url':'https://storage.example/a','model_sha256':'a'*64,'output_urls':dict.fromkeys(('png','blend','report'),'https://storage.example/b')}
 def test_blend_preserves_camera(self):
  self.assertEqual(validate(self.payload())['model_format'],'blend')
 def test_unknown_format_rejected(self):
  x=self.payload();x['model_format']='python'
  with self.assertRaises(ValueError):validate(x)
 def test_blend_final_needs_approval(self):
  x=self.payload();x['quality']='final'
  with self.assertRaises(ValueError):validate(x)
if __name__=='__main__': unittest.main()
