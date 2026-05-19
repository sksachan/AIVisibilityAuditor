from __future__ import annotations

from typing import Any


def as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [v.strip() for v in value.replace('|', ',').split(',') if v.strip()]
    return []


def first_number(*values: Any) -> int:
    for v in values:
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str) and v.strip().isdigit():
            return int(v.strip())
    return 0


def page_technical_signals(page: dict[str, Any], manifest: dict[str, Any] | None = None, score_result: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or {}
    score_result = score_result or {}
    meta = page.get('metadata') if isinstance(page.get('metadata'), dict) else {}
    manifest_meta = manifest.get('metadata') if isinstance(manifest.get('metadata'), dict) else {}
    geo = page.get('geo_signals') if isinstance(page.get('geo_signals'), dict) else {}
    score_standards = score_result.get('standards_signals') if isinstance(score_result.get('standards_signals'), dict) else {}
    structured = page.get('structured_data') if isinstance(page.get('structured_data'), dict) else {}
    tech = page.get('technical_signals') if isinstance(page.get('technical_signals'), dict) else {}
    schema_types: list[str] = []
    for value in (page.get('schema_types_detected'), page.get('schema_types'), meta.get('schema_types'), manifest_meta.get('schema_types'), score_result.get('schema_types'), structured.get('schema_types'), tech.get('schema_types')):
        schema_types.extend(as_list(value))
    schema_types = list(dict.fromkeys(schema_types))
    block_count = first_number(page.get('json_ld_block_count'), page.get('schema_block_count'), meta.get('schema_block_count'), manifest_meta.get('schema_block_count'), structured.get('json_ld_block_count'), tech.get('json_ld_block_count'))
    json_ld_present = any(v is True for v in (page.get('json_ld_present'), page.get('schema_json_ld'), meta.get('json_ld_present'), manifest_meta.get('json_ld_present'), geo.get('schema_json_ld'), structured.get('json_ld_present'), tech.get('json_ld_present'), score_standards.get('json_ld_observed'))) or block_count > 0 or bool(schema_types)
    canonical = page.get('canonical_url') or page.get('canonical') or meta.get('canonical') or manifest_meta.get('canonical') or tech.get('canonical_url') or ''
    meta_description = page.get('meta_description') or page.get('description') or meta.get('description') or manifest_meta.get('description') or ''
    robots_meta = page.get('robots_meta') or meta.get('robots') or manifest_meta.get('robots') or ''
    return {
        'json_ld_present': bool(json_ld_present),
        'json_ld_block_count': int(block_count),
        'schema_types_detected': schema_types,
        'schema_types': schema_types,
        'canonical_present': bool(canonical),
        'canonical_url': canonical,
        'meta_description_present': bool(meta_description),
        'meta_description': meta_description,
        'robots_meta': robots_meta,
    }


def enrich_with_technical_signals(obj: dict[str, Any], page: dict[str, Any], manifest: dict[str, Any] | None = None, score_result: dict[str, Any] | None = None) -> dict[str, Any]:
    signals = page_technical_signals(page, manifest, score_result)
    obj.update({
        'json_ld_present': signals['json_ld_present'],
        'json_ld_block_count': signals['json_ld_block_count'],
        'schema_types_detected': signals['schema_types_detected'],
        'schema_types': signals['schema_types'],
        'canonical_present': signals['canonical_present'],
        'meta_description_present': signals['meta_description_present'],
    })
    obj['technical_signals'] = {**(obj.get('technical_signals') if isinstance(obj.get('technical_signals'), dict) else {}), **signals}
    obj['structured_data'] = {**(obj.get('structured_data') if isinstance(obj.get('structured_data'), dict) else {}), 'json_ld_present': signals['json_ld_present'], 'json_ld_block_count': signals['json_ld_block_count'], 'schema_types': signals['schema_types']}
    return obj


def site_standards_status(site_standards: dict[str, Any]) -> dict[str, Any]:
    signals = site_standards.get('signals') if isinstance(site_standards.get('signals'), dict) else {}
    robots_obj = site_standards.get('robots_txt') if isinstance(site_standards.get('robots_txt'), dict) else {}
    llms_obj = site_standards.get('llms_txt') if isinstance(site_standards.get('llms_txt'), dict) else {}
    robots_status = site_standards.get('robots_txt_status') or ('present' if signals.get('robots_available') or robots_obj.get('status') in {'available', 'present'} else 'missing')
    llms_status = site_standards.get('llms_txt_status') or ('present' if signals.get('llms_txt_available') or llms_obj.get('status') in {'available', 'present'} else 'missing')
    return {
        **site_standards,
        'robots_txt_status': robots_status,
        'robots_txt_url': site_standards.get('robots_txt_url') or robots_obj.get('resolved_url') or robots_obj.get('url') or '',
        'llms_txt_status': llms_status,
        'llms_txt_url': site_standards.get('llms_txt_url') or llms_obj.get('resolved_url') or llms_obj.get('url') or '',
    }
