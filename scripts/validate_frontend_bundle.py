#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--bundle',default='outputs/frontend_report_bundle.json'); args=ap.parse_args()
    p=Path(args.bundle); obj=json.loads(p.read_text(encoding='utf-8'))
    errors=[]
    if obj.get('schema_version')!='query_workbench.v1': errors.append('schema_version must be query_workbench.v1')
    if not str(obj.get('contract_version','')).startswith('page_level_cms_grouped_pr.v'): errors.append('contract_version missing page_level_cms_grouped_pr')
    if not isinstance(obj.get('query_workbench'),list): errors.append('query_workbench must be list')
    if not isinstance(obj.get('page_level_cms_recommendations'),list): errors.append('page_level_cms_recommendations must be list')
    if not isinstance(obj.get('grouped_pr_opportunities'),list): errors.append('grouped_pr_opportunities must be list')
    status='failed' if errors else 'passed'
    print(json.dumps({'status':status,'errors':errors,'query_count':len(obj.get('query_workbench') or []),'cms_pages':len(obj.get('page_level_cms_recommendations') or []),'pr_groups':len(obj.get('grouped_pr_opportunities') or [])},indent=2))
    if errors: sys.exit(1)
if __name__=='__main__': main()
