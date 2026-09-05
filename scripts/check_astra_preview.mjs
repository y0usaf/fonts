#!/usr/bin/env node
// Browser smoke/raster checks against a running Chromium CDP endpoint.
// Start Chromium with --remote-debugging-port=9369 and a dedicated profile.
// Usage: node scripts/check_astra_preview.mjs [http://127.0.0.1:9369]
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath, pathToFileURL} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const endpoint=process.argv[2]||'http://127.0.0.1:9369';
const tab=await(await fetch(endpoint+'/json/new?about:blank',{method:'PUT'})).json();
const ws=new WebSocket(tab.webSocketDebuggerUrl);
await new Promise(resolve=>ws.addEventListener('open',resolve,{once:true}));
let id=0;const pending=new Map(),external=[];
ws.addEventListener('message',e=>{
 const m=JSON.parse(e.data);
 if(m.id){const {resolve,reject}=pending.get(m.id);pending.delete(m.id);m.error?reject(Error(m.error.message)):resolve(m.result);}
 if(m.method==='Network.requestWillBeSent'&&/^https?:/.test(m.params.request.url))external.push(m.params.request.url);
});
const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}));});
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
try{
 await send('Network.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:pathToFileURL(path.join(root,'assets/previews/astra-pixel/comparison.html')).href});
 for(let i=0;i<100;i++){if(await evaluate('Boolean(window.proofReady||window.proofError)'))break;await new Promise(r=>setTimeout(r,100));}
 assert.equal(await evaluate('window.proofError||window.proofReady'),true);
 const result=await evaluate(`(()=>{
  let glyphs=0;
  for(const {font} of contexts.filter(c=>c.font.name.startsWith('Astra Pixel'))){
   const c=document.createElement('canvas');c.width=40;c.height=60;const ctx=c.getContext('2d');
   for(const zoom of [1,2,3])for(let cp=32;cp<127;cp++){
    ctx.clearRect(0,0,40,60);ctx.fillStyle='#fff';ctx.font=font.ppem*zoom+'px '+font.id;ctx.textBaseline='alphabetic';
    ctx.fillText(String.fromCharCode(cp),0,font.ascent*zoom);
    if(Math.abs(ctx.measureText(String.fromCharCode(cp)).width-font.advance*zoom)>.01)throw Error('advance');
    const data=ctx.getImageData(0,0,40,60).data;
    for(let y=0;y<60;y++)for(let x=0;x<40;x++){
     const a=data[(y*40+x)*4+3];if(a!==0&&a!==255)throw Error(font.name+' grayscale edge');
     if(a&&(x>=(font.advance-1)*zoom||y<zoom||y>=font.line*zoom))throw Error(font.name+' separator/cell escape '+cp);
    }
    glyphs++;
   }
  }
  return {glyphs};
 })()`);
 for(const dpr of [1,2]){
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:dpr,mobile:false});
  for(const z of [1,2,3,4]){
   const sizes=await evaluate(`document.getElementById('zoom').value='${z}';draw();contexts.map(c=>[c.canvas.getBoundingClientRect().width*devicePixelRatio,c.canvas.getBoundingClientRect().height*devicePixelRatio])`);
   for(const size of sizes)assert.deepEqual(size,[640*z,330*z]);
  }
 }
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 for(const preset of ['code','prose','pairs','ascii','boxes']){
  assert.equal(await evaluate(`document.querySelector('[data-sample="${preset}"]').click();document.getElementById('sample').value===samples.${preset}`),true);
 }
 assert.equal(await evaluate(`document.getElementById('theme').click();document.body.classList.contains('light')`),true);
 assert.equal(await evaluate(`document.getElementById('theme').click();document.body.classList.contains('light')`),false);
 assert.match(await evaluate(`document.getElementById('sample').value='A🚀';draw();document.getElementById('status').textContent`),/unsupported/);
 assert.equal(await evaluate(`document.getElementById('sample').value='0O1lI gjpqy';document.getElementById('sample').dispatchEvent(new Event('input'));document.getElementById('status').textContent.includes('No fallback')`),true);
 await evaluate(`document.querySelector('[data-sample="pairs"]').click();document.getElementById('zoom').value='1';draw()`);
 const png=await evaluate(`(()=>{
  const out=document.createElement('canvas');out.width=1280;out.height=contexts.length*250;const c=out.getContext('2d');
  c.fillStyle='#151c1c';c.fillRect(0,0,out.width,out.height);c.imageSmoothingEnabled=false;
  contexts.forEach(({canvas,font},i)=>{
   c.fillStyle='#d1ef83';c.font='18px sans-serif';c.fillText(font.name+' / '+font.advance+' × '+font.line+'px cell',12,i*250+25);
   const height=Math.floor(100/font.line)*font.line;
   c.drawImage(canvas,0,0,640,height,0,i*250+40,1280,height*2);
  });
  return out.toDataURL().split(',')[1];
 })()`);
 fs.writeFileSync(path.join(root,'assets/previews/astra-pixel/pairs.png'),Buffer.from(png,'base64'));
 assert.deepEqual(external,[]);
 console.log(JSON.stringify({...result,networkRequests:external.length,dpr:[1,2],zoom:[1,2,3,4],presets:5,themes:2}));
}finally{
 await send('Page.close');ws.close();
}
