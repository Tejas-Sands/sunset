import type {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {resources,resourceById} from '../../../lib/library.mjs';
import GuideReader,{type GuidePack} from '../../../components/GuideReader';
import InteractiveLab from '../../../components/InteractiveLab';
import {SiteHeader,SiteFooter,Arrow} from '../../../components/Protocol';

export const dynamicParams=false;
export function generateStaticParams(){return resources.map(resource=>({slug:resource.id}));}
export async function generateMetadata({params}:{params:Promise<{slug:string}>}):Promise<Metadata>{const {slug}=await params,r=resourceById(slug);return r?{title:`${r.title} · SUNSET`,description:r.description}:{};}
export default async function Resource({params}:{params:Promise<{slug:string}>}){
  const {slug}=await params,r=resourceById(slug);if(!r)notFound();
  return <div className="protocol-site p-reading"><a className="p-skip" href="#reader-content">Skip to content</a><SiteHeader compact/>
    <main className="p-container" id="reader-content"><div className="p-reader-bar"><a href="/#commons">The commons / {r.topic.toLowerCase()}</a><div className="p-actions"><a className="p-text-button" href="#interactive-lab">Try the lab <Arrow/></a><a id="resource-download" className="p-button" href={r.download} download={r.id+'-offline.html'}>Download offline guide <Arrow down/></a></div></div>
      <GuideReader pack={r.pack as GuidePack}/><InteractiveLab resourceId={r.id}/>
      <section className="p-sources" aria-labelledby="sources-title"><span className="p-kicker">FOLLOW THE ORIGINAL WORK</span><h2 id="sources-title">Primary references.</h2><p>Original SUNSET explanations and exercises, released under CC0. The references below retain their own licenses.</p>{r.sources.map(source=><a key={source.href} href={source.href} target="_blank" rel="noreferrer">{source.label}<Arrow/></a>)}<p className="p-small">Your offline copy includes the complete reading guide and worked examples. Chapter progress stays on your device.</p></section>
    </main><SiteFooter/>
  </div>;
}
