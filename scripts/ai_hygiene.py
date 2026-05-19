from __future__ import annotations

from collections import Counter
from typing import Any


NOT_CHECKED_SUMMARY = (
    "AI discoverability hygiene was not fully checked. Robots.txt, LLMs.txt, "
    "or JSON-LD crawl signals are missing from this evidence run."
)


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _first(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _number(value: Any, default: float = 0) -> float:
    try:
        if isinstance(value, bool):
            return default
        if isinstance(value, (int, float)):
            return value
        return float(str(value).replace(",", ""))
    except Exception:
        return default


def _status(value: Any, attempted: bool = False) -> str:
    text = str(value or "").strip().lower().replace("_", " ").replace("-", " ")
    if text in {"available", "present", "found", "ok", "success", "successful", "fetched", "200"}:
        return "available"
    if text in {"missing", "not found", "404", "empty", "error", "failed", "unavailable", "absent", "not available"}:
        return "not found"
    if text in {"not checked", "not supplied", "unchecked", "unknown", "skipped", "not attempted"}:
        return "not checked"
    return "not found" if attempted else "not checked"


def _boolish(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "present", "available", "found"}:
        return True
    if text in {"0", "false", "no", "n", "missing", "absent", "not found"}:
        return False
    return None


def _priority(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if text in {"high", "medium", "low"} else "high"


def _hygiene_candidates(source: Any, _seen: set[int] | None = None):
    _seen = _seen or set()
    if id(source) in _seen:
        return
    _seen.add(id(source))
    source = _as_dict(source)
    if not source:
        return
    containers = [
        source,
        _as_dict(source.get("executive")),
        _as_dict(source.get("evidence_collection")),
        _as_dict(source.get("site_readiness")),
        _as_dict(source.get("site_standards")),
        _as_dict(source.get("metadata")),
    ]
    for container in containers:
        for key in ("ai_discoverability_hygiene", "site_ai_hygiene", "ai_hygiene"):
            value = _as_dict(container.get(key))
            if value:
                yield value
    for value in source.values():
        if isinstance(value, dict):
            yield from _hygiene_candidates(value, _seen)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield from _hygiene_candidates(item, _seen)


def _canonical_from_existing(raw: dict) -> dict:
    robots = _as_dict(_first(raw.get("robots_txt"), raw.get("robotsTxt"), raw.get("robots")))
    llms = _as_dict(_first(raw.get("llms_txt"), raw.get("llmsTxt"), raw.get("llms")))
    structured = _as_dict(_first(
        raw.get("structured_data"),
        raw.get("structuredData"),
        raw.get("schema_coverage"),
        raw.get("json_ld_schema_coverage"),
    ))

    robots_url = _first(robots.get("url"), robots.get("robots_url"), robots.get("robotsUrl"), robots.get("resolved_url"))
    llms_url = _first(llms.get("url"), llms.get("llms_url"), llms.get("llmsUrl"), llms.get("resolved_url"))
    sitemap_count = _first(robots.get("sitemap_entries_count"), robots.get("sitemapEntriesCount"), robots.get("sitemap_count"))
    llms_chars = _first(llms.get("chars"), llms.get("character_count"), llms.get("charCount"))
    schema_types = _as_list(_first(
        structured.get("schema_types_detected"),
        structured.get("schemaTypesDetected"),
        structured.get("schema_types"),
        structured.get("schemaTypes"),
    ))
    missing = _as_list(_first(
        structured.get("pages_missing_json_ld"),
        structured.get("pagesMissingJsonLd"),
        structured.get("missing_pages"),
        structured.get("pages_missing_schema"),
    ))

    canonical = {
        "priority": _priority(_first(raw.get("priority"), raw.get("severity"), "high")),
        "summary": str(_first(raw.get("summary"), raw.get("notes"), raw.get("message"), NOT_CHECKED_SUMMARY)),
        "robots_txt": {"status": _status(_first(robots.get("status"), robots.get("state"), robots.get("result")), bool(robots))},
        "llms_txt": {"status": _status(_first(llms.get("status"), llms.get("state"), llms.get("result")), bool(llms))},
        "structured_data": {
            "owned_pages_total": int(_number(_first(structured.get("owned_pages_total"), structured.get("ownedPagesTotal"), structured.get("total_pages"), structured.get("totalPages")), 0)),
            "pages_with_schema": int(_number(_first(structured.get("pages_with_schema"), structured.get("pagesWithSchema"), structured.get("pages_with_structured_data")), 0)),
            "pages_with_json_ld": int(_number(_first(structured.get("pages_with_json_ld"), structured.get("pagesWithJsonLd"), structured.get("json_ld_pages")), 0)),
            "coverage_pct": round(_number(_first(structured.get("coverage_pct"), structured.get("coveragePct"), structured.get("coverage_percent"), structured.get("coveragePercent")), 0), 1),
        },
    }
    if robots_url:
        canonical["robots_txt"]["url"] = str(robots_url)
    if sitemap_count is not None:
        canonical["robots_txt"]["sitemap_entries_count"] = int(_number(sitemap_count, 0))
    if llms_url:
        canonical["llms_txt"]["url"] = str(llms_url)
    if llms_chars is not None:
        canonical["llms_txt"]["chars"] = int(_number(llms_chars, 0))
    if schema_types:
        canonical["structured_data"]["schema_types_detected"] = schema_types
    if missing:
        canonical["structured_data"]["pages_missing_json_ld"] = missing[:20]
    return canonical


def _site_standards(source: Any) -> dict:
    source = _as_dict(source)
    candidates = [_as_dict(source.get("site_standards")), source]
    for candidate in candidates:
        if "robots_txt" not in candidate and "llms_txt" not in candidate:
            continue
        robots = _as_dict(candidate.get("robots_txt"))
        llms = _as_dict(candidate.get("llms_txt"))
        if robots or llms:
            return {
                "robots_txt": {
                    "status": _status(robots.get("status"), bool(robots)),
                    **({"url": str(_first(robots.get("url"), robots.get("resolved_url")))} if _first(robots.get("url"), robots.get("resolved_url")) else {}),
                },
                "llms_txt": {
                    "status": _status(llms.get("status"), bool(llms)),
                    **({"url": str(_first(llms.get("url"), llms.get("resolved_url")))} if _first(llms.get("url"), llms.get("resolved_url")) else {}),
                    **({"chars": int(_number(llms.get("chars"), 0))} if llms.get("chars") is not None else {}),
                },
            }
    return {}


def _records(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        out: list[dict] = []
        for key in ("pages", "owned_pages", "items", "rows", "page_analysis", "owned_url_readiness", "mapped_owned_urls"):
            out.extend(_records(value.get(key)))
        return out
    return []


def _unique_owned_pages(*sources: Any) -> list[dict]:
    pages: list[dict] = []
    seen: set[str] = set()
    for source in sources:
        for page in _records(source):
            url = _first(page.get("url"), page.get("page_url"), page.get("target_url"), page.get("resolved_url"), page.get("href"), page.get("link"))
            key = str(url or "").strip().lower().rstrip("/")
            if key and key not in seen:
                seen.add(key)
                pages.append(page)
    return pages


def _schema_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [str(x).strip() for x in _as_list(value) if str(x).strip()]


def _crawl_signals(page: dict) -> tuple[bool, bool | None, list[str]]:
    # Only these explicit crawl fields count. Do not read geo_dimensions or
    # scoring dimensions, because those can be inferred scoring artifacts.
    json_present = _first(page.get("json_ld_present"), page.get("jsonLdPresent"))
    block_count = _first(page.get("json_ld_block_count"), page.get("jsonLdBlockCount"))
    schema_types = _schema_list(_first(page.get("schema_types"), page.get("schemaTypes"), page.get("schema_types_detected"), page.get("schemaTypesDetected")))

    has_signal = json_present is not None or block_count is not None or bool(schema_types)
    json_ld = _boolish(json_present)
    if json_ld is None and block_count is not None:
        json_ld = _number(block_count, 0) > 0
    return has_signal, json_ld, schema_types


def build_ai_discoverability_hygiene(bundle: dict | None = None, *evidence_sources: Any) -> tuple[dict, str]:
    """Build the canonical AI discoverability hygiene object.

    Explicit hygiene wins. Otherwise structured-data coverage is derived only
    from explicit crawl fields, never from GEO score dimensions.
    """
    bundle = _as_dict(bundle)
    for source_name, source in [("bundle", bundle), *[(f"evidence_{i}", s) for i, s in enumerate(evidence_sources, start=1)]]:
        for candidate in _hygiene_candidates(source):
            return _canonical_from_existing(candidate), source_name

    standards = {}
    for source in (bundle, *evidence_sources):
        standards = _site_standards(source)
        if standards:
            break

    pages = _unique_owned_pages(bundle, *evidence_sources)
    total = len(pages)
    has_any_signal = False
    pages_with_json = 0
    pages_with_schema = 0
    schema_counts: Counter[str] = Counter()
    missing: list[dict] = []

    for page in pages:
        has_signal, json_ld, schemas = _crawl_signals(page)
        has_any_signal = has_any_signal or has_signal
        if json_ld is True:
            pages_with_json += 1
        if json_ld is True or schemas:
            pages_with_schema += 1
        schema_counts.update(schemas)
        if json_ld is not True and len(missing) < 20:
            missing.append({
                "url": str(_first(page.get("url"), page.get("page_url"), page.get("target_url"), page.get("resolved_url"), "")),
                "title": str(_first(page.get("title"), page.get("page_title"), "")),
            })

    checked = total > 0 and has_any_signal
    coverage = round((pages_with_json / total) * 100, 1) if total else 0
    robots = standards.get("robots_txt") or {"status": "not checked"}
    llms = standards.get("llms_txt") or {"status": "not checked"}

    if checked:
        priority = "high" if robots.get("status") != "available" or llms.get("status") != "available" or coverage < 50 else "medium" if coverage < 80 else "low"
        summary = f"JSON-LD/schema coverage: {pages_with_json}/{total} owned pages ({coverage}%). Robots.txt is {robots['status']}; LLMs.txt is {llms['status']}."
        structured = {
            "owned_pages_total": total,
            "pages_with_schema": pages_with_schema,
            "pages_with_json_ld": pages_with_json,
            "coverage_pct": coverage,
            "schema_types_detected": [[k, v] for k, v in schema_counts.most_common()],
            "pages_missing_json_ld": missing,
        }
        source = "derived_from_explicit_crawl_signals"
    else:
        priority = "high"
        summary = NOT_CHECKED_SUMMARY
        structured = {
            "owned_pages_total": total,
            "pages_with_schema": 0,
            "pages_with_json_ld": 0,
            "coverage_pct": 0,
            "schema_types_detected": [],
            "pages_missing_json_ld": [],
        }
        source = "not_checked_fallback"

    return {
        "priority": priority,
        "summary": summary,
        "robots_txt": robots,
        "llms_txt": llms,
        "structured_data": structured,
    }, source


def attach_ai_discoverability_hygiene(bundle: dict, *evidence_sources: Any) -> dict:
    hygiene, source = build_ai_discoverability_hygiene(bundle, *evidence_sources)
    bundle["ai_discoverability_hygiene"] = hygiene
    bundle["site_ai_hygiene"] = hygiene
    bundle.setdefault("parser_manifest", {})["ai_hygiene_source"] = source
    return bundle
