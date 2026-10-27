const $ = (s) => document.querySelector(s);
const escapeHtml = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function slug(text) { return text.toLowerCase().trim().replace(/<[^>]*>/g,'').replace(/[^\p{L}\p{N} _-]/gu,'').replace(/\s/g,'-'); }
function anchorsOf(text) {
  const result = new Set(), counts = new Map(); let fenced = false;
  for (const line of text.split(/\r?\n/)) {
    if (/^\s*(```|~~~)/.test(line)) { fenced = !fenced; continue; }
    if (fenced) continue;
    const m = line.match(/^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$/);
    if (!m) continue;
    const base = slug(m[1]), n = counts.get(base) || 0;
    result.add(n ? `${base}-${n}` : base); counts.set(base,n+1);
  }
  return result;
}
$('#run').onclick = async () => {
 const files = [...$('#folder').files], md = files.filter(f => /\.md$/i.test(f.name));
 if (!md.length) { $('#result').innerHTML='<p class="bad">Choose a folder containing .md files.</p>'; return; }
 if (md.length > 500) { $('#result').innerHTML='<p class="bad">Limit is 500 Markdown files.</p>'; return; }
 if (md.reduce((n,f)=>n+f.size,0) > 50_000_000) { $('#result').innerHTML='<p class="bad">Selected Markdown files exceed 50 MB total.</p>'; return; }
 try {
  const items = await Promise.all(md.map(async f => ({
   path: (f.webkitRelativePath || f.name).split('/').slice(1).join('/') || f.name,
   text: await f.text()
  })));
  const byPath = new Map(items.map(x => [x.path,x.text])), issues=[];
  for (const file of items) {
   let fenced=false; const lines=file.text.split(/\r?\n/);
   for(let i=0;i<lines.length;i++) {
    const line=lines[i]; if(/^\s*(```|~~~)/.test(line)){fenced=!fenced;continue;} if(fenced)continue;
    const links=/!?\[[^\]]*\]\(([^)]+)\)/g; let m;
    while((m=links.exec(line))) {
      const raw=m[1].trim().replace(/^<|>$/g,'').split(/\s+/)[0];
      if(/^(?:[a-z][a-z0-9+.-]*:|#|\/)/i.test(raw)) continue;
      const hash=raw.indexOf('#'), pathname=hash<0?raw:raw.slice(0,hash), fragment=hash<0?'':raw.slice(hash+1);
      let decoded; try{decoded=decodeURIComponent(pathname);}catch{decoded=pathname;}
      let dest=file.path; if(pathname){try{dest=decodeURIComponent(new URL(decoded,'https://local.invalid/'+encodeURI(file.path)).pathname.slice(1));}catch{issues.push(`${file.path}:${i+1} — invalid link path ${raw}`);continue;}}
      if(pathname && !byPath.has(dest)){issues.push(`${file.path}:${i+1} — missing file ${dest}`);continue;}
      if(fragment){let frag;try{frag=decodeURIComponent(fragment).toLowerCase();}catch{frag=fragment.toLowerCase();}
       const target=byPath.get(dest)||file.text;
       if(!anchorsOf(target).has(frag)) issues.push(`${file.path}:${i+1} — missing heading #${fragment} in ${dest}`);
      }
    }
   }
  }
  $('#result').innerHTML=`<div class="stats"><div><b>${items.length}</b><span class="muted">Markdown files</span></div><div><b>${issues.length}</b><span class="muted">broken links</span></div></div><h2 style="margin-top:20px">${issues.length?'Needs a look':'No broken relative links found'}</h2>${issues.length?'<div class="list">'+issues.map(x=>`<div class="item">${escapeHtml(x)}</div>`).join('')+'</div>':'<p class="ok">The selected Markdown files link only to files and headings that were found.</p>'}`;
 } catch(e) { $('#result').innerHTML=`<p class="bad">Could not read the selected folder: ${escapeHtml(e.message)}</p>`; }
};
