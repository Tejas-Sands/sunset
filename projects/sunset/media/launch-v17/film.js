/* Original SUNSET material worlds. All motion is deterministic and seekable. */
(() => {
  'use strict';
  const W=1920,H=1080,DURATION=29.5;
  const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
  const svg=(body,box='0 0 1000 1000',cls='')=>`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box}" class="${cls}" aria-hidden="true">${body}</svg>`;
  const check=svg('<path d="M110 480 370 720 860 180" fill="none" stroke="currentColor" stroke-width="100" stroke-linecap="round" stroke-linejoin="round"/>');
  const plant=svg('<path d="M490 940 C460 700 580 480 510 140" fill="none" stroke="#173b2d" stroke-width="22"/><path d="M490 650C260 650 100 480 140 300C380 290 490 450 490 650ZM520 490C730 490 920 270 870 130C650 130 530 300 520 490ZM490 860C700 850 850 690 810 530C590 530 490 700 490 860Z" fill="#173b2d"/><circle cx="510" cy="110" r="65" fill="#d25632"/>');
  const mechanism=svg('<g fill="none" stroke="#183b2e" stroke-width="22"><circle cx="420" cy="420" r="280"/><circle cx="420" cy="420" r="110"/><path d="M420 0v140M420 700v140M0 420h140M700 420h140M120 120l110 110M610 610l110 110M120 720l110-110M610 230l110-110M450 700v190h430V560H700"/></g><path d="m730 610 145-80-145-80" fill="none" stroke="#c14e30" stroke-width="45" stroke-linecap="round"/>');
  const wave=svg('<path d="M-90 670Q70 310 230 670T550 670T870 670T1190 670" fill="none" stroke="#173b2d" stroke-width="45"/><path d="M-90 800Q70 440 230 800T550 800T870 800T1190 800" fill="none" stroke="#d25b34" stroke-width="25"/><circle cx="740" cy="210" r="160" fill="#173b2d"/><path d="M100 160h350M100 240h240M100 320h310" stroke="#173b2d" stroke-width="20"/>');
  const diagram=svg('<g fill="none" stroke="#173b2d" stroke-width="15"><path d="M100 820 510 120 920 820ZM210 640h600M315 460h390M405 300h210"/><circle cx="510" cy="120" r="56"/><circle cx="100" cy="820" r="56"/><circle cx="920" cy="820" r="56"/></g><path d="M70 180C70-30 460-30 460 70M860 170C1070 170 1070 560 950 560" fill="none" stroke="#c65331" stroke-width="25"/>');
  const keyPath='M130 55A105 105 0 1 0 130 265A105 105 0 0 0 130 55ZM130 115A45 45 0 1 1 130 205A45 45 0 0 1 130 115ZM230 125H650V225H575V185H510V245H445V185H230Z';
  const edition=(cls='')=>`<div class="edition ${cls}"><span class="ed-title" data-layout-ignore>FIELD<br>NOTES</span>${plant}<span class="ed-foot" data-layout-ignore>A PREPARED EDITION · 01</span></div>`;
  const paths=(s)=>s.match(/<svg[^>]*>([\s\S]*)<\/svg>/)[1];
  const art=[plant,mechanism,wave,diagram];
  const scene=(id,content)=>`<section id="${id}" class="scene" aria-hidden="true">${content}</section>`;
  $('#worlds').innerHTML=
  scene('opening',`<div class="camera opening-camera"><div class="intro-glow"></div><div class="intro-sun-window"><div class="intro-sun"></div></div>${svg('<path d="M330 570H1590"/>','0 0 1920 1080','intro-horizon')}${svg('<path d="M700 608Q960 625 1220 608M810 640Q960 650 1110 640"/>','0 0 1920 1080','intro-ripple')}<h1 class="intro-wordmark">SUNSET</h1></div><div class="portal-hands"><img src="assets/hands.png" alt="">${svg('<path class="ribbon" d="M-100 700C100 20 1650 1150 2100 200"/>','0 0 1920 1080','fill')}</div>`)+
  scene('taught',`<div class="camera taught-camera"><div class="paper lesson-paper tear"></div><img class="lesson-hands" src="assets/hands.png" alt="">${svg('<circle cx="580" cy="630" r="310"/><path d="M160 920 580 190 1000 920ZM270 730H895M385 530H780M480 350H680M-100 230C170 70 540 120 710 30M870 170c220 0 240 300 140 380"/><path class="accent" d="M120 1060C450 800 140 690 600 710S850 1050 1310 520"/>','0 0 1370 1240','stroke-art lesson-diagram')}<div class="lesson-mark"></div><div class="lesson-strip tear"></div></div><h2 class="caption lesson-copy">Someone<br><em>taught it.</em></h2>`)+
  scene('built',`<div class="camera built-camera"><div class="build-grid"></div><div class="kit-plate tear">${svg('<path d="M150 730 480 210 840 730ZM250 575H730M355 415H620M790 170H1040V420H790ZM910 170V40M1040 290H1170M910 420V560M790 290H660"/><circle cx="480" cy="210" r="55"/><circle cx="150" cy="730" r="55"/><circle cx="840" cy="730" r="55"/><path class="warm" d="M50 95C700-50 1240 600 1040 900M1000 800 1040 900 1140 850"/>','0 0 1280 1000','kit-lines')}</div><div class="bolt one"></div><div class="bolt two"></div><div class="kit-tab tear"></div></div><h2 class="caption built-copy">Built it.</h2>`)+
  scene('wrote',`<div class="camera wrote-camera"><div class="workroom-bg"></div><div class="writing-sheet tear"></div>${svg('<path d="M10 110H650M10 180H780M10 250H680M10 430H900M10 500H780M10 570H840"/><path class="warm" d="M20 350C170 260 450 260 540 350S150 480 20 350"/>','0 0 1170 600','writing-lines')}<img class="writing-hands" src="assets/hands.png" alt="">${svg('<path d="M-200 400C200-150 1350 850 1900 200S2500 450 2800 0"/>','0 0 2550 700','ink-loop')}</div><h2 class="caption wrote-copy">Wrote it down.</h2>`)+
  scene('ideas',`<div class="idea-room"></div><div class="camera idea-camera"><div class="idea-wall"></div><div class="idea-portrait paper tear"><div class="portrait p0"></div></div>${Array.from({length:6},(_,i)=>`<div class="idea-print i${i} tear"><span class="index">OPEN IDEAS / ${String(i+1).padStart(2,'0')}</span>${art[i%4]}<span class="print-name">${['GROW','MAKE','PASS<br>IT ON','LEARN','BUILD','MORE'][i]}</span></div>`).join('')}${svg('<path d="M-100 1000C1100 1550 110 40 1110 220S1850 1280 2350 500 3300 1000 3900 100"/>','0 0 3700 1400','idea-ribbon')}<div class="idea-front-strip tear"></div>${edition('idea-edition')}</div><h2 class="caption ideas-copy">Help them<br><em>make more.</em></h2>`)+
  scene('funding',`<div class="funding-table"></div><div class="camera funding-camera"><div class="funding-plane">${edition('funding-edition')}${Array.from({length:6},(_,i)=>`<div class="ticket t${i}"><span class="ticket-mark" data-layout-ignore>${i%2?'FOR ALL':'RELEASE'}</span><span class="ticket-sub" data-layout-ignore>SUPPORT / PUBLIC EDITION</span><i class="hole"></i></div>`).join('')}<div class="fund-strip">${'<b></b>'.repeat(6)}</div><div class="fund-stop"></div></div></div><h2 class="caption funding-copy">Sponsor a<br><em>public release.</em></h2>`)+
  scene('custody',`<div class="custody-dots dotfield"></div><div class="camera custody-camera"><div class="sleeve tear"><div class="sleeve-top"></div><div class="sleeve-sign" data-layout-ignore>PUBLIC<br>RELEASE</div><div class="deposit d0">SPONSOR<br>DEPOSIT</div><div class="deposit d1">SPONSOR<br>DEPOSIT</div><div class="deposit d2">SPONSOR<br>DEPOSIT</div><div class="sleeve-bottom"></div><div class="sleeve-binding"></div><div class="sleeve-rule"></div></div><div class="custody-stop"></div>${svg(`<path fill-rule="evenodd" d="${keyPath}"/>`,'0 0 700 320','binding-key')}</div><h2 class="caption custody-copy">NEAR holds<br><em>the funds.</em></h2>`)+
  scene('release',`<div class="release-grid"></div><div class="camera release-camera"><div class="release-target"><span class="seal-text">TARGET COMPLETE</span>${check}</div>${svg(`<path fill-rule="evenodd" d="${keyPath}"/>`,'0 0 700 320','release-key')}<div class="deadline"><i class="clock"></i>BEFORE DEADLINE</div><div class="public-page"><div class="page-inside">${wave}<span class="public-stamp">PUBLIC</span></div><div class="page-cover">${plant}<span class="cover-name" data-layout-ignore>FIELD NOTES</span></div></div></div><h2 class="caption release-copy ontime-copy">On-time release.</h2><div class="payment-world"><div class="credit-card"><div class="credit-card-label">Creator credit</div><div class="credit-card-symbol">${svg('<path d="M28 105H142M45 80H125M60 55H110" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><circle cx="85" cy="160" r="27" fill="none" stroke="currentColor" stroke-width="7"/>','0 0 170 200')}</div><div class="credit-card-rule"></div><div class="credit-state state-ready">Ready to claim</div><div class="credit-state state-claiming">Claiming…</div><div class="credit-state state-confirmed">Confirmed</div><div class="credit-state state-paid">Paid</div><div class="credit-action"><span>Claim payment</span>${svg('<path d="M25 50H125M95 20 125 50 95 80" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>','0 0 150 100')}</div><div class="credit-progress"><i></i></div><div class="credit-confirm">${check}</div>${svg('<path d="M170 570C120 570 80 535 80 490V460" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round"/>','0 0 800 650','credit-gesture')}</div></div><h2 class="caption release-copy claim-copy">Creator claims<br><em>payment.</em></h2><div class="reader-wipe"></div>`)+
  scene('reader',`<div class="reader-edge tear"></div><h2 class="caption reader-copy">Use it. Share it. <em>Offline.</em></h2><div class="reader-frame"><img id="reader-unchecked" class="reader-shot" src="assets/unchecked.png" alt="Real downloaded handbook, unchecked"><img id="reader-checked" class="reader-shot" src="assets/checked.png" alt="Real downloaded handbook, saved checked state"></div><div class="reader-label">Local handbook example · browser offline</div>`)+
  scene('next',`<div class="next-room"></div><div class="camera next-camera"><div class="fresh-sheet tear">${svg('<path class="fresh-ink" d="M30 730C180 400 220 630 300 450S450 120 590 310 850 590 930 220M110 780H930M500 550C180 600 80 210 300 100S700 150 620 420 330 820 130 930"/>','0 0 980 1000')}</div><img class="next-hands" src="assets/hands.png" alt=""><div class="next-portrait paper tear"><div class="portrait p2"></div></div><div class="new-world">${svg('<g fill="none" stroke="#e9b93a" stroke-width="12"><circle cx="900" cy="620" r="420"/><circle cx="900" cy="620" r="320"/><path d="M-100 350C300 650 500-100 950 250S1500 850 1900 300M-100 900C300 1200 500 450 950 800S1500 1400 1900 850"/></g><g fill="#d35e38"><circle cx="500" cy="530" r="90"/><circle cx="1330" cy="280" r="150"/><circle cx="1150" cy="1100" r="140"/></g>','0 0 1800 1320')}</div>${[0,1,2].map((i)=>`<div class="world-sheet w${i} tear">${art[(i+1)%4]}</div>`).join('')}${svg('<path d="M-100 750C700 1250 450-100 1300 180S1800 1050 2440 480 3400 950 4400 180"/>','0 0 4300 1100','next-ribbon')}</div><div class="next-copy-back"></div><h2 class="caption next-copy">Make the next<br><em>free thing possible.</em></h2>`)+
  scene('minimal',`<div class="minimal-guides"></div><div class="minimal-window"><div class="minimal-content"><div class="mini-sheet">${plant}</div>${svg('<path d="M-100 650C150-200 1200 1050 1400 50"/>','0 0 1300 700','mini-ink')}</div></div><div class="minimal-point"></div><div class="minimal-phrase free-phrase"><span class="bracket">[</span><span class="word">FREE TO <em>USE</em></span><span class="bracket">]</span></div><div class="minimal-phrase paid-phrase"><span class="bracket">[</span><span class="word">CREATOR <em>PAID</em></span><span class="bracket">]</span></div>`)+
  scene('closing',`<div class="close-point"></div>${svg('<path d="M550 40V220M165 205 290 330M935 205 810 330M10 590H190M910 590H1090M180 970 300 850M920 970 800 850"/>','0 0 1100 1100','closing-rays')}<div class="close-sun"></div><div class="horizon"></div><div class="closing-paper tear"></div>${svg('<path d="M180 460C250 300 470 280 600 340S1100 560 1450 340M400 600C700 850 1200 740 1450 510"/>','0 0 1720 870','close-ink')}<div class="closing-logo">SUNSET</div><div class="closing-tagline">Support once. Share forever.</div>`)+
  '<div class="truth-label" id="finance-truth">NEAR testnet · illustration</div>';

  // Solid per-line paper/ink protects every editorial sentence while material worlds travel behind it.
  $$('.caption').forEach(copy=>{copy.innerHTML=copy.innerHTML.split('<br>').map(line=>`<span class="copy-line">${line}</span>`).join('')});

  // The same photographic hand cutout crosses the portal without inheriting the new chalk camera.
  $('#taught').insertBefore($('.lesson-hands'),$('.lesson-copy'));
  const tl=gsap.timeline({paused:true,defaults:{ease:'power2.inOut'}});
  window.__timelines=window.__timelines||{};
  const bounds=[['opening',0,1.8],['taught',1.8,2.75],['built',2.75,3.7],['wrote',3.7,4.8],['ideas',4.8,7],['funding',7,9.2],['custody',9.2,12],['release',12,16.4],['reader',16.4,19.1],['next',19.1,23],['minimal',23,26],['closing',26,29.5]];
  gsap.set('.scene',{autoAlpha:0});
  bounds.forEach(([id,start,end])=>{tl.set('#'+id,{autoAlpha:1},start);if(end<DURATION)tl.set('#'+id,{autoAlpha:0},end)});
  tl.set('#finance-truth',{autoAlpha:0},0).set('#finance-truth',{autoAlpha:1},7).set('#finance-truth',{autoAlpha:0},16.4);
  tl.set('#paper-grain',{opacity:0},13.4).set('#paper-grain',{opacity:.14},19.1);
  const draw=(selector,start,duration,stagger=0)=>{
    $$(selector).forEach((p,i)=>{const len=p.getTotalLength();gsap.set(p,{strokeDasharray:len,strokeDashoffset:len});tl.to(p,{strokeDashoffset:0,duration,ease:'power1.inOut'},start+i*stagger)});
  };
  const reveal=(selector,start,duration=.3,props={})=>tl.fromTo(selector,{opacity:0,y:55,rotation:-5,...props},{opacity:1,y:0,rotation:0,duration,ease:'power3.out'},start);

  // 0–1.8: an actual warm sun rises to a drawn horizon; the same disc opens into the maker's hands.
  tl.fromTo('.intro-sun',{y:190,scale:.94},{y:0,scale:1,duration:.82,ease:'power3.out'},0);
  tl.fromTo('.intro-glow',{opacity:.25,scale:.9},{opacity:1,scale:1,duration:.95,ease:'sine.out'},0);
  draw('.intro-horizon path',.04,.78);draw('.intro-ripple path',.34,.66,.06);
  tl.fromTo('.intro-wordmark',{opacity:0,y:24},{opacity:1,y:0,duration:.3,ease:'power2.out'},.48);
  tl.to('.intro-sun',{y:4,duration:.32,ease:'sine.inOut'},.9);
  tl.to('.intro-wordmark',{opacity:0,y:20,duration:.24,ease:'power2.in'},1.37);
  tl.to('.intro-horizon,.intro-ripple',{opacity:0,duration:.28},1.4);
  tl.to('.portal-hands',{clipPath:'circle(1850px at 50% 53%)',duration:.4,ease:'power3.in'},1.4);
  tl.fromTo('.portal-hands img',{scale:1.35,x:-70,y:-65},{scale:1,x:0,y:0,duration:.4,ease:'power2.out'},1.4);

  // 1.8–4.8: three materials hand the same line to one another.
  tl.fromTo('.taught-camera',{scale:1.55,x:-250,y:130,rotation:-10},{scale:1,x:0,y:0,rotation:0,duration:.78,ease:'power3.out'},1.8);
  tl.fromTo('.lesson-hands',{x:0,y:0,scale:1,rotation:8},{x:540,y:-96.6666666667,scale:1280/2080,rotation:-12,duration:.5,ease:'power3.out'},1.95);
  reveal('.lesson-copy',1.82,.25);draw('.lesson-diagram path',1.8,.5,.025);draw('.lesson-diagram circle',1.85,.45);
  tl.fromTo('.lesson-strip',{x:-2300},{x:0,duration:.45,ease:'power4.out'},2.03);
  tl.to('.lesson-strip',{y:-1300,rotation:22,scaleY:10,duration:.25,ease:'power3.in'},2.5);
  tl.to('.lesson-mark',{rotation:25,scale:1.15,duration:.55},2.03);
  tl.fromTo('.built-camera',{x:620,y:-120,rotation:19,scale:1.3},{x:0,y:0,rotation:0,scale:1,duration:.55,ease:'power3.out'},2.75);
  tl.fromTo('.kit-plate',{rotationY:-40,rotationZ:-20,x:250},{rotationY:0,rotationZ:0,x:0,duration:.62},2.75);
  tl.fromTo('.bolt.one',{x:-500,y:650,rotation:-180},{x:0,y:0,rotation:0,duration:.45},2.8);
  tl.fromTo('.bolt.two',{x:500,y:-500,rotation:140},{x:0,y:0,rotation:0,duration:.45},2.91);
  tl.fromTo('.kit-tab',{x:700,y:-500},{x:0,y:0,duration:.48},2.94);
  reveal('.built-copy',2.79,.24);draw('.kit-lines path',2.75,.5,.02);
  tl.to('.built-camera',{scale:1.9,x:-550,y:250,rotation:-8,duration:.28,ease:'power3.in'},3.42);
  tl.fromTo('.wrote-camera',{scale:1.8,x:-350,y:-150,rotation:12},{scale:1,x:0,y:0,rotation:0,duration:.6,ease:'power3.out'},3.7);
  tl.fromTo('.writing-hands',{x:350,y:190,rotation:15},{x:0,y:0,rotation:0,duration:.65},3.7);
  tl.fromTo('.writing-sheet',{x:-500,rotationZ:-20},{x:0,rotationZ:0,duration:.6},3.7);
  reveal('.wrote-copy',3.76,.26);draw('.writing-lines path',3.7,.45,.045);draw('.ink-loop path',4.1,.65);
  tl.to('.ink-loop',{y:-680,scale:1.7,rotation:15,duration:.35,ease:'power3.in'},4.45);
  tl.to('.wrote-camera',{scale:1.35,x:190,y:-120,duration:.45,ease:'power2.in'},4.35);

  // 4.8–7: a face macro becomes a populated maker's wall; prepared work breaks forward.
  tl.fromTo('.idea-camera',{scale:2.35,x:-630,y:110,rotation:-8},{scale:1,x:0,y:0,rotation:0,duration:.66,ease:'power3.out'},4.8);
  tl.to('.idea-camera',{x:-1250,y:-10,scale:.96,rotation:0,duration:1.52,ease:'power2.inOut'},5.47);
  tl.fromTo('.idea-portrait',{rotationY:25,rotationZ:8,scale:1.15,z:50},{rotationY:-7,rotationZ:0,scale:1,z:50,duration:1.15},4.8);
  $$('.idea-print').forEach((p,i)=>tl.fromTo(p,{x:(i%2?1:-1)*450,y:i%2?600:-500,rotationY:i%2?40:-40,scale:.65},{x:0,y:0,rotationY:0,scale:1,duration:.7,ease:'power3.out'},4.95+i*.12));
  reveal('.ideas-copy',4.85,.28);tl.to('.ideas-copy',{x:30,y:18,duration:1.6,ease:'sine.inOut'},5.15);
  draw('.idea-ribbon path',4.8,1.55);
  tl.fromTo('.idea-front-strip',{x:850,y:500,rotationZ:25},{x:0,y:0,rotationZ:0,duration:.8},5.45);
  tl.to('.idea-front-strip',{x:-1500,y:-700,rotationZ:-20,duration:.55,ease:'power3.in'},6.38);
  tl.fromTo('.idea-edition',{x:700,y:400,rotationY:65,rotationZ:25,scale:.45},{x:0,y:0,rotationY:-8,rotationZ:0,scale:1,duration:.92,ease:'power3.out'},6.02);
  tl.to('.ideas-copy',{x:-50,y:-85,opacity:0,duration:.3,ease:'power3.in'},6.7);

  // 7–9.2: capped support arrives from separate depths; follow the last perforation.
  tl.fromTo('.funding-camera',{scale:1.18,rotation:8,x:-130,y:80},{scale:1,rotation:0,x:0,y:0,duration:.62,ease:'power3.out'},7);
  tl.fromTo('.funding-plane',{rotationX:24,rotationY:-8,rotationZ:-13},{rotationX:8,rotationY:5,rotationZ:-7,duration:1.7,ease:'sine.inOut'},7);
  tl.fromTo('.funding-edition',{scale:.74,y:180,rotationY:45},{scale:1,y:0,rotationY:0,duration:.7,ease:'power3.out'},7);
  $$('.ticket').forEach((ticket,i)=>{const sign=i%2?1:-1;tl.fromTo(ticket,{x:sign*(1200+i*60),y:i<3?-800:700,z:450+i*55,rotationZ:sign*30,rotationY:sign*45},{x:0,y:0,z:i===5?160:20+i*12,rotationZ:0,rotationY:0,duration:.73,ease:'power3.out'},7.08+i*.14)});
  tl.fromTo('.fund-strip b',{scaleY:0,transformOrigin:'50% 100%'},{scaleY:1,duration:.22,stagger:.15,ease:'back.out(1.7)'},7.43);
  reveal('.funding-copy',7.04,.3);
  tl.to('.ticket.t0',{x:-80,y:40,rotationZ:-5,duration:1.2,ease:'sine.inOut'},7.78);
  tl.to('.ticket.t3',{x:60,y:-70,rotationZ:7,duration:.95,ease:'sine.inOut'},8.02);
  tl.to('.funding-copy',{x:-120,y:-100,opacity:0,duration:.3,ease:'power3.in'},8.65);
  tl.to('.funding-camera',{transformOrigin:'1755px 537px',scale:12,x:-790,y:3,rotation:13,duration:.48,ease:'expo.in'},8.72);

  // 9.2–12: the ticket aperture is the sleeve's printed green; deposits seat at a stop.
  tl.fromTo('.custody-camera',{scale:2.45,x:-400,y:250,rotation:-18},{scale:.95,x:0,y:0,rotation:0,duration:.75,ease:'power3.out'},9.2);
  tl.fromTo('.sleeve',{rotationX:25,rotationY:-28,rotationZ:-17},{rotationX:0,rotationY:10,rotationZ:-7,duration:1.55,ease:'sine.inOut'},9.2);
  tl.fromTo('.custody-dots',{x:-150,y:80,rotation:5},{x:0,y:0,rotation:-5,duration:2.8,ease:'none'},9.2);
  $$('.deposit').forEach((deposit,i)=>tl.fromTo(deposit,{x:-600+i*60,y:-650,z:220+i*50,rotationZ:-20+i*12},{x:0,y:260+i*10,z:0,rotationZ:i*3,duration:.72,ease:'power3.out'},9.48+i*.3));
  reveal('.custody-copy',9.32,.3);
  tl.fromTo('.sleeve-rule',{scaleY:0,transformOrigin:'50% 100%'},{scaleY:1,duration:.3,ease:'power3.out'},10.55);
  tl.fromTo('.custody-stop',{x:200,y:300,rotation:20},{x:0,y:0,rotation:0,duration:.5},10.3);
  tl.to('.custody-camera',{scale:1.34,x:-340,y:-120,rotation:4,duration:1.08,ease:'power2.inOut'},10.9);
  tl.fromTo('.binding-key',{clipPath:'inset(0 100% 0 0)',rotationZ:-15,x:-270,y:30},{clipPath:'inset(0 0% 0 0)',rotationZ:0,x:0,y:0,duration:.65,ease:'power2.out'},11.15);
  tl.to('.sleeve-binding',{scaleX:3,x:70,rotationZ:90,duration:.6,ease:'power2.inOut'},11.2);
  tl.to('.custody-copy',{opacity:0,x:-70,y:-80,duration:.3,ease:'power3.in'},11.7);
  tl.to('.binding-key',{scale:2.7,x:-540,y:-50,duration:.33,ease:'power3.in'},11.67);

  // 12–16.4: a single camera passage preserves each separate causal state.
  $('.release-camera').insertAdjacentHTML('afterbegin',svg(`<path fill-rule="evenodd" d="${keyPath}" fill="#173f2e"/>`,'0 0 700 320','key-slot'));
  $('.release-camera').insertAdjacentHTML('beforeend','<div class="matched-label">MATCHED KEY</div>');
  tl.fromTo('.release-camera',{x:250,y:0,scale:1.08,rotation:-5},{x:0,y:0,scale:1,rotation:0,duration:.55,ease:'power3.out'},12);
  tl.fromTo('.release-key',{x:-640,y:-80,rotationZ:-20,scale:1.25},{x:0,y:0,rotationZ:0,scale:1,duration:.48,ease:'power3.out'},12);
  tl.fromTo('.release-target',{rotation:-28,scale:.7},{rotation:0,scale:1,duration:.5,ease:'back.out(1.25)'},12);
  tl.fromTo('.deadline',{opacity:0,y:70},{opacity:1,y:0,duration:.3},12.12);
  tl.fromTo('.matched-label',{opacity:0,scale:1.3},{opacity:1,scale:1,duration:.17,ease:'power2.out'},12.45);
  reveal('.ontime-copy',12.02,.25);
  tl.fromTo('.page-cover',{rotationY:0},{rotationY:-154,duration:.72,ease:'power3.inOut'},12.6);
  tl.to('.release-camera',{x:-640,y:25,scale:1.02,rotation:-3,duration:.85,ease:'power2.inOut'},12.6);
  tl.fromTo('.public-page',{rotationZ:14,y:140},{rotationZ:0,y:0,duration:.65,ease:'power3.out'},12.6);
  tl.fromTo('.public-stamp',{scale:1.7,opacity:0,rotation:-20},{scale:1,opacity:1,rotation:0,duration:.21,ease:'power3.out'},13.05);
  // One front-facing symbolic credit card separates release credit from the deliberate later claim.
  tl.set('.release-camera',{autoAlpha:0},13.4);
  tl.set('.payment-world,.credit-state,.credit-progress,.credit-confirm,.credit-gesture,.claim-copy,.reader-wipe',{autoAlpha:0},0);
  tl.set('.ontime-copy',{autoAlpha:0},13.4).set('.claim-copy,.payment-world,.state-ready',{autoAlpha:1},13.4);
  tl.fromTo('.claim-copy',{y:24,opacity:0},{y:0,opacity:1,duration:.22,ease:'power2.out'},13.4);
  tl.fromTo('.credit-card',{y:30,scale:.985},{y:0,scale:1,duration:.25,ease:'power2.out'},13.4);
  tl.set('.credit-gesture',{autoAlpha:1},14.08);draw('.credit-gesture path',14.08,.22);
  tl.to('.credit-action',{scale:.975,duration:.09,ease:'power2.in'},14.21);
  tl.to('.credit-action',{scale:1,duration:.13,ease:'power2.out'},14.3);
  tl.set('.state-ready',{autoAlpha:0},14.3).set('.state-claiming,.credit-progress',{autoAlpha:1},14.3);
  tl.fromTo('.state-claiming',{y:12,opacity:0},{y:0,opacity:1,duration:.12,ease:'power2.out'},14.3);
  tl.to('.credit-action,.credit-gesture',{autoAlpha:0,duration:.15},14.3);
  tl.fromTo('.credit-progress i',{scaleX:0},{scaleX:1,duration:1.15,ease:'power1.inOut'},14.3);
  tl.set('.state-claiming,.credit-progress',{autoAlpha:0},15.45).set('.state-confirmed,.credit-confirm',{autoAlpha:1},15.45);
  tl.fromTo('.credit-confirm',{scale:.85,opacity:0},{scale:1,opacity:1,duration:.16,ease:'power2.out'},15.45);
  tl.to('.credit-card',{backgroundColor:'#e8eddf',duration:.25,ease:'power1.inOut'},15.45);
  tl.set('.state-confirmed',{autoAlpha:0},15.8).set('.state-paid',{autoAlpha:1},15.8);
  tl.fromTo('.state-paid',{y:10,opacity:0},{y:0,opacity:1,duration:.1,ease:'power2.out'},15.8);
  tl.fromTo('.reader-wipe',{autoAlpha:0,scale:.05,rotation:0},{autoAlpha:1,scale:4.2,rotation:0,duration:.1,ease:'power2.in'},16.3);

  // 16.4–19.1: unchanged native PNGs at their original capture times, pure editorial crop.
  tl.set('#reader-checked',{autoAlpha:0},0);
  tl.set('#reader-unchecked',{autoAlpha:0},17.8736603630008176).set('#reader-checked',{autoAlpha:1},17.8736603630008176);
  tl.fromTo('.reader-shot',{scale:1.12,transformOrigin:'1071px 1020px'},{scale:1.12,duration:1.46,ease:'none'},16.4);
  tl.to('.reader-shot',{scale:1,duration:.65,ease:'power2.inOut'},17.91);
  tl.fromTo('.reader-edge',{x:-140,rotation:-10},{x:0,rotation:0,duration:.4},16.4);
  tl.fromTo('.reader-copy',{y:20,opacity:0},{y:0,opacity:1,duration:.18,ease:'power2.out'},16.4);

  // 19.1–23: the paid maker starts again, and the page turns into an abundant world.
  tl.fromTo('.next-camera',{scale:1.28,x:100,y:-110,rotation:5},{scale:1,x:0,y:0,rotation:0,duration:.6,ease:'power3.out'},19.1);
  tl.fromTo('.fresh-sheet',{rotationZ:12,x:-330,y:450},{rotationZ:0,x:0,y:0,duration:.7,ease:'power3.out'},19.1);
  tl.fromTo('.next-hands',{x:-250,y:250,rotationZ:-20},{x:0,y:0,rotationZ:0,duration:.7,ease:'power3.out'},19.1);
  draw('.fresh-ink',19.15,1.1);
  reveal('.next-copy',19.19,.3);tl.fromTo('.next-copy-back',{scaleX:.7,x:-450},{scaleX:1,x:0,duration:.5,ease:'power3.out'},19.1);
  tl.to('.next-camera',{x:-910,y:0,scale:1.13,rotation:3,duration:1.2,ease:'power2.inOut'},19.9);
  tl.to('.next-hands',{x:440,y:-90,rotationZ:13,duration:1.3,ease:'sine.inOut'},19.8);
  tl.fromTo('.next-portrait',{rotationY:45,x:200,y:180},{rotationY:-12,x:0,y:0,duration:1.1,ease:'power3.out'},19.8);
  tl.to('.next-camera',{x:-2050,y:40,scale:1.1,rotation:-4,duration:1.75,ease:'power2.inOut'},21.1);
  tl.fromTo('.new-world svg',{rotation:12,scale:1.4},{rotation:-5,scale:1,duration:3.4,ease:'sine.inOut'},19.5);
  $$('.world-sheet').forEach((p,i)=>tl.fromTo(p,{y:700-i*300,x:300,rotationY:55,rotationZ:20-i*12,scale:.6},{x:0,y:0,rotationY:-6,rotationZ:0,scale:1,duration:1.1,ease:'power3.out'},20.1+i*.55));
  tl.to('.world-sheet.w0',{x:-110,y:-80,rotationZ:-10,duration:1.3,ease:'sine.inOut'},21.3);
  tl.to('.world-sheet.w1',{x:130,y:70,rotationZ:9,duration:1.2,ease:'sine.inOut'},21.6);
  draw('.next-ribbon path',19.1,3.5);
  tl.to('.next-ribbon',{x:-200,y:80,rotationZ:3,duration:3.4,ease:'sine.inOut'},19.2);
  tl.to('.next-copy,.next-copy-back',{opacity:0,y:-80,duration:.22,ease:'power3.in'},22.72);

  // 23–26: the single quiet punctuation; its contained ink remains independently alive.
  tl.set('.minimal-point,.minimal-phrase',{autoAlpha:0},0);
  tl.fromTo('.minimal-window',{scale:1.12},{scale:.88,duration:.65,ease:'power2.out'},23);
  tl.fromTo('.mini-sheet',{x:180,y:-120,rotationZ:30},{x:-80,y:70,rotationZ:0,duration:.65,ease:'sine.inOut'},23);
  draw('.mini-ink path',23,.65);tl.to('.mini-ink',{x:100,y:-60,duration:.65,ease:'none'},23);
  tl.set('.minimal-window,.minimal-guides',{autoAlpha:0},23.65).set('.minimal-point',{autoAlpha:1},23.65);
  tl.to('.minimal-point',{scale:.62,y:4,duration:.15,ease:'power2.out'},23.65);
  tl.set('.minimal-point',{autoAlpha:0},23.8).set('.free-phrase',{autoAlpha:1},23.8);
  tl.fromTo('.free-phrase .bracket',{x:i=>i?35:-35},{x:0,duration:.1,ease:'back.out(1.4)'},23.8);
  tl.fromTo('.free-phrase .word',{y:12,opacity:0},{y:0,opacity:1,duration:.1,ease:'power2.out'},23.8);
  tl.to('.free-phrase em',{color:'#162f26',duration:.1},23.9);
  tl.set('.free-phrase',{autoAlpha:0},25).set('.paid-phrase',{autoAlpha:1},25);
  tl.fromTo('.paid-phrase .bracket',{x:i=>i?-30:30},{x:0,duration:.12,ease:'back.out(1.2)'},25);
  tl.fromTo('.paid-phrase .word',{scaleX:1.15,y:8,opacity:0},{scaleX:1,y:0,opacity:1,duration:.12,ease:'power2.out'},25);
  tl.to('.paid-phrase em',{color:'#162f26',duration:.06},25.08);

  // 26–28: point -> warm disc -> cut-paper horizon -> clear mark; final hold is 1.5 s.
  $('.closing-logo').innerHTML='SUNSET'.split('').map((c,i)=>`<span class="closing-letter letter-${i}">${c}</span>`).join('');
  tl.fromTo('.close-point',{scale:.6},{scale:73,duration:.48,ease:'power3.in'},26);
  tl.to('.close-point',{autoAlpha:0,duration:.2},26.46);
  tl.fromTo('.close-sun',{scale:0,rotation:-50,y:120},{scale:1.3,rotation:0,y:0,duration:.64,ease:'power3.out'},26.38);
  tl.to('.close-sun',{scale:1,duration:.82,ease:'power2.inOut'},27.02);
  draw('.closing-rays path',26.45,.6,.025);
  tl.fromTo('.closing-rays',{rotation:-30,scale:.7},{rotation:12,scale:1.1,duration:1.3,ease:'power2.inOut'},26.4);
  tl.to('.closing-rays',{autoAlpha:0,scale:1.45,duration:.4,ease:'power3.in'},27.35);
  tl.fromTo('.horizon',{scaleX:0,transformOrigin:'50% 50%'},{scaleX:1,duration:.75,ease:'power3.inOut'},26.65);
  tl.fromTo('.closing-paper',{x:-1800,y:-220,rotation:-40,scaleY:1.8},{x:1700,y:100,rotation:20,scaleY:.3,duration:1.12,ease:'power3.inOut'},26.45);
  tl.fromTo('.closing-letter',{y:320,rotation:i=>i%2?20:-20,scaleY:1.3,opacity:0},{y:0,rotation:0,scaleY:1,opacity:1,duration:.64,stagger:.055,ease:'back.out(1.25)'},27.04);
  draw('.close-ink path',26.9,.55,.13);tl.to('.close-ink',{opacity:0,scale:1.5,y:-180,duration:.48,ease:'power3.in'},27.45);
  tl.fromTo('.closing-tagline',{opacity:0,y:35},{opacity:1,y:0,duration:.35,ease:'power3.out'},27.05);

  // One master clock drives every physical layer and the selective ink/smear canvas.
  const marker={time:0};tl.to(marker,{time:DURATION,duration:DURATION,ease:'none'},0);
  const fx=$('#ink-fx').getContext('2d');
  function drawFX(time){
    fx.clearRect(0,0,W,H);
    if(time<1.8||(time>=13.4&&time<19.1))return; // Genuine reader pixels receive no authored texture or smear.
    const cuts=[1.64,2.65,3.59,4.66,6.9,9.07,11.85,16.27,19.08,22.91,26.12];
    cuts.forEach((c,k)=>{const d=Math.abs(time-c);if(d>.095)return;const strength=1-d/.095;fx.save();fx.globalAlpha=.19*strength;fx.strokeStyle=k%2?'#f5eed8':'#18392e';fx.lineWidth=8+14*strength;for(let i=0;i<13;i++){const x=(i*183+k*73)%2100-100;fx.beginPath();fx.moveTo(x,-100);fx.lineTo(x-650,1200);fx.stroke()}fx.restore()});
    if(time>=4.8&&time<7){fx.save();fx.globalAlpha=.13;fx.strokeStyle='#efe3c7';fx.lineWidth=2;for(let i=0;i<13;i++){const x=(i*181+time*31)%2050;fx.beginPath();fx.moveTo(x,30);fx.lineTo(x+80,50);fx.stroke()}fx.restore()}
  }
  tl.eventCallback('onUpdate',()=>drawFX(tl.time()));
  window.__timelines.main=tl;
  const r=(id,from,to)=>({id,from,to});
  window.__sunsetV17={duration:DURATION,fps:30,frames:885,proofReadyThrough:29.5,sceneBoundaries:bounds.map(([id,start,end])=>({id,start,end})),readingWindows:[r('opening',.78,1.37),r('taught',2.08,2.54),r('built',3.03,3.43),r('wrote',4.02,4.51),r('ideas',5.15,6.65),r('funding',7.35,8.6),r('custody',9.7,11.6),r('ontime',12.3,13.4),r('claim',13.65,16.3),r('credit-ready',13.65,14.3),r('credit-claiming',14.42,15.45),r('credit-confirmed',15.45,15.8),r('credit-paid',15.9,16.3),r('reader',16.6,19.1),r('next',19.5,22.7),r('free',23.9,25),r('paid',25.12,26),r('closing',28,29.5)],financeEvents:{targetComplete:8.4,matchedKey:12.45,publicRelease:12.6,creatorCredit:13.4,withdrawal:14.3,claim:14.3,confirmation:15.45,paid:15.8,paidClearUntil:16.3},uiPlacements:n=>{const time=n>DURATION?n/30:n;const state=time<17.8736603630008176?'unchecked':'checked';const shot=$('#reader-'+state),image=shot.getBoundingClientRect(),clip=$('.reader-frame').getBoundingClientRect(),sx=image.width/1920,sy=image.height/1080;return {sourcePath:'.publication/sunset-launch-v15/capture/'+state+'.png',assetPath:'assets/'+state+'.png',sourceBounds:[(clip.left-image.left)/sx,(clip.top-image.top)/sy,(clip.right-image.left)/sx,(clip.bottom-image.top)/sy],destinationBounds:clip.toJSON(),pixelTransform:{scaleX:sx,scaleY:sy,translateX:image.left,translateY:image.top},actualInputAt:17.600145381000766,time,state:time<17.8736603630008176?'unchecked':'checked',sourceAt:time-16.4,speed:1,sourceROI:[630,600,1562,975],sourceDimensions:[1920,1080],screenshotBounds:shot.getBoundingClientRect().toJSON(),clipBounds:$('.reader-frame').getBoundingClientRect().toJSON(),sampleSwitch:17.8736603630008176,noReloadClaim:true}},seek:time=>tl.seek(time,false)};
  document.fonts.ready.then(()=>{tl.seek(0,false);window.__SUNSET_READY__=true;drawFX(0)});
})();
