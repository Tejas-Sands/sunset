// Finalized NEAR testnet records shown on the site. Every value is copied from evidence/testnet-showcase.json
// and evidence/testnet-refunds.json; tests/proof.test.mjs fails if any of them drifts from that evidence.
export const EXPLORER='https://testnet.nearblocks.io';
export const transactionUrl=hash=>`${EXPLORER}/txns/${hash}`;
export const accountUrl=id=>`${EXPLORER}/address/${id}`;
export const shorten=(value,head=6,tail=4)=>value.length<=head+tail+1?value:`${value.slice(0,head)}…${tail?value.slice(-tail):''}`;

export const PROOF=Object.freeze({
  contract:'sunset.shiftultra.testnet',
  codeHash:'9Envfh1ieixUpUoe3egVPSHphJdRuDnyGfEhWcLe46fx',
  verifiedBlock:275928158,
  release:[
    {step:'create-campaign',label:'Campaign created',detail:'Content and terms committed',signer:'shiftultra.testnet',hash:'5ffZw3hFKThQvypwrkUEEpHkdFwviXCT921AJ2y5PSfA',block:'ADXAk77mpAEDH46fCimE6LA7YVmXn4B2hcsb151PFTTk'},
    {step:'approve-campaign',label:'Content approved',detail:'Reviewer accepted the agreement',signer:'reviewer.shiftultra.testnet',hash:'FD7itSMqfXzxkD6mTPcmPWTryK3sNtqGnfMzPoTuxcsj',block:'7vnv6gYnDz5Kojxg8tX9JTaBDYAaxtt1HTZRg6cssV7s'},
    {step:'contribute-sponsor',label:'Sponsored 0.06 testNEAR',detail:'Held by the contract',signer:'sponsor.shiftultra.testnet',hash:'HHJndL2H5DRXgWoaAg5nndsNwyMS16bqQBGYVc6nEHd8',block:'43GN1udMngeYKEZPCnJ3f277txDdZkYCfFRBp2BFHiPQ'},
    {step:'contribute-reviewer',label:'Sponsored 0.04 testNEAR',detail:'Goal of 0.1 reached',signer:'reviewer.shiftultra.testnet',hash:'nyoxYNWPnFiiqNakxnENbNQnDz6ANSe52fx8FvahePD',block:'Bi3UHSe6r2L6HtopwRgNpJ9MuR1qX1mem5x2C9bHb4qX'},
    {step:'publish-release',label:'Release key published',detail:'Resource opened under CC0',signer:'shiftultra.testnet',hash:'7Z2kZEcTCeHnVC4P59najdsHfZXKNVEn3zumCUAgPUxd',block:'2p4z4zoqsgsJveBkcwMo9HAxTC6DCMUAn3GE9pe67PWH'},
    {step:'creator-withdrawal',label:'Creator paid 0.1 testNEAR',detail:'Native transfer confirmed',signer:'shiftultra.testnet',hash:'4tUbpdnkMV52ET6iLMosYVeRwfipyTMS3wQBDFRovcL4',block:'EmyNJa1ZfQLwo98JTmW2bB8snDXggJje5W844Z6dZU1Z'},
    {step:'stewardship-transfer',label:'Stewardship transferred',detail:'Mirror duty moved to a new holder',signer:'shiftultra.testnet',hash:'6GL3kPGnE9NyiMQxsgJWfZt1wVS5k49yPdWNT5kVADTp',block:'AfcuuPy4ogoWoMcyQ7B5nroTxP9Z7SCf46h14ZZKJ2zX'}
  ],
  refund:[
    {step:'claim',label:'Refund claimed',detail:'Funding deadline passed unmet',signer:'sponsor.shiftultra.testnet',hash:'5zTJtUY1qa8Fev8t3tfpB4JgQVaxNjWb1ZBDRQyEKsum',block:'xub5dFCegmHM2XncQ2HacAm6L8j5mQbYQvFAdTM4mJC'},
    {step:'withdraw',label:'Refund withdrawn',detail:'Contribution returned to the sponsor',signer:'sponsor.shiftultra.testnet',hash:'AT6nuVmzNoj9zghYkDPNWSU8uWLjxtx3fMthZJkjbBRt',block:'5GasSedX5hzXgXcsHvqpjPjT8WKT26dxnX4C4ceeef5Y'}
  ]
});

// A 5 x 5 mirrored pattern derived from a hex digest, so matching content always draws the same mark.
export function fingerprintCells(hex){
  const digits=String(hex).replace(/[^0-9a-f]/gi,'');
  if(digits.length<15)return [];
  const cells=[];
  for(let row=0;row<5;row++)for(let column=0;column<3;column++){
    const value=parseInt(digits[row*3+column],16);
    if(value%2===0)continue;
    const strong=value>8;
    cells.push({x:column,y:row,strong});
    if(column<2)cells.push({x:4-column,y:row,strong});
  }
  return cells;
}

// Stable pseudo-digest for account names, so each account always draws the same avatar.
export function seedHex(text){
  let a=0x811c9dc5,b=0x9e3779b9,out='';
  for(const char of String(text)){a=Math.imul(a^char.codePointAt(0),0x01000193)>>>0;b=Math.imul(b+a,0x85ebca6b)>>>0;}
  for(let i=0;i<4;i++){a=Math.imul(a^(a>>>15),0x2c1b3c6d)>>>0;b=Math.imul(b^(b>>>13),0x297a2d39)>>>0;out+=a.toString(16).padStart(8,'0')+b.toString(16).padStart(8,'0');}
  return out;
}
