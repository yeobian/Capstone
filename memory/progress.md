# Progress

This file contains manual test notes from early development.
I ran the retrieval system against different clothing queries and recorded
how well the results matched — this helped me understand where the model
performs well and where it struggles.

---

3/16/2026
## Query Test 1
- Query: light blue shirt
- Result quality: okay to good
- Why: returned top-like clothing items with somewhat similar category and neutral color palette, though exact style match is still inconsistent.

## Query Test 2
- Query: cream cable-knit sweater
- Result quality: okay
- Category match: partial to good
- Style match: partial
- Why: the system returned mostly top/sweater-like items, which is a meaningful improvement over earlier results. However, some returned items still differ in exact garment type, texture, and style, so retrieval is not yet consistently precise.

## Query Test 3
- Query: navy puffer jacket
- Result quality: bad
- Category match: weak
- Style match: weak
- Why: the system did not return jacket-like items consistently. Several results were unrelated tops or even non-jacket clothing, so the retrieval failed to capture the key outerwear structure and material of the query.

## Query Test 4
- Query: black cardigan
- Result quality: bad
- Category match: weak
- Style match: weak
- Why: the system returned mostly unrelated items such as a knit top, a coat/blazer, pants, and a sweatshirt-like top instead of cardigan-like results. The retrieval captured broad clothing similarity but failed to preserve the specific cardigan category and structure.

## Query Test 5
- Query: black pants
- Result quality: good
- Category match: good
- Style match: partial to good
- Why: the system returned mostly pants-like results, which shows the local CLIP baseline can preserve broad clothing category better for this query. Exact cut, fabric, and style still vary, but the retrieval is meaningfully aligned with the input.
## Baseline Summary
The local CLIP baseline performs reasonably well on broad clothing categories such as shirts and pants, but it is less reliable on more specific garment types such as puffer jackets and cardigans. This suggests that the current system captures general apparel similarity better than fine-grained fashion structure or style.

## Main Pattern
- Stronger on: broad clothing categories, especially pants and some generic tops
- Weaker on: specific outerwear and cardigan-like items
- Main limitation: broad visual similarity is captured better than exact garment type and structure


## Its okay sometimes you just have to work on it