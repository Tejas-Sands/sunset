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
    {step:'create-campaign',label:'Campaign created',detail:'Content and terms committed',signer:'shiftultra.testnet',hash:'5ffZw3hFKThQvypwrkUEEpHkdFwviXCT921AJ2y5PSfA'},
    {step:'approve-campaign',label:'Content approved',detail:'Reviewer accepted the agreement',signer:'reviewer.shiftultra.testnet',hash:'FD7itSMqfXzxkD6mTPcmPWTryK3sNtqGnfMzPoTuxcsj'},
    {step:'contribute-sponsor',label:'Sponsored 0.06 testNEAR',detail:'Held by the contract',signer:'sponsor.shiftultra.testnet',hash:'HHJndL2H5DRXgWoaAg5nndsNwyMS16bqQBGYVc6nEHd8'},
    {step:'contribute-reviewer',label:'Sponsored 0.04 testNEAR',detail:'Goal of 0.1 reached',signer:'reviewer.shiftultra.testnet',hash:'nyoxYNWPnFiiqNakxnENbNQnDz6ANSe52fx8FvahePD'},
    {step:'publish-release',label:'Release key published',detail:'Resource opened under CC0',signer:'shiftultra.testnet',hash:'7Z2kZEcTCeHnVC4P59najdsHfZXKNVEn3zumCUAgPUxd'},
    {step:'creator-withdrawal',label:'Creator paid 0.1 testNEAR',detail:'Native transfer confirmed',signer:'shiftultra.testnet',hash:'4tUbpdnkMV52ET6iLMosYVeRwfipyTMS3wQBDFRovcL4'},
    {step:'stewardship-transfer',label:'Stewardship transferred',detail:'Mirror duty moved to a new holder',signer:'shiftultra.testnet',hash:'6GL3kPGnE9NyiMQxsgJWfZt1wVS5k49yPdWNT5kVADTp'}
  ],
  refund:[
    {step:'claim',label:'Refund claimed',detail:'Funding deadline passed unmet',signer:'sponsor.shiftultra.testnet',hash:'5zTJtUY1qa8Fev8t3tfpB4JgQVaxNjWb1ZBDRQyEKsum'},
    {step:'withdraw',label:'Refund withdrawn',detail:'Contribution returned to the sponsor',signer:'sponsor.shiftultra.testnet',hash:'AT6nuVmzNoj9zghYkDPNWSU8uWLjxtx3fMthZJkjbBRt'}
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
