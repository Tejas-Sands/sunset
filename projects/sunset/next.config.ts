import type { NextConfig } from 'next';
// Use the pinned TypeScript compiler API; strict tsc checks also run independently.
const config: NextConfig = {output:'export',trailingSlash:true,poweredByHeader:false,images:{unoptimized:true},experimental:{workerThreads:true,cpus:1,useTypeScriptCli:false}};
export default config;
