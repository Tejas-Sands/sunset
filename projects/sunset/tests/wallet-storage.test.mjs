import test from 'node:test';
import assert from 'node:assert/strict';

test('SDK metadata restores durable wallet selection and observes another tab while storage works',async()=>{
 const {createWalletMetadataStorage}=await import('../src/lib/wallet-storage.mjs');
 const map=new Map([['selected-wallet','meteor-wallet']]),local={getItem:key=>map.get(key)??null,setItem:(key,value)=>map.set(key,value),removeItem:key=>map.delete(key)};
 const storage=createWalletMetadataStorage(()=>local);
 assert.equal(await storage.get('selected-wallet'),'meteor-wallet');
 map.set('selected-wallet','nightly');assert.equal(await storage.get('selected-wallet'),'nightly');
 await storage.set('selected-wallet','intear');assert.equal(map.get('selected-wallet'),'intear');
 await storage.remove('selected-wallet');assert.equal(await storage.get('selected-wallet'),null);
});
test('denied SDK metadata storage stays usable in memory without uncaught rejection or durable writes',async()=>{
 const {createWalletMetadataStorage}=await import('../src/lib/wallet-storage.mjs');
 const storage=createWalletMetadataStorage(()=>{throw new DOMException('Denied','SecurityError');});
 assert.equal(await storage.get('debug-wallets'),null);
 await storage.set('selected-wallet','meteor-wallet');assert.equal(await storage.get('selected-wallet'),'meteor-wallet');
 await storage.remove('selected-wallet');assert.equal(await storage.get('selected-wallet'),null);
});
test('quota failure retains the latest SDK metadata rather than reverting to a stale durable selection',async()=>{
 const {createWalletMetadataStorage}=await import('../src/lib/wallet-storage.mjs');
 const storage=createWalletMetadataStorage(()=>({getItem:()=> 'old-wallet',setItem(){throw Error('Quota exceeded');},removeItem(){throw Error('Denied');}}));
 await storage.set('selected-wallet','new-wallet');assert.equal(await storage.get('selected-wallet'),'new-wallet');
 await storage.remove('selected-wallet');assert.equal(await storage.get('selected-wallet'),null);
});
