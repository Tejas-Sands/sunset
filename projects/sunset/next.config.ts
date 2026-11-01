import type { NextConfig } from 'next';
const config: NextConfig = {output:'export',poweredByHeader:false,images:{unoptimized:true},experimental:{workerThreads:true,cpus:1}};
export default config;
