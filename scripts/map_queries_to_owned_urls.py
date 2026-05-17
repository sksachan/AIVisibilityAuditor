#!/usr/bin/env python3
"""Map each query to top-N owned URLs using query portfolio and sitemap inventory.
This is a lightweight CLI wrapper; the canonical builder performs final mapping too.
"""
from __future__ import annotations
import argparse,json,re,hashlib
from pathlib import Path

def load(p):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception: return {}

def rows(obj,*keys):
    if isinstance(obj,list): return obj
    if isinstance(obj,dict):
        for k in keys:
            v=obj.get(k)
            if isinstance(v,list): return v
            if isinstance(v,dict):
                r=rows(v,*keys)
                if r: return r
    return []

def toks(s): return {w for w in re.findall(r'[a-z0-9]+', str(s or '').lower()) if len(w)>2}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--query-portfolio',default='outputs/query_portfolio/query_portfolio.json'); ap.add_argument('--sitemap-inventory',default='outputs/sitemap/sitemap_inventory.json'); ap.add_argument('--max-owned',type=int,default=3); args=ap.parse_args()
    root=Path(args.project_root); qobj=load(root/args.query_portfolio); pobj=load(root/args.sitemap_inventory)
    qs=rows(qobj,'queries','query_portfolio','items'); pages=rows(pobj,'urls','pages','items')
    out=[]
    for i,q in enumerate(qs,1):
        qd=q if isinstance(q,dict) else {'query':str(q)}; query=qd.get('query') or ''; qt=toks(query+' '+str(qd.get('topic') or '')+' '+str(qd.get('recommended_page_type') or ''))
        scored=[]
        for p in pages:
            pd=p if isinstance(p,dict) else {'url':str(p)}
            blob=' '.join(str(pd.get(k) or '') for k in ['url','title','description','page_type']).lower(); pt=toks(blob)
            score=len(qt & pt)*20 + (15 if str(qd.get('recommended_page_type') or '').lower() in blob else 0)
            if score>0: scored.append((score,pd))
        scored.sort(key=lambda x:x[0], reverse=True)
        out.append({'query_id':qd.get('query_id') or f'q{i:03d}','query':query,'mapped_owned_urls':[{'rank':r,'url':p.get('url'),'title':p.get('title',''),'page_type':p.get('page_type',''),'mapping_score':s,'mapping_reason':'Matched by query/topic/page-type terms from sitemap inventory.'} for r,(s,p) in enumerate(scored[:args.max_owned],1)]})
    dest=root/'outputs/mapping/query_owned_url_mapping.json'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps({'mappings':out},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'ready','query_count':len(out),'output':str(dest)},indent=2))
if __name__=='__main__': main()
