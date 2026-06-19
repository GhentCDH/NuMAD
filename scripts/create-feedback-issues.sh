#!/usr/bin/env bash
#
# create-feedback-issues.sh
#
# Creates GitHub issues for the NuMAD team feedback on app version 2026-06-10
# (https://tst.numad.ugent.be/en/). Each item was verified against the live app
# with Chrome DevTools, and file references point at the Sampo-UI config files.
#
# Usage:
#   gh auth status        # make sure you are logged in
#   bash scripts/create-feedback-issues.sh
#
# NOTE: This script is NOT idempotent — running it twice creates duplicate issues.
#       Run it once, or delete the previous issues first.
#
# Implementation note: issue bodies are passed via `--body-file -` with a quoted
# heredoc (<<'EOF') piped on stdin. This keeps backticks, parentheses and quotes in
# the body literal — do NOT switch to `--body "$(cat <<'EOF' ...)"`, because the
# command substitution would try to execute backtick-quoted text in the body.
#
set -euo pipefail

REPO="GhentCDH/NuMAD"
ASSIGNEE="Ceetto"

# Sanity check: gh present and authenticated.
command -v gh >/dev/null 2>&1 || { echo "error: gh CLI not found" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "error: not authenticated (run 'gh auth login')" >&2; exit 1; }

echo "Creating feedback issues in $REPO (assignee: $ASSIGNEE)..."

# ---------------------------------------------------------------------------
# Issue 1 — COINS: limit result-table columns to the agreed 13
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" --assignee "$ASSIGNEE" \
  --label "enhancement" \
  --title "COINS: limit result-table to the 13 agreed columns" \
  --body-file - <<'EOF'
**Feedback (v2026-06-10) — Perspective Coins, "Kolommen per munt"**

Keep every field available on the coin **detail page**, but the **table view** of the
COINS perspective should show only these 13 columns:

- ID
- Municipality (former)
- Find spot toponym
- Reece period
- Authority
- Stated authority
- Issuer
- Mint
- Denomination
- T.p.q.
- T.a.q.
- Type

The left-hand **"Narrow down by"** facet list must stay exactly as it is — this change
only affects which columns render in the results table.

**Columns to drop from the table** (still shown on the detail page): Identifier, Object
type, Object classification, Object subclass, State, Reference work, Material,
Denomination detail, Authenticity, Countermark, Weight, Diameter, Axis, Obverse design,
Obverse legend, Reverse design, Reverse legend.

**Verified:** the table currently renders 29 columns (ID … Reverse legend).

**Where to change**
- `sampoConfigs/sampo/search_perspectives/coins.json` → the `properties` array (~lines 283–571).
- Suggested approach: set `onlyOnInstancePage: true` on the columns to drop, so they
  remain on the detail page but disappear from the table.

**Acceptance**
- COINS table shows exactly the 13 columns above, in that order.
- The dropped fields are still visible on a coin's detail page.
- The "Narrow down by" facets are unchanged.
EOF

# ---------------------------------------------------------------------------
# Issue 2 — MINTS map: replace faint heatmap with a normal marker map
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" --assignee "$ASSIGNEE" \
  --label "enhancement" \
  --title "MINTS map: replace faint heatmap with a normal marker map" \
  --body-file - <<'EOF'
**Feedback (v2026-06-10) — Mints**

> The map with the heatmaps is unclear because the colour is so faint that many mint
> locations stay invisible. Better to use a normal map (like 'map').

**Verified:** the "MINTS" map tab (`/coins/faceted-search/mintsheatmap`) renders a
Deck.gl `heatmapLayer`. Because there are only ~109 mints spread across the whole
Mediterranean, the heatmap density is so low that only one or two faint blobs are
visible and most mints are invisible. (Contrast: the finds HEATMAP over Belgium has
32k points clustered in a small area, so it reads fine — heatmaps simply don't suit the
sparse mint dataset.)

**Where to change**
- `sampoConfigs/sampo/search_perspectives/coins.json` → the "Mints Heatmap" map config
  (~lines 87–102: `layerType: "heatmapLayer"`, `sparqlQuery: "mintPlaces"`).
- Switch it to a normal marker map (LeafletMap), modelled on the "Finds Places" map
  config in the same file (~lines 47–70). Keep using the `mintPlaces` query for the data.

**Acceptance**
- Each mint location is shown as a clearly visible marker on a normal map.
EOF

# ---------------------------------------------------------------------------
# Issue 3 — COINS Aoristic chart: show Reece-period breakdown / fix layout
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" --assignee "$ASSIGNEE" \
  --label "bug" \
  --title "COINS Aoristic chart: Reece periods are not all represented" \
  --body-file - <<'EOF'
**Feedback (v2026-06-10) — Aoristic chart**

> Looks nice, but the Reece Periods are not all on it (could it be that the chart is too
> big for the map?).

**Verified:** the Aoristic chart (`/coins/faceted-search/aoristic_chart`) renders as a
single-colour histogram binned by year interval. There is **no Reece-period breakdown,
no per-period series, and no legend** — so the Reece periods the reviewer expects to see
are not represented. The X-axis also runs far past the populated data (empty space all
the way to 2000–2009), which makes the populated Roman range look cramped.

