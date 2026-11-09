import type { Metadata } from 'next';
import './globals.css';
import './landing.css';
import './workspace.css';
import './theme.css';
import {themeBootstrap} from '../lib/theme.mjs';
export const metadata: Metadata = {title:'SUNSET — Support once. Share forever.',icons:{icon:'/icon.svg'},description:'A community funds a useful resource. Its creator is paid when the verified pack becomes public. Learn offline, long after the campaign ends.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en" suppressHydrationWarning><head><script id="sunset-theme" dangerouslySetInnerHTML={{__html:themeBootstrap}}/><link rel="preload" href="/fonts/geist-latin-variable.woff2" as="font" type="font/woff2" crossOrigin="anonymous"/></head><body>{children}</body></html>}
