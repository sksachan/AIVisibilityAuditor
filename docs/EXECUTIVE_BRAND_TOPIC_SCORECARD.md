# Executive Brand Topic Scorecard Contract

Stage 2 adds an evidence-backed, CMO-ready topic scorecard to the canonical frontend report bundle.

The scorecard is generated deterministically by `scripts/build_query_workbench_bundle.py` from `query_workbench` evidence. It groups queries by brand topic / journey category and calculates:

- topic query coverage
- average AI visibility score where citation evidence exists
- mapped owned URL coverage
- citation count
- owned target / owned domain citation counts
- dominant visibility status
- top competitor or external source indicator
- direction versus last period when rerun deltas are available

The builder emits the scorecard in three places for compatibility:

```json
{
  "executive": {
    "brandTopicScorecard": [],
    "brand_topic_scorecard": []
  },
  "executive_summary": {
    "schema_version": "executive_topic_scorecard.v1",
    "brand_topic_scorecard": [],
    "scorecard_methodology": "..."
  }
}
```

Frontend v21 reads `executive.brandTopicScorecard` first and falls back to deriving the same table when the field is missing.

For dry runs without SerpAPI, the scorecard must not fabricate visibility. Rows should show `aiVisibilityScore: null` and comments explaining that fresh AI citation evidence was not collected.

For live evidence runs, scores are based on observed query-level visibility signals and citations. Competitor and source comments must only use observed evidence.
