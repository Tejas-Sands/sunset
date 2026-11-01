import Image from 'next/image';

function Arrow({diagonal=false}:{diagonal?:boolean}){
  return <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={diagonal?'M6 18 18 6M6 6h12v12':'M4 12h15m-6-6 6 6-6 6'}/></svg>;
}
function Sun({className=''}:{className?:string}){
  return <svg className={className} width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M5 22a15 15 0 0 1 30 0" fill="currentColor"/><path d="M5 26h30M8 31h24M13 36h14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/></svg>;
}
function Symbol({name}:{name:'people'|'release'|'offline'|'leaf'|'play'}){
  const path={people:'M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm8-1a2.5 2.5 0 1 0 0-5M2 20v-2a6 6 0 0 1 12 0v2m2-7a5 5 0 0 1 5 5v2',release:'M7 10V7a5 5 0 0 1 10 0m-13 8h16v11H4V10Zm5 5 2 2 4-4',offline:'M5 3h14v18H5V3Zm4 4h6m-6 4h6m-6 5 2 2 4-4',leaf:'M19 4C8 1 2 9 7 15s14-1 12-11ZM5 21 15 9',play:'m9 5 11 7-11 7V5Z'}[name];
  return <svg width="25" height="25" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.45" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={path}/></svg>;
}
function Cover({variant}:{variant:number}){
  const colors=[['#e7ad73','#ed643c','#42594a','#2b4337'],['#c6d9d5','#ebbe79','#799b92','#325d57'],['#e1cfba','#d8784a','#9c997a','#515b45']][variant];
  return <svg className="lp-cover" viewBox="0 0 400 250" role="img" aria-label={['A lantern-lit path through a sunset forest','A winding river between quiet green hills','Sculptural counting stones in a village market'][variant]}>
    <rect width="400" height="250" fill={colors[0]}/><circle cx={variant===1?95:290} cy="80" r="48" fill={colors[1]}/>
    <path d="M0 162 67 102 155 168 246 104 400 174v76H0Z" fill={colors[2]}/><path d="M0 211 97 151 231 215 325 159 400 188v62H0Z" fill={colors[3]}/>
    {variant===0?<><path d="M222 250q-38-30 8-53t28-52" stroke="#f6d4a2" strokeWidth="18" fill="none"/><path d="M44 217v-87m-21 31 21-33 21 33m-16-18-5-21-6 21M342 245v-85m-17 27 17-32 17 32" stroke="#243e32" strokeWidth="6" fill="none"/><g fill="#ffcc72"><circle cx="226" cy="220" r="5"/><circle cx="238" cy="188" r="4"/><circle cx="252" cy="157" r="3"/></g></>:variant===1?<><path d="M220 250q-100-40-10-72t-19-62" stroke="#d7e9e3" strokeWidth="35" fill="none"/><path d="m51 209 17-8 18 8-18 8z m264 11 14-7 16 7-16 7z" fill="#b5c7b4"/></>:<g><ellipse cx="210" cy="228" rx="92" ry="10" fill="#203a2c" opacity=".25"/><rect x="113" y="180" width="41" height="41" rx="20" fill="#dca978"/><rect x="166" y="150" width="41" height="71" rx="20" fill="#ead4ae"/><rect x="219" y="120" width="41" height="101" rx="20" fill="#ca6d44"/><path d="M272 221h30v-72h-30z" fill="#e8b578"/></g>}
    <path d="M30 36h50m-37 9h32M309 34h55" stroke="#fffaf1" strokeOpacity=".6" strokeWidth="3" strokeLinecap="round"/>
  </svg>;
}
const resources=[
  {id:'lantern-trail',name:'The Lantern Trail',description:'Five number puzzles. One little journey to bring the lighthouse back to life.',status:'Funding demo',variant:0,footer:'6.4 of 8 NEAR · sample funding',tone:'funding'},
  {id:'river-routes',name:'River Routes',description:'Explore the refund story when a resource does not reach its funding goal.',status:'Refund demo',variant:1,footer:'Expired campaign · try a refund',tone:'refund'},
  {id:'pebble-market',name:'The Pebble Market',description:'A released sample you can play, download and keep on your own device.',status:'Public sample',variant:2,footer:'CC0 content · free to explore',tone:'public'},
];
const faqs=[
  ['Do I need a wallet?', 'You can try the sample and use a downloaded game without a wallet or account. The current workspace lets adults rehearse funding and release with sample accounts and simulated NEAR.'],
  ['What happens if a resource is not released?', 'The funding agreement has a deadline for funding and a deadline for public key disclosure. If its conditions are missed, contributors can claim their refundable contribution. The rehearsal lets you explore both outcomes.'],
  ['What am I supporting?', 'A specific, already prepared learning pack and its public release. The creator receives a capped payment when the committed key is published on time. Sponsorship does not buy an exclusive copy.'],
  ['What does the stewardship NFT control?', 'Its current holder can maintain the preferred recovery mirror for an already released pack. Transferring the token hands over that maintenance role. It does not transfer copyright, redirect creator payments or restrict anyone’s copy.'],
  ['What if the website disappears?', 'The standalone HTML export includes the learning content and its game runtime. You can retain and share that file independently. Matching encrypted files and a release backup also support recovery without the website.'],
  ['Is SUNSET live?', 'SUNSET is currently an interactive prototype. Financial actions in the rehearsal use simulated NEAR and do not move real funds. A separate read-only view can inspect an actual reviewed testnet contract once configured.'],
];

