# Page-Level CMS and Grouped PR Contract

This contract refines the locked query-led GEO loop.

## CMS optimisation

CMS recommendations are generated at owned-page level, not as one recommendation per query.

For each owned URL, the builder aggregates all linked queries, top external citation patterns, source types, observed domains, current GEO gaps and AI visibility statuses. It then recommends the top 2-3 highest-value page changes only.

Page CMS changes are prioritised by:

- number of linked queries covered
- current external-led or competitor-led AI visibility gaps
- absence of owned target-page citation
- current owned-page GEO score
- quality of external winning patterns
- source authority and evidence value

CMS actions are tracked by owned URL and should be rerun against the same linked query set to measure page GEO score and AI visibility score movement.

## PR optimisation

PR recommendations are grouped by source type and query cluster. They are not URL-specific and must not be assigned to owned pages.

PR opportunities are prioritised by:

- number of grouped queries influenced
- source type value, e.g. authority, publisher, partner, finance/insurance, competitor, forum/social
- competitor-led or external-led visibility status
- observed external domains and journey mix

Forum/social/video sources are treated as objection evidence and community-signal monitoring unless explicitly validated as a PR target.

## Measurement

CMS success metrics:

- page_geo_score_120_delta
- linked_query_ai_visibility_score_delta
- owned_target_citation_count_delta

PR success metrics:

- grouped_query_ai_visibility_score_delta
- external_led_query_count_delta
- competitor_led_query_count_delta
- owned_domain_citation_count_delta
