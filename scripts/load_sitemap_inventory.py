#!/usr/bin/env python3
"""Load owned URL inventory from sitemap XML, site-standards output, or direct URL list.

Output: outputs/sitemap/sitemap_inventory.json
"""
from __future__ import annotations
import argparse, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
import requests


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def load_json(path: str):
    if not path: return {}
    p=Path(path)
    if not p.exists(): return {}
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return {}


def page_type(url: str, title: str = "") -> str:
    blob=(url+' '+title).lower()
    if any(x in blob for x in ['charge','charging','battery','range','ev','leaf','ariya','sakura']): return 'ev_charging_range'
    if any(x in blob for x in ['warranty','support','faq','service','maintenance']): return 'support_warranty_faq'
    if any(x in blob for x in ['finance','lease','loan','price','payment','insurance']): return 'finance_cost'
    if any(x in blob for x in ['safety','assist','adas','crash','360']): return 'safety_adas'
    if any(x in blob for x in ['e-power','epower','hybrid','powertrain']): return 'powertrain'
    if any(x in blob for x in ['serena','x-trail','elgrand','family','seat','luggage']): return 'family_practicality'
    if any(x in blob for x in ['news','press','release']): return 'news_press'
    return 'product_or_content'


def parse_sitemap_xml(xml_text: str) -> list[dict]:
    urls=[]
    root=ET.fromstring(xml_text.encode('utf-8'))
    ns=''
    if root.tag.startswith('{'):
        ns=root.tag.split('}')[0]+'}'
    # sitemap index
    for sm in root.findall(f'.//{ns}sitemap'):
        loc=sm.findtext(f'{ns}loc')
        lastmod=sm.findtext(f'{ns}lastmod')
        if loc: urls.append({'sitemap_url':text(loc),'lastmod':text(lastmod),'record_type':'sitemap'})
    for u in root.findall(f'.//{ns}url'):
        loc=u.findtext(f'{ns}loc')
        lastmod=u.findtext(f'{ns}lastmod')
        if loc:
            urls.append({'url':text(loc),'lastmod':text(lastmod),'record_type':'url','page_type':page_type(text(loc))})
    return urls


def fetch_text(url: str, timeout: int = 20) -> str:
    r=requests.get(url, timeout=timeout, headers={'User-Agent':'AIVisibilityAuditor/phase2'})
    r.raise_for_status()
    return r.text


def extract_from_site_standards(obj) -> list[dict]:
    if isinstance(obj, list): rows=obj
    elif isinstance(obj, dict):
        rows=obj.get('urls') or obj.get('pages') or obj.get('sitemap_urls') or obj.get('site_inventory') or obj.get('items') or []
    else: rows=[]
    out=[]
    for row in rows:
        if isinstance(row, str): row={'url':row}
        if not isinstance(row, dict): continue
        u=text(row.get('url') or row.get('loc') or row.get('canonical_url') or row.get('href'))
        if not u: continue
        out.append({
            'url':u,
            'title':text(row.get('title') or row.get('page_title')),
            'description':text(row.get('description') or row.get('meta_description')),
            'lastmod':text(row.get('lastmod') or row.get('last_modified')),
            'page_type':row.get('page_type') or page_type(u, text(row.get('title'))),
            'source':'site_standards_output'
        })
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--domain', default='')
    ap.add_argument('--sitemap-url', default='')
    ap.add_argument('--sitemap-file', default='')
    ap.add_argument('--site-standards-json', default='')
    ap.add_argument('--max-urls', type=int, default=5000)
    args=ap.parse_args()
    root=Path(args.project_root)
    records=[]
    ss=load_json(args.site_standards_json)
    if ss:
        records.extend(extract_from_site_standards(ss))
    xml_text=''
    if args.sitemap_file and Path(args.sitemap_file).exists(): xml_text=Path(args.sitemap_file).read_text(encoding='utf-8', errors='ignore')
    elif args.sitemap_url: xml_text=fetch_text(args.sitemap_url)
    if xml_text:
        parsed=parse_sitemap_xml(xml_text)
        # If sitemap index, fetch child sitemaps but cap quickly.
        child=[x['sitemap_url'] for x in parsed if x.get('record_type')=='sitemap'][:50]
        records.extend([x for x in parsed if x.get('record_type')=='url'])
        for sm in child:
            try:
                records.extend([x for x in parse_sitemap_xml(fetch_text(sm)) if x.get('record_type')=='url'])
            except Exception as e:
                print(f'WARN: failed child sitemap {sm}: {e}', file=sys.stderr)
    seen=set(); clean=[]
    dom=urlparse(args.domain).netloc.lower().replace('www.','') if args.domain else ''
    for r in records:
        u=text(r.get('url'))
        if not u or u in seen: continue
        if dom and dom not in urlparse(u).netloc.lower().replace('www.',''): continue
        seen.add(u); r.setdefault('page_type', page_type(u, r.get('title',''))); r.setdefault('source','sitemap'); clean.append(r)
        if len(clean)>=args.max_urls: break
    out={'domain':args.domain,'url_count':len(clean),'urls':clean}
    dest=root/'outputs/sitemap/sitemap_inventory.json'; dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status':'ready','url_count':len(clean),'output':str(dest)}, indent=2))
if __name__=='__main__': main()
