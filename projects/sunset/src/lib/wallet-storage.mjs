// SDK wallet selections/manifests may be ephemeral. Financial pending intents use
// the separate strict durable-storage path and must never fall back to this map.
export function createWalletMetadataStorage(getStorage){
  const memory=new Map();let memoryOnly=false;
  return {
    async get(key){
      if(!memoryOnly)try{const value=getStorage().getItem(key);memory.set(key,value);return value;}catch{memoryOnly=true;}
      return memory.get(key)??null;
    },
    async set(key,value){
      memory.set(key,value);
      if(!memoryOnly)try{getStorage().setItem(key,value);}catch{memoryOnly=true;}
    },
    async remove(key){
      memory.delete(key);
      if(!memoryOnly)try{getStorage().removeItem(key);}catch{memoryOnly=true;}
    }
  };
}
