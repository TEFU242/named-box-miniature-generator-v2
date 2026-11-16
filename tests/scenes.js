// 截圖場景（注入 index.html 副本；網址 hash 指定場景）
const SC=location.hash.slice(1)||'1';
const A=(o)=>{applyState({...JSON.parse(JSON.stringify(DEFAULT_P)),...o});};
const base={roofStyle:'none'};
const scenes={
 '1':()=>{A({step:1});},
 '2':()=>{A({step:2,roof:'mansard',rise:30,eaveX:8,eaveZ:8,roofT:2.5,ridgeCap:true,chimOn:true,roofStyle:'clay',roofScale:0.6,roofSplit:true,roofLift:18,floors:2,frameOn:true,winStyle:'arch'});},
 '3':()=>{A({step:3,floors:2,frameOn:true,winStyle:'cross',winManual:[{wall:'front',c:-32,w:12,h:12,y0:6,style:'cross'},{wall:'front',c:4,w:12,h:12,y0:9,style:'cross'},{wall:'front',c:34,w:12,h:12,y0:3,style:'cross'},{wall:'front',c:-32,w:12,h:12,y0:28,style:'arch'},{wall:'front',c:4,w:12,h:12,y0:28,style:'arch'}]});setWinSel([0,1,2]);},
 '4':()=>{A({step:4,roofStyle:'slate',roofAge:55,skinAge:60,skinRes:'0.5',tool:'rect'});sync();SEL.clear();for(const f of FACES)if(Math.abs(f.n[1])<0.05)SEL.add(f.name);P.skinType='brick';applySkin(false);
  const f=FACES.find(x=>wallOfFace(x)==='front'),it=FLAT.items.find(i=>i.f.name===f.name),poly=[[0,0],[0,0],[0,0],[0,0]];setRect(poly,it.umin+55,it.vmin+3,it.umin+85,it.vmin+16);PEND.push({name:f.name,poly});selectRegion(poly,f.name);},
 '5':()=>{A({step:5,floors:2,floorOn:true,iwalls:[{axis:'x',pos:-8,a0:-48,a1:48,doors:[{c:-25,w:12,h:18},{c:22,w:12,h:18}]},{axis:'z',pos:10,a0:-8,a1:48,doors:[{c:25,w:10,h:18}]}]});iwSel=0;},
 '6':()=>{A({step:6,print:'laser',roof:'gambrel',roofSplit:true,roofOut:'same',floors:2,slabOn:true,frameOn:true});},
 '7':()=>{A({step:2,roof:'hip',rise:28,eaveX:10,eaveZ:10,roofStyle:'metal'});applyTheme(true);},
 '9':()=>{A({step:5,floors:3,slabOn:true,floorOn:true,doorOn:true,doorStyle:'arch',roof:'hip',iwalls:[{axis:'x',pos:-10,a0:-48,a1:10,doors:[{c:-20,w:12,h:18}]}],stairs:[{on:true,x:-40,z:20,dir:'+x',width:10,slope:36,riserH:2.5},{on:true,x:20,z:35,dir:'-z',width:10,slope:42,riserH:2.5}]});iwSel=0;},
 '10':()=>{A({step:3,floors:2,doorOn:true,doorStyle:'double',doorW:16,doorC:12,frameOn:true,roof:'gable'});},
 '11':()=>{A({step:2,roofSplit:true,roofLift:40,roof:'gable',rise:25});cam.position.set(95,55,120);ctl.target.set(0,25,0);},
 '12':()=>{A({step:1,roof:'gable',rise:22,annex:[newAnnex('garage',{side:'right',off:-12}),newAnnex('porch',{side:'front',off:-20,aw:40}),newAnnex('shed',{side:'back',gap:12,off:-25})]});cam.position.set(210,150,260);ctl.target.set(20,12,0);},
 '13':()=>{A({step:5,floors:3,slabOn:true,floorOn:true,planFloor:1,iwalls:[{axis:'x',floor:0,pos:-8,a0:-48,a1:48,doors:[{c:-25,w:12,h:18}]},{axis:'z',floor:1,pos:12,a0:-30,a1:48,doors:[{c:20,w:10,h:18}]}],stairs:[{on:true,x:-40,z:25,dir:'+x',width:10,slope:38,riserH:2.5,type:'L',struct:'open',rail:'both',turn:'right',split:50,railH:6,chain:false,chainTurn:'straight'},{on:true,x:0,z:0,dir:'+x',width:10,slope:40,riserH:2.5,type:'U',struct:'solid',rail:'right',turn:'right',split:50,railH:6,chain:true,chainTurn:'straight'}]});},
 '14':()=>{A({step:4,skinType:'brick',skinAge:45,skinScale:0.7});sync();setTimeout(()=>{$('panel').scrollTop=520;},50);},
 '15':()=>{A({step:3,floors:2,winManual:[{wall:'front',c:-30,w:10,h:10,y0:6,style:'fixed'},{wall:'front',c:5,w:10,h:10,y0:6,style:'fixed'},{wall:'front',c:30,w:10,h:10,y0:6,style:'fixed'},{wall:'front',c:-30,w:10,h:10,y0:26,style:'cross'}]});sync();goStep(3);setWinSel([0,1,2]);winKey=1;WLAY=WLAY||layoutFaces(FACES.filter(f=>Math.abs(f.n[1])<0.05));WDRAG={h:null,start:[0,0],primary:3,toggle:false,moved:true,items:[{i:3,c:-30,y0:26,w:10,h0:10,sg:1}]};P.snapOn=true;elevMove({shiftKey:false},[22,-6]);renderFlat();},
 '16':()=>{A({step:1,roof:'gable',rise:22,eaveX:6,eaveZ:6,annex:[newAnnex('garage',{side:'right',off:-12}),newAnnex('porch',{side:'front',off:-20,aw:40})]});cam.position.set(60,12,150);ctl.target.set(10,14,10);},
 '17':()=>{A({step:5,floors:3,slabOn:true,floorOn:true,planFloor:1,iwalls:[{axis:'x',floor:0,pos:-8,a0:-48,a1:48,doors:[{c:-25,w:12,h:18}]},{axis:'z',floor:1,pos:12,a0:-30,a1:48,doors:[{c:20,w:10,h:18}]},{axis:'x',floor:2,pos:20,a0:-40,a1:40,doors:[{c:0,w:12,h:18}]}],stairs:[{on:true,x:-40,z:25,dir:'+x',width:10,slope:38,riserH:2.5,type:'L',struct:'open',rail:'both',turn:'right',split:50,railH:6,chain:false,chainTurn:'straight'},{on:true,x:0,z:0,dir:'+x',width:10,slope:40,riserH:2.5,type:'straight',struct:'solid',rail:'right',turn:'right',split:50,railH:6,chain:true,chainTurn:'straight'}]});},
 '18':()=>{A({step:1,xray:true,floors:2,slabOn:true,floorOn:true,iwalls:[{axis:'x',floor:0,pos:-8,a0:-48,a1:48,doors:[{c:-25,w:12,h:18}]}],stairs:[{on:true,x:-40,z:25,dir:'+x',width:10,slope:38,riserH:2.5,type:'L',struct:'open',rail:'both',turn:'right',split:50,railH:6,chain:false,chainTurn:'straight'}]});applyXray();},
 '8':()=>{A({step:2,roof:'gambrel',rise:34,roofStyle:'asphalt',ridgeCap:true,floors:2});},
};
(scenes[SC]||scenes['1'])();
setView(P.mode==='lamp'?defaultView():'3d');sync();
if(SC==='6')setView('flat');
