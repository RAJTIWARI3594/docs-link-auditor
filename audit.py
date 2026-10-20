import argparse,json,re,sys,unicodedata
from pathlib import Path
from urllib.parse import unquote,urlsplit
LINK=re.compile(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)')
def slug(s):
 s=re.sub(r'[`*_~]','',s).lower().strip();s=''.join(c for c in s if c.isalnum() or c in ' -_');return re.sub(r'\s+','-',s)
def visible(text):
 out=[];fence=None
 for line in text.splitlines():
  m=re.match(r'^\s*(`{3,}|~{3,})',line)
  if m:
   ch=m[1][0];length=len(m[1])
   if fence and ch==fence[0] and length>=fence[1]:fence=None
   elif fence is None:fence=(ch,length)
   out.append('');continue
  out.append(line if fence is None else '')
 return out

def anchors(path):
 seen={};out=set()
 for line in visible(path.read_text(encoding='utf-8')):
  m=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
  if m:
   a=slug(m[1]);n=seen.get(a,0);out.add(a if n==0 else f'{a}-{n}');seen[a]=n+1
 return out

def audit(root):
 root=Path(root).resolve()
 if not root.is_dir():raise ValueError('Documentation root must be a directory')
 files=sorted(root.rglob('*.md'));issues=[];checked=0;skipped=0;cache={}
 for source in files:
  if not source.resolve().is_relative_to(root):raise ValueError('Markdown symlink escapes root')
  if source.stat().st_size>1_000_000:raise ValueError('Markdown exceeds 1 MB')
  for lineno,line in enumerate(visible(source.read_text(encoding='utf-8')),1):
   for m in LINK.finditer(re.sub(r'`[^`]*`','',line)):
    raw=m[1];url=urlsplit(raw)
    if url.scheme in ('http','https','mailto','tel') or url.netloc:skipped+=1;continue
    checked+=1;target=(source.parent/unquote(url.path)).resolve() if url.path else source.resolve();reason=None
    if url.scheme:reason='unsupported scheme'
    elif not target.is_relative_to(root):reason='path escapes root'
    elif not target.exists():reason='missing file'
    elif target.is_dir():reason='directory links require an explicit file'
    elif url.fragment and target.suffix.lower()=='.md':
     if target not in cache:
      if target.stat().st_size>1_000_000:raise ValueError('Markdown target exceeds 1 MB')
      cache[target]=anchors(target)
     if unquote(url.fragment) not in cache[target]:reason='missing heading anchor'
    if reason:issues.append({'file':str(source.relative_to(root)),'line':lineno,'target':raw,'reason':reason})
 return {'files':len(files),'checked_links':checked,'skipped_external':skipped,'issues':issues}

def main():
 ap=argparse.ArgumentParser(description='Audit bounded local Markdown links');ap.add_argument('root');ap.add_argument('--json');a=ap.parse_args()
 try:
  if a.json and Path(a.json).exists():raise ValueError('Report output already exists')
  result=audit(a.root);s=json.dumps(result,ensure_ascii=False,indent=2)
  if a.json:
   with open(a.json,'x',encoding='utf-8') as f:f.write(s+'\n')
  print(s);return int(bool(result['issues']))
 except (ValueError,OSError,UnicodeError) as e:print(f'Error: {e}',file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
