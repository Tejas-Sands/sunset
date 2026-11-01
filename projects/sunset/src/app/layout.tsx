import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {title:'SUNSET — Support once. Share forever.',description:'A community funds a useful resource. Its creator is paid when the verified pack becomes public. Learn offline, long after the campaign ends.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
