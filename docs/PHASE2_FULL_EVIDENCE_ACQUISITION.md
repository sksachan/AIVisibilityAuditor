# Phase 2 Full Evidence Acquisition — AIVisibilityAuditor v5

This version prepares the deterministic repo for the full Phase 2 flow:

1. Manual, reuse or synthetic DeepResearch query portfolio input.
2. Sitemap / site-standards URL inventory loading.
3. Query-to-owned URL mapping with configurable `max_owned_pages_per_query`.
4. Optional SerpAPI / Google AI Mode citation collection upstream.
5. Optional owned and external URL crawl refresh upstream.
6. Deterministic benchmark pattern extraction.
7. Page-level CMS recommendation aggregation.
8. Grouped, non-URL-specific PR opportunity aggregation.
9. Canonical frontend bundle: `schema_version=query_workbench.v1`, `contract_version=page_level_cms_grouped_pr.v2`.

Paid collection is controlled outside this builder. The builder records whether `enable_serpapi`, `enable_owned_crawl`, and `enable_external_crawl` were enabled, but it does not force paid calls.

## Safe test mode

```bash
python3 scripts/build_query_workbench_bundle.py \
  --project-root . \
  --brand Nissan \
  --market Japan \
  --domain https://www.nissan.co.jp \
  --run-mode reuse_existing_evidence \
  --query-portfolio-mode reuse \
  --enable-serpapi false \
  --enable-owned-crawl true \
  --enable-external-crawl false \
  --max-owned 3 \
  --max-external 3
```

## Paid limited test mode

```bash
python3 scripts/build_query_workbench_bundle.py \
  --project-root . \
  --brand Nissan \
  --market Japan \
  --domain https://www.nissan.co.jp \
  --run-mode fresh_ai_citations \
  --query-portfolio-mode manual \
  --query-portfolio outputs/query_portfolio/query_portfolio.json \
  --sitemap-inventory outputs/sitemap/sitemap_inventory.json \
  --ai-citations outputs/ai_citations/ai_citations.json \
  --enable-serpapi true \
  --enable-owned-crawl true \
  --enable-external-crawl true \
  --query-limit 5 \
  --max-owned 3 \
  --max-external 3
```

## Report selection rule

The dashboard should always load the last successful completed bundle. In-progress and failed refresh runs must be displayed as run status only and must not replace the loaded report.
