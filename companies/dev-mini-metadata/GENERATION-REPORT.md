# Generation report: dev-mini

Derived artifact: re-emit with `python -m orgsmith report dev-mini`. Never edit by hand. Nothing here gates anything; it is what the quality instrument measured and what the review board said, for a human to read.

13 documents planned; 11 carry authored prose.

## Provenance

Generator, per batch (self-reported at ingest; not verifiable):

| work order | model | effort |
| --- | --- | --- |
| wo:author:0001 | claude-opus-4-8 | max |
| wo:author:0002 | claude-opus-4-8 | max |
| wo:author:0003 | claude-opus-4-8 | max |
| wo:author:0004 | claude-opus-4-8 | max |
| wo:foundation:0001 | claude-opus-4-8 | max |

## Length against brief

11 authored documents, 3638 words, mean 331.

Every document is within 75%-150% of the words its brief asked for.

## Same-genre similarity

No same-genre pair reaches 0.15 4-gram Jaccard (highest: 0.087).

## Review board

7 findings from the review board.

| id | dimension | severity | docs | summary |
| --- | --- | --- | --- | --- |
| rf:docplaus-letterhead-dup | document_plausibility | major | d:0001, d:0005, d:0008 | Every rendered engagement letter prints the firm name twice at the top, once in the letterhead/running header and again as the first body line placed directly above the client's inside address, so the recipient block reads as though the letter were addressed to Pinebrook itself. |
| rf:voice-1 | cross_document_voice | minor | d:0001, d:0002, d:0005, d:0006, d:0011 | The authorial voice does not vary by author: Managing Partner, both Principals, and the analysts all deploy the same balanced 'not X but Y' antithesis, the same triadic cadence, and the same 'settle it now rather than in front of the client' aphorism, so the distinct personas the foundation promises never surface, and internal staff-to-staff memos carry the same literary polish as the partner's client letters where the partner's editing does not even apply. |
| rf:docplaus-missing-dates | document_plausibility | minor | d:0002, d:0006, d:0003, d:0007, d:0009 | The internal working documents carry no date on the document itself: the kickoff-memo header is To/From/Re with the conventional Date line omitted, and the meeting minutes give location and attendees but no meeting date or time; each document's date survives only in its filename. |
| rf:finance-payment-terms-1 | finance_realism | minor | d:0001, d:0005, d:0008 | All three executed fixed-fee engagement letters state the fee but specify no payment terms: no invoicing schedule, retainer, installments, or net terms for a signed six-figure contract. |
| rf:graphacl-1 | graph_acl_naturalness | minor | d:0008, d:0009, d:0010, d:0011, d:0012, d:0013 | The open-posture ACL grants departed analyst Susan Wiley read access to every document created after she left, including both annual financial summaries, because grants are built over the whole roster with no employment-date filter. |
| rf:graphacl-2 | graph_acl_naturalness | note | corpus | The who-knows-whom half reads organic, not assembled: staffing varies with headcount and tracks the one departure/backfill, mentions are role-appropriate, and each client carries a single named sponsor. Recording as a strength so it is not flattened. |
| rf:org-realism-1 | org_realism | note | d:0001, d:0008 | In two of the three engagements the firm presents Senior Consultant Jennifer Fletcher to the client as the engagement lead over Principal Consultant Robert Miller, the manager she reports to, who does the hands-on work under her direction. |
