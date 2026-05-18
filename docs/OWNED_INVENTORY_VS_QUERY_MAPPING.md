# Owned inventory vs query mapping

AIVisibilityAuditor v5.9 separates two scopes:

1. Site-level owned inventory readiness: all crawled inventory URLs are GEO scored and shown as the broader owned-site readiness baseline.
2. Query-mapped optimisation scope: only the top mapped URLs per query are used for query diagnostics, CMS recommendations, PR/action logic and opportunity analysis.

Inputs expected from Evidence Service v3.5.3:
- `owned_pages_full.pages[*].site_inventory_audit`
- `owned_pages_full.pages[*].query_mapped`
- `owned_pages_full.pages[*].inventory_source`
- `query_owned_url_mapping.json.mappings`

Outputs:
- `outputs/page_scores/owned_page_scores.json.scope.owned_inventory_scored`
- `outputs/page_scores/owned_page_scores.json.scope.owned_query_mapped_scored`
- page-level `query_mapped`, `inventory_source`, `related_query_count` and `technical_signals`
