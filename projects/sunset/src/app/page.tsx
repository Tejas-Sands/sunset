import {resources} from '../lib/library.mjs';
import SunsetMark from '../components/SunsetMark';
import ReleasePath from '../components/ReleasePath';
import MotionReveal from '../components/MotionReveal';
import {SiteHeader,SiteFooter,Icon,ResourceCard} from '../components/Protocol';

const steps=[
  ['Commit the work','The creator prepares the finished resource, keeps a private release backup and names a reviewer. The agreement fixes the beneficiary, goal, deadlines and CC0 license.'],
  ['Fund its release','Once the reviewer approves, sponsors connect their own wallets and add to the pool. Each wallet request is explicit and shows the exact deposit.'],
  ['Open it for good','The creator publishes the matching key on time. Anyone can then read the resource without an account and download a copy that works offline.']
];
const questions=[
  ['Do I need a wallet?','No, not to read. The guides, their interactive labs and the offline downloads are open to everyone. Connect a NEAR testnet wallet only to sponsor, publish, withdraw credit or manage a stewardship token.'],
  ['What exactly does sponsorship fund?','A creator commits an already finished resource to a fixed release agreement. Sponsors pool support up to its goal. Publishing the matching key on time opens the resource and credits the creator, who can then withdraw.'],
  ['What happens when a deadline is missed?','The campaign becomes refundable. Contributors claim their contribution as credit, then withdraw it to their own wallet. Network gas and storage allowances are separate from sponsorship.'],
  ['Are the three guides funded campaigns?','No. They are original free resources, available now and separate from the campaign catalog. The app reads the contract for actual campaign states and never presents these guides as funded releases.'],
  ['Can anyone publish a campaign?','Not on this deployment. Publishing on the testnet contract is curated by its configured creator account, and a named reviewer approves the committed content. Sponsorship is open to anyone while a campaign is active.'],
  ['What survives if this website disappears?','Your copy. A downloaded guide holds its content and reader in one HTML file you can keep and share. Released campaigns also keep their content commitments onchain, plus a transferable right to maintain a matching recovery mirror.']
];
export default function Landing(){return <div className="protocol-site p-landing"><a className="p-skip" href="#content">Skip to content</a><MotionReveal/><SiteHeader/>
  <main id="content">
    <section className="p-hero p-container" aria-labelledby="hero-title">
      <div className="p-hero-copy"><h1 id="hero-title">Fund a work once.<br/>It stays open to everyone.</h1>
        <p>Creators commit a finished resource and a goal. Sponsors pool testNEAR on NEAR. When the release key is published on time, the work enters the public domain. If a deadline is missed, sponsors get their contributions back.</p>
        <div className="p-actions"><a className="p-button p-button-accent p-button-large" href="#commons">Read the library</a><a className="p-button p-button-large" href="/app/?view=Funding">See live campaigns<Icon name="forward"/></a></div>
        <p className="p-hero-aside">No wallet or account is needed to read.</p></div>
      <ReleasePath/>
    </section>
    <section id="commons" className="p-commons p-container" aria-labelledby="commons-title">
      <div className="p-section-heading" data-reveal=""><h2 id="commons-title">The open library</h2><p>Three original guides with working calculations: attention, gradients and low-rank adaptation. Read them here or keep a copy that works offline.</p></div>
      <div className="p-resource-grid" data-reveal="stagger">{resources.map(resource=><ResourceCard key={resource.id} resource={resource}/>)}</div>
    </section>
    <section id="how-it-works" className="p-mechanism" aria-labelledby="mechanism-title"><div className="p-container">
      <div className="p-section-heading" data-reveal=""><h2 id="mechanism-title">How a release works</h2><p>One fixed agreement, enforced by a contract on NEAR testnet. There are only two ways a campaign can end.</p></div>
      <ol className="p-steps" data-reveal="stagger">{steps.map(([title,copy],i)=><li key={title}><span className="p-step-number" aria-hidden="true">{i+1}</span><h3>{title}</h3><p>{copy}</p></li>)}</ol>
      <div className="p-outcomes" data-reveal="stagger">
        <article className="p-outcome p-outcome-open"><span className="p-outcome-icon"><Icon name="check" size={20}/></span><div><h3>Released on time</h3><p>The resource is public under CC0. The creator is credited the pooled amount and a stewardship token is created.</p></div></article>
        <article className="p-outcome p-outcome-refund"><span className="p-outcome-icon"><Icon name="clock" size={20}/></span><div><h3>A deadline is missed</h3><p>The resource stays encrypted. Every sponsor can claim their contribution and withdraw it to their wallet.</p></div></article>
      </div>
      <a className="p-text-button" href="/app/?view=Funding">See both outcomes on testnet<Icon name="forward"/></a>
    </div></section>
    <section id="stewardship" className="p-stewardship p-container" aria-labelledby="stewardship-title" data-reveal="stagger">
      <div><h2 id="stewardship-title">The host can change. The work stays open.</h2>
        <p>Each release creates one stewardship NFT. Its holder has a practical job: keep the preferred recovery mirror current. Transfer the token and that job moves to the next holder.</p>
        <a className="p-button" href="/app/?view=Stewardship">View stewardship tokens<Icon name="forward"/></a></div>
      <div className="p-steward-card"><div className="p-steward-card-head"><SunsetMark/><div><strong>Stewardship token</strong><span>One per released resource, transferable</span></div></div>
        <dl><div><dt>The holder controls</dt><dd>The preferred recovery mirror</dd></div><div><dt>The holder never controls</dt><dd>Who can read, or the CC0 license</dd></div><div><dt>Stays fixed on transfer</dt><dd>The creator’s payout and sponsor refunds</dd></div></dl></div>
    </section>
    <section id="questions" className="p-faq p-container" aria-labelledby="faq-title" data-reveal=""><div><h2 id="faq-title">Questions</h2><p>What to know before you connect a wallet.</p></div><div>{questions.map(([question,answer])=><details key={question}><summary>{question}<Icon name="chevron"/></summary><p>{answer}</p></details>)}</div></section>
    <section className="p-final p-container" aria-labelledby="final-title" data-reveal=""><div><h2 id="final-title">Start with something you can read today.</h2><p>The library is free. Campaigns are live on NEAR testnet.</p></div><div className="p-actions"><a className="p-button p-button-accent p-button-large" href="#commons">Read the library</a><a className="p-button p-button-large" href="/app/">Open the app</a></div></section>
  </main><SiteFooter/>
</div>;}
