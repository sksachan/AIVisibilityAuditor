#!/usr/bin/env python3
"""Extract deterministic winning patterns from top external citation evidence.
Input normally comes from outputs/frontend_report_bundle.json or query_workbench JSON.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

def load(p):
    try: return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception: return {}

def qwork(obj):
    if isinstance(obj,dict):
        if isinstance(obj.get('query_workbench'),list): return obj['query_workbench']
        if isinstance(obj.get('frontend_report_bundle'),dict): return qwork(obj['frontend_report_bundle'])
    return []

def classify_pattern(c):
    st=c.get('source_type') or 'other'; txt=' '.join(str(c.get(k) or '') for k in ['snippet','title','domain']).lower()
    pats=[]
    if re.search(r'\d', txt): pats.append('numeric_or_dated_proof')
    if any(x in txt for x in ['compare','vs','best','ranking','cost','price']): pats.append('comparison_or_buyer_guidance')
    if any(x in txt for x in ['faq','how','guide','what','why']): pats.append('answer_first_guide_structure')
    if st in {'authority_body','partner_infrastructure'}: pats.append('authority_or_partner_validation')
    if st == 'competitor_owned': pats.append('competitor_model_specific_claim')
    if st == 'forum_social_video': pats.append('objection_or_lived_experience_signal')
    return pats or ['extractable_answer_wording']

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--input-json',default='outputs/frontend_report_bundle.json'); args=ap.parse_args()
    root=Path(args.project_root); obj=load(root/args.input_json) if not Path(args.input_json).is_absolute() else load(args.input_json)
    rows=[]
    for q in qwork(obj):
        for c in q.get('external_top3_benchmark') or []:
            for pat in classify_pattern(c):
                rows.append({'query_id':q.get('query_id'),'query':q.get('query'),'source_url':c.get('url'),'source_domain':c.get('domain'),'source_type':c.get('source_type'),'pattern_type':pat,'cms_relevance':'high' if pat not in {'authority_or_partner_validation','objection_or_lived_experience_signal'} else 'medium','pr_relevance':'high' if pat in {'authority_or_partner_validation','comparison_or_buyer_guidance','competitor_model_specific_claim'} else 'medium','evidence_basis':c.get('snippet') or c.get('title') or c.get('domain')})
    out={'pattern_count':len(rows),'patterns':rows}
    dest=root/'outputs/benchmark/page_benchmark_patterns.json'; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'ready','pattern_count':len(rows),'output':str(dest)},indent=2))
if __name__=='__main__': main()
