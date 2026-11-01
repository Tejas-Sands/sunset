# NEAR Builders project and community research

Collected on October 22, 2026 to help choose a more distinctive NEAR hackathon project. Start with [FINDINGS.md](FINDINGS.md), browse the [readable idea index](project-index.md), or filter [projects.csv](projects.csv). [projects.json](projects.json) holds the same records for further analysis.

## What is included

| Material | Count | File |
| --- | ---: | --- |
| Native project-board entries | 125 | [projects.csv](projects.csv) and [projects.json](projects.json) |
| Linked NEAR Catalog listings | 11 | The same files, with origin `claimed_near_catalog` |
| Current public GitHub issues | 16 | [community-signals.csv](community-signals.csv) |
| Public replies to those issues | 18 | [discussion-comments.csv](discussion-comments.csv) |
| Recent activity events | 100 | [recent-activity.csv](recent-activity.csv) |
| Groups sharing a title or repository field | 7 | [possible-duplicates.json](possible-duplicates.json) |

The 125 native entries comprise **75 ideas, 39 projects, 10 scopes, and 1 result**. Their creation timestamps range from May 27 to October 21, 2026. Both project-list pages reached a terminal response, and all 125 source IDs are unique. The catalog response also reached its terminal page. All source records are retained, including repeated listings.

The summaries are paraphrases. Metadata such as kind, status, dates, repository fields, and catalog phase comes from the source. A listing's status or category does not establish that its software works. Repository fields sometimes contain ordinary website URLs. Topic tags are simple keyword labels for navigation, not measurements of demand.

## Discussion coverage

[community-discussions.json](community-discussions.json) joins issue metadata and summarized replies. These are conversations in the public `NEARBuilders/nearbuilders.org` issue tracker. Several replies offer to implement work; those offers do not establish delivery or broad user demand.

The activity sample covers October 12 through October 21. **72 of the 100 events have no public payload in the API response.** They are retained as activity metadata, not represented as discussion transcripts. More activity pages exist; this sample is deliberately bounded.

Private Telegram and Discord conversations were not accessed. This collection is not a verified archive of historical hackathon entrants or winners. The lone native `result` entry is a source category, not a prize result.

## Sources and collection method

The requested `/dashboard` route required authentication in the content fetcher. The public [project board](https://nearbuilders.org/projects) explicitly allows anonymous browsing. Its [published guide](https://nearbuilders.org/skill.md) documents the public API and links to its [OpenAPI specification](https://nearbuilders.org/api/spec.json).

The project pages were collected with read-only requests to documented public endpoints. [collection-manifest.json](collection-manifest.json) records the exact listing URLs, pagination evidence, counts, limits, and source ranges. [public-read-contracts.json](public-read-contracts.json) contains the four relevant GET contracts. Follow the returned cursor when refreshing; a future listing may need more pages than this snapshot.

The existing collector at `/home/citrux/Sides/new_dir/community-explorer/v2` was inspected. Its host checks, GraphQL operations, browser session, and projections are specific to Arc House. Its useful patterns informed the source and pagination checks here; its code and archive were left unchanged. Direct public JSON reads were sufficient, so no replacement browser-scraping framework was added.

Full website assets, full proposal bodies, browser profiles, credentials, and private conversations are excluded. The source links and body hashes allow a deeper review of a particular entry without copying the whole site.
