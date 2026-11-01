import type { Metadata } from 'next';
import './globals.css';
import './landing.css';
import './workspace.css';
export const metadata: Metadata = {title:'SUNSET — Support once. Share forever.',icons:{icon:'/icon.svg'},description:'A community funds a useful resource. Its creator is paid when the verified pack becomes public. Learn offline, long after the campaign ends.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><head><link rel="preload" href="/fonts/geist-latin-variable.woff2" as="font" type="font/woff2" crossOrigin="anonymous"/></head><body>{children}</body></html>}
