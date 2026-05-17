#!/usr/bin/env python3
"""Normalise SerpAPI / Google AI Mode citation evidence into a query-keyed citation file.
Does not call SerpAPI; use 02_collect_google_ai_mode.py for live collection.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from urllib.parse import urlparse

def load(p):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception: return {}

def domain(u):
    try:
        d=urlparse(u or '').netloc.lower(); return d[4:] if d.startswith('www.') else d
    except Exception: return ''

def source_type(u):
    d=domain(u)
    if 'nissan' in d: return 'owned_or_nissan_ecosystem'
    if any(x in d for x in ['toyota','honda','mitsubishi','mazda','subaru','suzuki']): return 'competitor_owned'
    if any(x in d for x in ['reddit','youtube','facebook','instagram','twitter','x.com']): return 'forum_social_video'
    if any(x in d for x in ['go.jp','mlit','meti']): return 'authority_body'
    if any(x in d for x in ['nikkei','asahi','car','auto','review']): return 'publisher_review'
    return 'other'

def walk(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in {'citations','references','sources','top_citations','answer_supporting_references'} and isinstance(v,list):
                yield v
            yield from walk(v)
    elif isinstance(obj,list):
        for x in obj: yield from walk(x)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--input-json',required=True); ap.add_argument('--max-external',type=int,default=3); args=ap.parse_args()
    obj=load(args.input_json); rows=[]
    qrows=obj.get('queries') if isinstance(obj,dict) and isinstance(obj.get('queries'),list) else obj if isinstance(obj,list) else []
    for i,row in enumerate(qrows,1):
        if not isinstance(row,dict): continue
        qid=str(row.get('query_id') or row.get('id') or f'q{i:03d}'); query=row.get('query') or row.get('search_query') or ''
        cites=[]
        for lst in walk(row):
            for j,c in enumerate(lst,1):
                if not isinstance(c,dict): continue
                u=c.get('url') or c.get('link') or c.get('href') or c.get('source_url')
                if not u: continue
                cites.append({'query_id':qid,'query':query,'rank':len(cites)+1,'url':u,'domain':c.get('domain') or domain(u),'title':c.get('title') or c.get('source_name') or domain(u),'snippet':c.get('snippet') or c.get('text') or c.get('summary') or '', 'source_type':c.get('source_type') or source_type(u)})
        seen=set()
        for c in cites:
            if c['url'] in seen: continue
            seen.add(c['url']); rows.append(c)
    out={'citation_count':len(rows),'citations':rows}
    dest=Path(args.project_root)/'outputs/ai_citations/ai_citations.json'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'ready','citation_count':len(rows),'output':str(dest)},indent=2))
if __name__=='__main__': main()
