# Canonical Auditor Modules

The following scripts are the **canonical** modules used by the Bodhi Auditor workflow.
Numbered pipeline scripts (00-18, 99) and `run_pipeline.py` have been removed as they
were superseded by `build_query_workbench_bundle.py`.

## Active Scripts

| Script | Purpose |
|--------|--------|
| `build_query_workbench_bundle.py` | **Canonical builder** — assembles the `frontend_report_bundle.json` |
| `ai_hygiene.py` | AI discoverability hygiene checks (robots.txt, llms.txt, JSON-LD) |
| `lib.py` | Shared utilities (JSON I/O, text cleaning, URL helpers) |
| `build_query_portfolio.py` | Query portfolio builder |
| `score_owned_geo_readiness.py` | Page-intrinsic GEO readiness scorer |
| `map_queries_to_owned_urls.py` | Query-to-owned-URL mapping |
| `generate_page_level_cms_actions.py` | Page-level CMS recommendation generator |
| `generate_grouped_pr_opportunities.py` | Grouped PR opportunity generator |
| `normalise_ai_citations.py` | AI citation normaliser |
| `extract_benchmark_patterns.py` | External benchmark pattern extractor |
| `load_sitemap_inventory.py` | Sitemap inventory loader |
| `local_hybrid_scraper.py` | Local hybrid page scraper |
| `strict_geo_visibility_runtime.py` | Strict GEO visibility runtime |
| `validate_frontend_bundle.py` | Frontend bundle validator |

## Note on ai_hygiene.py and lib.py

Both `ai_hygiene.py` and `lib.py` exist in the Evidence Service repo as well.
- `lib.py` is **identical** between repos — shared utility functions.
- `ai_hygiene.py` has **diverged** — the Evidence Service version handles runtime HTTP
  checks (robots.txt fetching), while this Auditor version works from pre-crawled data.

Both versions are intentionally kept because the repos are deployed independently.
The Evidence Service version is canonical for runtime checks; the Auditor version
is canonical for offline/batch analysis from crawl artifacts.
