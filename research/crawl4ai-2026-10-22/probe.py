import asyncio,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode,JsonCssExtractionStrategy

async def main():
 out=Path('/tmp/near-crawl-research-output')
 schema={'name':'NEAR Builders visible project titles','baseSelector':'button[aria-label^="Preview "]','fields':[
  {'name':'title','selector':'span.truncate.font-bold','type':'text'},
  {'name':'preview_label','selector':'','type':'attribute','attribute':'aria-label'}]}
 conf=CrawlerRunConfig(cache_mode=CacheMode.BYPASS,check_robots_txt=True,page_timeout=30000,
  wait_for='css:button[aria-label^="Preview "]',wait_for_timeout=20000,delay_before_return_html=1,
  extraction_strategy=JsonCssExtractionStrategy(schema),verbose=False)
 async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False,ignore_https_errors=False)) as c:
  r=await c.arun('https://nearbuilders.org/projects',config=conf)
  rows=json.loads(r.extracted_content or '[]')
  (out/'nearbuilders-structured.json').write_text(json.dumps(rows,indent=2)+'\n')
  report={'tool':'Crawl4AI','version':'0.9.5','url':r.url,'status_code':r.status_code,'success':r.success,
   'method':'Rendered browser DOM; CSS extraction of observed preview buttons; explicit CSS wait',
   'records':len(rows),'nonempty_titles':sum(bool(v.get('title')) for v in rows),
   'robots_check':True,'paid_llm_calls':0,'fetched_at':datetime.now(timezone.utc).isoformat(),
   'html_sha256':hashlib.sha256((r.html or '').encode()).hexdigest()}
  (out/'structured-verification.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps(report),flush=True)
  print(json.dumps({'sample':rows[:3]}),flush=True)
  assert r.success and 200 <= r.status_code < 300
  assert len(rows)>100 and all(x.get('title') for x in rows)
asyncio.run(main())
