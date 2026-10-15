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
if __name__=='__main__': unittest.main()
