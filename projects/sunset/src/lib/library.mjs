import attention from '../../public/packs/transformer-attention.json' with {type:'json'};
import backprop from '../../public/packs/backpropagation.json' with {type:'json'};
import adapters from '../../public/packs/low-rank-adapters.json' with {type:'json'};

const details=[
  {pack:attention,topic:'TRANSFORMERS',duration:'18 min',formula:'softmax(QKᵀ / √dₖ)V',sources:[{label:'Attention Is All You Need · Vaswani et al.',href:'https://arxiv.org/abs/1706.03762'}]},
  {pack:backprop,topic:'NEURAL NETWORKS',duration:'16 min',formula:'∂L/∂w = (p − y)x',sources:[{label:'Backpropagation · Stanford CS231n',href:'https://cs231n.github.io/optimization-2/'}]},
  {pack:adapters,topic:'EFFICIENT ADAPTATION',duration:'15 min',formula:'ΔW = (α/r)BA',sources:[{label:'LoRA · Hu et al.',href:'https://arxiv.org/abs/2106.09685'}]}
];
export const resources=details.map((resource,index)=>({...resource,index,id:resource.pack.id,title:resource.pack.title,description:resource.pack.description,
  href:`/resources/${resource.pack.id}/`,download:`/library/${resource.pack.id}.html`}));
export function resourceById(id){return resources.find(resource=>resource.id===id);}
