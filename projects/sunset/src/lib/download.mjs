export function download(filename,value,type='application/json'){
  const blob=new Blob([typeof value==='string'?value:Uint8Array.from(value)],{type});
  const url=URL.createObjectURL(blob),link=document.createElement('a');
  link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
