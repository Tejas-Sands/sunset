'use client';
import {useEffect} from 'react';

// Reveals [data-reveal] blocks once as they enter the viewport. Content is only hidden after this
// script has started, so pages stay fully readable without JavaScript or with reduced motion.
export default function MotionReveal(){
  useEffect(()=>{
    const root=document.documentElement,nodes=[...document.querySelectorAll('[data-reveal]')];
    if(!('IntersectionObserver' in window)||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){entry.target.classList.add('p-in');observer.unobserve(entry.target);}},{rootMargin:'0px 0px -64px 0px',threshold:.08});
    for(const node of nodes)observer.observe(node);
    root.classList.add('p-motion');
    return()=>{observer.disconnect();root.classList.remove('p-motion');for(const node of nodes)node.classList.remove('p-in');};
  },[]);
  return null;
}
