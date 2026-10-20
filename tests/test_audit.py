import unittest,tempfile
from pathlib import Path
from audit import audit,anchors,slug
class Tests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
 def write(self,n,t):p=self.root/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(t);return p
 def test_clean(self):self.write('a.md','# A\n[ok](b.md#hi)');self.write('b.md','# Hi');self.assertEqual(audit(self.root)['issues'],[])
 def test_missing(self):self.write('a.md','[x](b.md)');self.assertEqual(audit(self.root)['issues'][0]['reason'],'missing file')
 def test_anchor(self):self.write('a.md','# A\n[x](#no)');self.assertEqual(len(audit(self.root)['issues']),1)
 def test_repeated_heading(self):p=self.write('a.md','# A\n# A\n');self.assertEqual(anchors(p),{'a','a-1'})
 def test_escape(self):self.write('a.md','[x](../../outside.md)');self.assertEqual(audit(self.root)['issues'][0]['reason'],'path escapes root')
 def test_external(self):self.write('a.md','[x](https://example.org)');self.assertEqual(audit(self.root)['skipped_external'],1)
 def test_code(self):self.write('a.md','```md\n[x](none)\n```');self.assertEqual(audit(self.root)['checked_links'],0)
 def test_image(self):self.write('a.md','![alt](none.png)');self.assertEqual(len(audit(self.root)['issues']),1)
 def test_encoded(self):self.write('a.md','[x](my%20file.md#hi)');self.write('my file.md','# Hi');self.assertEqual(audit(self.root)['issues'],[])
 def test_directory(self):self.write('a.md','[x](sub)');(self.root/'sub').mkdir();self.assertEqual(len(audit(self.root)['issues']),1)
 def test_unicode(self):self.assertEqual(slug('Hello *World*!'),'hello-world')
 def test_symlink(self):
  self.write('a.md','[x](escape)');(self.root/'escape').symlink_to('/etc/passwd');self.assertEqual(audit(self.root)['issues'][0]['reason'],'path escapes root')
 def test_line_numbers(self):
  self.write('a.md','```md\n[ignored](none)\n```\n[bad](none)')
  self.assertEqual(audit(self.root)['issues'][0]['line'],4)
 def test_inline_code(self):self.write('a.md','Use `[x](missing)` here.');self.assertEqual(audit(self.root)['checked_links'],0)
if __name__=='__main__':unittest.main()
