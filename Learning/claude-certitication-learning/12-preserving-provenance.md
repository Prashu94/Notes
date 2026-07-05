# Chapter 12: Preserving Provenance

---

## 12.1 The Attribution Loss Problem

When summarizing results from multiple sources, the "claim → source" link can be lost.

### Bad
```text
"The AI music market is estimated at $3.2B." (No source, no year.)
```

### Good
```json
{
  "claim": "The AI music market is estimated at $3.2B.",
  "source_url": "https://example.com/report",
  "source_name": "Global AI Music Report 2024",
  "publication_date": "2024-06-15",
  "confidence": 0.9
}
```

---

## 12.2 Handling Conflicting Data

When two sources provide different values:

```json
{
  "claim": "Share of AI-generated music on streaming platforms",
  "values": [
    {
      "value": "12%",
      "source": "Spotify Annual Report 2024",
      "date": "2024-03",
      "methodology": "Automated classification"
    },
    {
      "value": "8%",
      "source": "Music Industry Association Survey",
      "date": "2024-07",
      "methodology": "Survey of 500 labels"
    }
  ],
  "conflict_detected": true,
  "possible_explanation": "Difference in methodology and time period"
}
```

**Do not arbitrarily choose one value.** Preserve both with attribution; let coordinator decide.

---

## 12.3 Include Dates for Correct Interpretation

### Bad
```text
"Source A says 10%, source B says 15%. Contradiction."
```

### Good
```text
"Source A (2023) says 10%, source B (2024) says 15%. Likely +5% growth over a year."
```

Without dates, temporal differences misinterpreted as contradictions.

---

## 12.4 Render by Content Type

Don't force everything into one format:

| Content Type | Format |
|--------------|--------|
| Financial data | Tables |
| News and analysis | Prose |
| Technical findings | Structured lists |
| Time series | Chronological ordering |

---

## Subagent Output Requirements

Require structured subagent output:
- Claim
- Quote
- Source URL
- Publication date

Structure final reports to separate:
- **Confirmed findings** (well-supported)
- **Disputed findings** (conflicting sources with attribution)

---

## Memory Aids

| Principle | Action |
|-----------|--------|
| Attribution | claim → source mapping always |
| Conflicts | Preserve both, don't pick one |
| Temporal data | Include publication dates |
| Synthesis | Separate confirmed vs disputed |
| Content types | Match format to data type |
