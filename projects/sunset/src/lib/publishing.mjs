import {prepareArtifact} from './demo.mjs';
import {validatePack,hashBytes} from './pack.mjs';
import {toYocto} from './ledger.mjs';
import {validateMirrorUri} from './stewardship.mjs';
import {validContract} from './chain.mjs';

/** Same preparation in the creator UI and private CLI; this never publishes or signs. */
export async function prepareOnchainCampaign(pack,options,now=Date.now()){
 validatePack(pack);if(!validContract(options.reviewer))throw Error('Use a real testnet reviewer account');
 const manifestUri=validateMirrorUri(options.manifestUri);
 const deadline=Date.parse(options.deadline);if(!Number.isSafeInteger(deadline)||deadline<=now)throw Error('Funding deadline must be a future ISO date');
 const hours=Number(options.releaseHours||24);if(!Number.isInteger(hours)||hours<1||hours>720)throw Error('Release window must be 1–720 hours');
 const target=toYocto(options.target);if(target==='0')throw Error('Target must be positive');
 if(new TextEncoder().encode(pack.title).length>120)throw Error('Contract title exceeds 120 UTF-8 bytes');
 const a=await prepareArtifact(pack),terms={id:pack.id,title:pack.title,reviewer:options.reviewer,manifest_uri:manifestUri,manifest_hash:a.manifestHash,plaintext_hash:a.plaintextHash,ciphertext_hash:a.ciphertextHash,key_commitment:a.keyCommitment,license_hash:await hashBytes(new TextEncoder().encode(pack.license)),target,funding_deadline_ns:(BigInt(deadline)*1000000n).toString(),release_window_ns:(BigInt(hours)*3600000000000n).toString()};
 const {key,...artifact}=a;return{terms,artifact,backup:{schema:1,campaignId:pack.id,keyBase64:key,manifestHash:a.manifestHash}};
}
