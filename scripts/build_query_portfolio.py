#!/usr/bin/env python3
"""Build or normalise a query portfolio from manual JSON, synthetic DeepResearch output, or existing evidence."""
from __future__ import annotations
import argparse, json, re, hashlib
from pathlib import Path

def load(path):
    if not path: return {}
    try: return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception: return {}

def as_list(obj,*keys):
    if isinstance(obj,list): return obj
    if isinstance(obj,dict):
        for k in keys:
            v=obj.get(k)
            if isinstance(v,list): return v
            if isinstance(v,dict):
                x=as_list(v,*keys)
                if x: return x
    return []

def sid(q,i):
    raw=(q or str(i)).encode(); return 'q'+hashlib.sha1(raw).hexdigest()[:6]

def normalise(rows, brand, market, source):
    out=[]
    for i,row in enumerate(rows,1):
        if isinstance(row,str): row={'query':row}
        if not isinstance(row,dict): continue
        q=str(row.get('query') or row.get('question') or row.get('search_query') or '').strip()
        if not q: continue
        out.append({
            'query_id':str(row.get('query_id') or row.get('id') or f'q{i:03d}'),
            'query':q,
            'topic':row.get('topic') or row.get('brand_topic') or row.get('category') or 'Unclassified',
            'journey_stage':row.get('journey_stage') or row.get('journey_category') or row.get('stage') or 'Discovery',
            'intent':row.get('intent') or row.get('query_intent') or 'information_seeking',
            'priority':row.get('priority') or 'medium',
            'recommended_page_type':row.get('recommended_page_type') or row.get('page_type') or '',
            'reason_selected':row.get('reason_selected') or row.get('rationale') or '',
            'portfolio_source':source
        })
    return {'brand':brand,'market':market,'portfolio_source':source,'query_count':len(out),'queries':out}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root',default='.')
    ap.add_argument('--brand',default='')
    ap.add_argument('--market',default='')
    ap.add_argument('--mode',choices=['manual','synthetic','reuse'],default='reuse')
    ap.add_argument('--manual-json',default='')
    ap.add_argument('--deepresearch-json',default='')
    ap.add_argument('--existing-json',default='')
    ap.add_argument('--query-limit',type=int,default=0)
    args=ap.parse_args(); root=Path(args.project_root)
    obj=load(args.manual_json if args.mode=='manual' else args.deepresearch_json if args.mode=='synthetic' else args.existing_json)
    rows=as_list(obj,'queries','query_portfolio','items','rows')
    if args.query_limit: rows=rows[:args.query_limit]
    out=normalise(rows,args.brand,args.market,args.mode if args.mode!='synthetic' else 'synthetic_deepresearch')
    dest=root/'outputs/query_portfolio/query_portfolio.json'; dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'ready','query_count':len(out['queries']),'output':str(dest)},indent=2))
if __name__=='__main__': main()
