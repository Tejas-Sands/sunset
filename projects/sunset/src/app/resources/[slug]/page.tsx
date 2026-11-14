import type {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {resources,resourceById} from '../../../lib/library.mjs';
import GuideReader,{type GuidePack} from '../../../components/GuideReader';
import InteractiveLab from '../../../components/InteractiveLab';
import {SiteHeader,SiteFooter,Icon} from '../../../components/Protocol';

export const dynamicParams=false;
export function generateStaticParams(){return resources.map(resource=>({slug:resource.id}));}
export async function generateMetadata({params}:{params:Promise<{slug:string}>}):Promise<Metadata>{const {slug}=await params,r=resourceById(slug);return r?{title:`${r.title} · SUNSET`,description:r.description}:{};}
export default async function Resource({params}:{params:Promise<{slug:string}>}){
  const {slug}=await params,r=resourceById(slug);if(!r)notFound();
  return <div className="protocol-site p-reading"><a className="p-skip" href="#reader-content">Skip to content</a><SiteHeader compact/>
    <main className="p-container" id="reader-content"><div className="p-reader-bar"><div className="p-reader-where"><nav aria-label="Breadcrumb"><a href="/#commons">Library</a><span aria-hidden="true">/</span><span>{r.topic.charAt(0)+r.topic.slice(1).toLowerCase()}</span></nav><span className="p-reader-time">{r.duration} read</span></div><div className="p-actions"><a className="p-button" href="#interactive-lab">Try the lab</a><a id="resource-download" className="p-button p-button-accent" href={r.download} download={r.id+'-offline.html'}><Icon name="download"/>Download offline guide</a></div></div>
      <GuideReader pack={r.pack as GuidePack}/><InteractiveLab resourceId={r.id}/>
      <section className="p-sources" aria-labelledby="sources-title"><h2 id="sources-title">Primary references</h2><p>The explanations and exercises are original to SUNSET and released under CC0. The references below keep their own licenses.</p>{r.sources.map(source=><a key={source.href} href={source.href} target="_blank" rel="noreferrer">{source.label}<Icon name="external"/></a>)}<p className="p-small">Your offline copy includes the complete guide and worked examples. Chapter progress stays on your device.</p></section>
    </main><SiteFooter/>
  </div>;
}