export default function Landing(){
  return <div className="landing">
    <a className="lp-skip" href="#content">Skip to content</a>
    <header className="lp-header lp-container">
      <a className="lp-brand" href="/" aria-label="SUNSET home"><Sun/><span>SUNSET</span></a>
      <nav className="lp-nav" aria-label="Website navigation"><a href="#commons">The commons</a><a href="#how-it-works">How it works</a><a href="#for-creators">For creators</a><a href="#questions">Questions</a></nav>
      <a className="lp-button lp-button-dark lp-nav-cta" href="/app/">Open the app <Arrow diagonal/></a>
    </header>

    <main id="content">
      <section className="lp-hero lp-container" aria-labelledby="hero-title">
        <div className="lp-hero-copy">
          <div className="lp-eyebrow"><span className="lp-small-dot"/> THE COMMONS STARTS WITH US</div>
          <h1 id="hero-title">Good things<br/>belong to<br/><em>everyone.</em></h1>
          <p className="lp-hero-description">Help useful learning resources become free for everyone. Fund the beginning. Share what comes after.</p>
          <div className="lp-hero-actions"><a className="lp-button lp-button-orange" href="/app/?view=Discover">Explore the commons <Arrow/></a><a className="lp-play-link" href="/try-lantern-trail.html"><span><Symbol name="play"/></span>Try a free adventure</a></div>
          <p className="lp-prototype"><span/> Interactive prototype · Simulated NEAR · No wallet needed to learn</p>
        </div>
        <div className="lp-hero-visual">
          <div className="lp-visual-caption"><span>01 / A SHARED FUTURE</span><span>MADE TO OUTLAST US <Arrow diagonal/></span></div>
          <Image className="lp-hero-image" src="/images/sunset-commons-hero.webp" alt="An open book and steppingstone path leading toward a warm setting sun" width={1254} height={1254} priority sizes="(max-width: 760px) 100vw, 52vw"/>
          <div className="lp-hero-note"><span className="lp-note-icon"><Symbol name="leaf"/></span><div><strong>A little support. A lasting resource.</strong><span>Made to be kept, used and shared.</span></div></div>
          <span className="lp-visual-coordinate">A GOOD ENDING IS A NEW BEGINNING.</span>
        </div>
      </section>

      <div className="lp-principles lp-container" aria-label="The SUNSET idea">
        <span className="lp-principles-label">SMALL BEGINNINGS.<br/>LASTING POSSIBILITIES.</span>
        <div><Symbol name="people"/><span>Fund it <strong>together.</strong></span></div>
        <div><Symbol name="release"/><span>Release it <strong>openly.</strong></span></div>
        <div><Symbol name="offline"/><span>Keep it <strong>independently.</strong></span></div>
      </div>

      <section id="commons" className="lp-commons lp-container" aria-labelledby="commons-title">
        <div className="lp-section-heading"><div><span className="lp-eyebrow">A FEW GOOD THINGS TO GET BEHIND</span><h2 id="commons-title">Small resources.<br/><em>Wide-open possibilities.</em></h2></div><div className="lp-section-aside"><p>Start with a little learning adventure.<br/>See how the whole story works.</p><a className="lp-text-link" href="/app/?view=Discover">Explore all demo resources <Arrow/></a></div></div>
        <div className="lp-resource-grid">{resources.map(r=><a className="lp-resource" key={r.id} href={`/app/?view=Discover&campaign=${r.id}`}><div className={`lp-resource-art lp-resource-art-${r.variant}`}><Cover variant={r.variant}/><span className="lp-cover-label">THE LEARNING COLLECTION / 0{r.variant+1}</span><span className="lp-resource-cta" aria-hidden="true"><Arrow diagonal/></span></div><div className="lp-resource-content"><span className={`lp-status lp-status-${r.tone}`}><span/>{r.status}</span><h3>{r.name}</h3><p>{r.description}</p><div className="lp-resource-foot"><span>{r.footer}</span><Arrow/></div></div></a>)}</div>
        <p className="lp-sample-caption">Three demonstration scenarios using one original maths sample. Campaign amounts are illustrative, not live funding.</p>
      </section>

      <section id="how-it-works" className="lp-how" aria-labelledby="how-title"><div className="lp-container">
        <div className="lp-section-heading"><div><span className="lp-eyebrow">A DIFFERENT KIND OF FINISH LINE</span><h2 id="how-title">Support once.<br/><em>Open a new chapter.</em></h2></div><p className="lp-how-intro">A clear agreement brings a community together.<br/>The outcome belongs in everyone’s hands.</p></div>
        <div className="lp-steps"><article><div className="lp-step-top"><span>01</span><Symbol name="people"/></div><h3>Give it a beginning.</h3><p>A creator prepares a resource. An independent reviewer checks the exact pack and its public-release agreement.</p></article><article><div className="lp-step-top"><span>02</span><Symbol name="release"/></div><h3>Bring it into the open.</h3><p>Sponsors pool support up to a fixed goal. A timely release credits the creator. Missed conditions allow contributor refunds.</p></article><article><div className="lp-step-top"><span>03</span><Symbol name="offline"/></div><h3>Let it live beyond us.</h3><p>The released pack can be verified, downloaded and used independently. A new steward can take over its recovery mirror.</p></article></div>
        <div className="lp-how-footer"><span><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m12 3 8 4v5c0 5-8 9-8 9s-8-4-8-9V7l8-4Z"/><path d="m8 12 3 3 5-6"/></svg>Clear terms. Fixed beneficiaries. A way to recover.</span><a className="lp-text-link" href="/app/?view=How%20it%20works">Walk through the mechanism <Arrow/></a></div>
      </div></section>

      <section id="for-creators" className="lp-creators lp-container" aria-labelledby="creator-title"><div className="lp-creator-art" aria-hidden="true"><div className="lp-paper lp-paper-back"><Sun/></div><div className="lp-paper lp-paper-front"><span>AN IDEA WORTH SHARING</span><svg viewBox="0 0 240 160"><circle cx="120" cy="81" r="59" fill="#dc5938"/><path d="M0 114 60 68l83 83 60-71 37 29v51H0Z" fill="#5c725a"/><path d="M0 145 79 119l87 41H0Z" fill="#304c3c"/><path d="M127 160q-24-26 0-40t8-28" stroke="#ead8b9" strokeWidth="9" fill="none"/></svg><strong>Your next<br/>good thing.</strong><span className="lp-paper-caption">A PUBLIC FUTURE STARTS SOMEWHERE.</span></div><span className="lp-creator-asterisk">✳</span></div><div className="lp-creator-copy"><span className="lp-eyebrow">FOR THE PEOPLE WHO MAKE THINGS</span><h2 id="creator-title">Make something<br/>worth <em>passing on.</em></h2><p>You bring the useful idea. SUNSET gives it a clear path from community support to public release.</p><ul><li><span>01</span>Set a finite funding goal.</li><li><span>02</span>Commit to the exact resource and license.</li><li><span>03</span>Invite review. Keep an independent backup.</li></ul><a className="lp-button lp-button-dark" href="/app/?view=Creator%20studio">Prepare your first resource <Arrow diagonal/></a><p className="lp-small-copy">Start with the sample or your own validated learning pack.</p></div></section>

      <section className="lp-stewardship" aria-labelledby="steward-title"><div className="lp-container lp-stewardship-inner"><div className="lp-steward-symbol" aria-hidden="true"><Sun/><span>A ROLE.<br/>NOT A PAYWALL.</span></div><div><span className="lp-eyebrow">GOOD STEWARDSHIP, BUILT IN</span><h2 id="steward-title">The home can change.<br/><em>The resource stays open.</em></h2><p>A transferable stewardship NFT gives its holder one practical responsibility: maintain the preferred recovery mirror. It never controls the public’s copies or changes who gets paid.</p><a className="lp-text-link" href="/app/?view=Stewardship">Explore stewardship <Arrow/></a></div></div></section>

      <section id="questions" className="lp-faq lp-container" aria-labelledby="faq-title"><div><span className="lp-eyebrow">A LITTLE MORE CLARITY</span><h2 id="faq-title">Good questions.<br/><em>Clear answers.</em></h2><p>Curious about the details?<br/>The rehearsal makes them tangible.</p><a className="lp-text-link" href="/app/?view=How%20it%20works">See the complete flow <Arrow/></a></div><div className="lp-faq-list">{faqs.map(([question,answer])=><details key={question}><summary>{question}<span className="lp-faq-plus" aria-hidden="true"/></summary><p>{answer}</p></details>)}</div></section>

      <section className="lp-final lp-container" aria-labelledby="final-title"><div className="lp-final-top"><span className="lp-eyebrow">SOME THINGS GET BETTER WHEN THEY’RE SHARED.</span><Sun/></div><div className="lp-final-row"><h2 id="final-title">Let’s make room<br/>for <em>everyone.</em></h2><div><p>A little contribution can be<br/>the start of a much longer story.</p><a className="lp-button lp-button-dark" href="/app/?view=Discover">Explore the rehearsal <Arrow diagonal/></a></div></div></section>
    </main>

    <footer className="lp-footer lp-container"><div className="lp-footer-top"><a className="lp-brand" href="/" aria-label="SUNSET home"><Sun/><span>SUNSET</span></a><p>Good things shouldn’t have an expiry date.</p><a href="#content" className="lp-text-link">Back to the beginning <Arrow diagonal/></a></div><div className="lp-footer-bottom"><span>AN OPEN RESOURCE EXPERIMENT · NOVEMBER 2026</span><div><a href="/app/?view=Discover">Explore</a><a href="/try-lantern-trail.html">Free sample</a><a href="/app/?view=How%20it%20works">How it works</a></div><span>BUILT FOR NEAR · TESTNET PROTOTYPE</span></div></footer>
  </div>;
}
