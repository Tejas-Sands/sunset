# Crawl4AI research collection

Crawl4AI 0.9.5 was installed and exercised locally on 22 October 2026, using an isolated environment at `/tmp/near-crawl4ai-env`. It controlled a fresh headless Chromium browser; no existing signed-in profile was used.

The successful structured probe extracted **136 nonempty project titles** from the rendered public NEAR Builders board. It waited for the observed preview-button selector and used CSS extraction. The initial short-wait fetch had returned a loading shell, so HTTP 200 alone was not accepted as project coverage.

- [Rendered project titles](nearbuilders-titles.json)
- [Structured extraction checks](structured-verification.json)
- [Browser fetch metadata](crawl-manifest.json)
- [Installed package versions](environment.json)
- [Research probe](probe.py)

Raw HTML and Markdown were used temporarily to inspect sources. Retained artifacts contain metadata, titles and original research analysis rather than a mirror of source websites.

## Method and limitations

The browser pass made thirteen fetches across eleven distinct URLs. Eleven fetches returned a 2xx status. Two returned 404, even though the library's `success` field was true; the HTTP status must also be checked. A successful fetch may still be a loading page. These distinctions are recorded in the manifest.

The first OutLayer vault URL was wrong. The correct `/docs/vaults` URL was discovered from the current custody documentation and checked separately. The old Algora pricing page also returned 404; current Algora scope was checked against its homepage. Neither failed URL supports a current product claim.

`check_robots_txt=True` was enabled. No paid extraction model or Crawl4AI Cloud service was used. The browser and CSS extractor supplied content; project comparison and proposed designs are the assistant's analysis. Titles are not evidence that projects work or have users.

## Repeating the narrow probe

The probe is research tooling and is separate from hackathon product development. Its assertions check HTTP success, record count above 100, and nonempty extracted titles. They do not assume the live board will always contain exactly 136 records.

The temporary environment currently contains the required library and matching Playwright browser. Run:

```sh
CRAWL4AI_NO_CLOUD_NOTICE=1 /tmp/near-crawl4ai-env/bin/python research/crawl4ai-2026-10-22/probe.py
```

It writes fresh output under `/tmp/near-crawl-research-output`; it does not overwrite this dated snapshot. If the temporary environment no longer exists, create an isolated environment and install `crawl4ai==0.9.5` following the official setup instructions before running it.

## Why this tool was chosen

Crawl4AI fits the existing Python research workflow and directly produces Markdown or CSS-based structured extraction. Crawlee's JavaScript tooling provides crawling queues and browser-based handlers, which would be useful for a larger maintained crawl. Crawlee was reviewed, not installed or benchmarked in this run. Installing both would not improve the completed extraction.

[Crawl4AI quick start](https://docs.crawl4ai.com/core/quickstart/), [installation](https://docs.crawl4ai.com/core/installation/), [Crawlee quick start](https://crawlee.dev/js/docs/quick-start).
