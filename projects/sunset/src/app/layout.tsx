import type { Metadata } from 'next';
import './globals.css';
import './theme.css';
import './protocol.css';
import {themeBootstrap} from '../lib/theme.mjs';
export const metadata: Metadata = {title:'SUNSET — Support once. Share forever.',icons:{icon:'/icon.svg'},description:'Open technical guides and community-sponsored public releases on NEAR testnet. Read, calculate and keep a copy. Connect your wallet to participate.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en" suppressHydrationWarning><head><script id="sunset-theme" dangerouslySetInnerHTML={{__html:themeBootstrap}}/><link rel="preload" href="/fonts/geist-latin-variable.woff2" as="font" type="font/woff2" crossOrigin="anonymous"/><link rel="preload" href="/fonts/bricolage-grotesque-latin-variable.woff2" as="font" type="font/woff2" crossOrigin="anonymous"/></head><body>{children}</body></html>}