**Where to change**
- `sampoConfigs/sampo/search_perspectives/coins.json` → Aoristic chart config (~lines 140–251).
- Backing queries `coinsByTimeSpansQuery10/20/50/100` in
  `sampoConfigs/sampo/sparql_queries/coins.js` (~lines 314–414).
- Add a Reece-period dimension (e.g. a stacked series + legend per Reece period), and/or
  constrain the X-axis to the populated range so all periods are legible.

**Acceptance**
- The aoristic chart shows the Reece periods (series/legend), and the axis is scoped to
  the data range.
EOF

# ---------------------------------------------------------------------------
# Issue 4 — Reece period facet: split multi-value (semicolon-joined) entries
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" --assignee "$ASSIGNEE" \
  --label "bug" \
  --title "Reece period facet: split multi-value (semicolon-joined) entries" \
  --body-file - <<'EOF'
**Feedback (v2026-06-10) — Reece periods filter**

> The filter does not yet split fields with more than one Reece period; whenever there is
> a semicolon, that signals that the assignment to the exact period failed. (Compare with
> Authority (Ruler), where the split was done correctly.)

**Verified:**
- A combined value exists in the data, e.g.
  `002b Augustan I / Late Celtic ; 003 Augustan II / Gallo-Roman` — a single field
  holding two Reece periods joined by `;`. The Reece period facet keeps these as one
  combined entry instead of splitting them, so exact-period filtering fails.
- The **Authority** facet, by contrast, lists each ruler individually (Unknown,
  Tetricus I, Gallienus, …) with no semicolons — this is the working pattern to follow.

**Where to change**
- Reece period facet: `sampoConfigs/sampo/search_perspectives/coins.json` (~lines 695–707,
  predicate `nmd:hasReecePeriods`, a forward predicate).
- Working reference: Authority facet in the same file (~line 755) uses the reverse-predicate
  path `^nmo:hasAuthority/nmd:hasState/rdfs:label`, which yields individuated values.
- Likely a data/model fix is needed so each Reece period is its own resource rather than a
  combined string literal, mirroring how Authority is modelled.

**Acceptance**
- Coins with multiple Reece periods appear under each individual period in the facet; no
  semicolon-joined entries remain in the filter list.
EOF

# ---------------------------------------------------------------------------
# Issue 5 — "Name" facets show no selectable value list (AUTHORITIES & MINTS)
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" --assignee "$ASSIGNEE" \
  --label "enhancement" \
  --title 'AUTHORITIES & MINTS: "Name" facet shows no selectable value list' \
  --body-file - <<'EOF'
**Feedback (v2026-06-10) — Authorities "Name (Ruler)" and Mints "Name (Mint)"**

> No list of possible filter values is shown.

This was reported for two facets and has the same root cause, so they are grouped here:
- AUTHORITIES perspective → "Name" (Ruler) facet
- MINTS perspective → "Name" (Mint) facet

**Verified:** expanding either facet shows only a free-text search box and a search
button — there is no checklist of selectable values (unlike e.g. the Authority or
Deposition-type facets, which list values with counts). Both are configured as
text-only filters (`textQueryProperty: "rdfs:label"`).

**Where to change**
- `sampoConfigs/sampo/search_perspectives/authorities.json` (~lines 153–158, "Name").
- `sampoConfigs/sampo/search_perspectives/mints.json` (~lines 151–156, "Name").
- Add a `list`-type facet (selectable values with counts), like the other faceted fields,
  either replacing or complementing the existing text search.

**Acceptance**
- Expanding "Name (Ruler)" and "Name (Mint)" shows a selectable list of values with counts.
EOF

# ---------------------------------------------------------------------------
# Issue 6 — FINDS facet charts truncate categories vs the filter list
# ---------------------------------------------------------------------------
gh issue create --repo "$REPO" --assignee "$ASSIGNEE" \
  --label "bug" \
  --title "FINDS facet charts (pie/bar) show only some of the filter values" \
  --body-file - <<'EOF'
**Feedback (v2026-06-10) — reported under "Mints", but the facets are in FINDS**

> For many of the filters (e.g. 'deposition type', 'discovery type'…) I do get the list
> of values to filter on, but the accompanying bar and pie chart show only a few of them.

Note: the feedback was written under the "Mints" heading, but "deposition type" and
"discovery type" are facets of the **FINDS** perspective (MINTS only has a "Name" facet).
Scoping this to FINDS.

**Verified:** in FINDS, the "Deposition type" facet lists 12 distinct values in the
filter (e.g. <isolated find> [523], Unknown [463], Chance loss [92], Burial deposit
[11], Hoard [5], "hoard ; funerary deposition" [3], …). Its **pie chart shows only 3
slices plus an aggregated "Other: 26 (2.36%)" bucket** — the 9 smaller categories are
collapsed and not individually shown. Same effect applies to other facet charts.

**Where to change**
- `sampoConfigs/sampo/search_perspectives/finds.json` → the facet chart configs.
- The relevant knob is `sliceVisibilityThreshold`. Set it to `false`/`0` so all categories
  render (the aoristic configs in `coins.json` already use `sliceVisibilityThreshold: false`).

**Acceptance**
- The pie/bar charts for FINDS facets show all categories present in the filter list (no
  silent "Other" bucket hiding the smaller ones), or this is a deliberate, documented cap.
EOF

echo "Done. View them: gh issue list --repo $REPO --assignee $ASSIGNEE"
