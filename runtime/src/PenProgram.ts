import {svgPathProperties} from 'svg-path-properties';
import {clamp, smooth} from './contracts';

/** One clock drives both deposited ink and the calibrated pen tip. Coordinates are world pixels. */
export type PenLayer = {id:string; clip?:string; image?:{src:string;x:number;y:number;width:number;height:number}};
export type PenStroke = {id:string;layer:string;d:string;width:number;color:string;start:number;end:number;sweep?:{bounds:[number,number,number,number];direction:'left-to-right'|'right-to-left'|'top-left-to-bottom-right'}};
export type PenProgram = {layers:PenLayer[];strokes:PenStroke[]};
export function validatePen(program:PenProgram, duration:number) {
  if (!program || !Array.isArray(program.layers) || !program.layers.length || !Array.isArray(program.strokes) || !program.strokes.length) throw Error('Pen layers and strokes required');
  const layers=new Set<string>(), ids=new Set<string>();
  for (const l of program.layers) {
    if (!l.id || layers.has(l.id)) throw Error('Unique pen layer IDs required');
    layers.add(l.id);
    if(l.clip && (!Number.isFinite(new svgPathProperties(l.clip).getTotalLength()) || new svgPathProperties(l.clip).getTotalLength()<=0)) throw Error('Invalid pen clip');
    if(l.image) {const a=l.image;if(!a.src || /^(?:\/|[a-zA-Z][a-zA-Z0-9+.-]*:)/.test(a.src) || a.src.includes('\\') || a.src.split('/').some(p=>!p||p==='.'||p==='..') || ![a.x,a.y,a.width,a.height].every(Number.isFinite)||a.width<=0||a.height<=0) throw Error('Pen image must be public-relative with valid bounds');}
  }
  let previous:PenStroke|undefined;
  for(const s of program.strokes) {
    if(!s.id || ids.has(s.id) || !layers.has(s.layer)) throw Error('Unique stroke ID and existing layer required');
    ids.add(s.id);
    if(s.sweep){const sw=s.sweep,layer=program.layers.find(l=>l.id===s.layer)!;if(layer.image||!layer.clip||!Array.isArray(sw.bounds)||sw.bounds.length!==4||!sw.bounds.every(Number.isFinite)||sw.bounds[2]<=0||sw.bounds[3]<=0||!['left-to-right','right-to-left','top-left-to-bottom-right'].includes(sw.direction))throw Error('Color sweep requires a clipped layer, positive bounds and supported direction');}
    if(![s.start,s.end].every(Number.isInteger)||s.start<20||s.end<=s.start||s.end+45>duration||!Number.isFinite(s.width)||s.width<=0||!/^#[0-9a-fA-F]{6}$/.test(s.color)) throw Error('Invalid pen time, width or color');
    // Compound paths jump between subpaths; split them into separate strokes with lift/travel time.
    if(typeof s.d!=='string'||(s.d.match(/[mM]/g)||[]).length!==1) throw Error('Each pen stroke needs one continuous subpath');
    const path=new svgPathProperties(s.d),length=path.getTotalLength();
    if(!Number.isFinite(length)||length<=0||length/(s.end-s.start)>(s.sweep?120:30)) throw Error('Pen stroke exceeds its speed budget');
    if(previous) {
      const a=new svgPathProperties(previous.d).getPointAtLength(new svgPathProperties(previous.d).getTotalLength()),b=path.getPointAtLength(0),gap=s.start-previous.end;
      if(gap<0 || Math.hypot(b.x-a.x,b.y-a.y)>30*gap) throw Error('Pen travel overlaps or teleports; reserve travel frames');
    }
    previous=s;
  }
  if(program.layers.some(l=>!program.strokes.some(s=>s.layer===l.id))) throw Error('Every pen layer needs strokes');
  return true;
}
export const strokeProgress=(s:PenStroke,frame:number)=>clamp((frame-s.start)/(s.end-s.start));
export function penTip(program:PenProgram, frame:number):{x:number;y:number}|null {
  const first=program.strokes[0],last=program.strokes[program.strokes.length-1];
  if(frame<first.start-20||frame>last.end+45)return null;
  const start=new svgPathProperties(first.d).getPointAtLength(0);
  if(frame<first.start){const t=smooth((frame-first.start+20)/20);return {x:2100+(start.x-2100)*t,y:1350+(start.y-1350)*t};}
  for(let i=0;i<program.strokes.length;i++){
    const s=program.strokes[i],path=new svgPathProperties(s.d);
    if(frame<=s.end)return path.getPointAtLength(path.getTotalLength()*strokeProgress(s,frame));
    const a=path.getPointAtLength(path.getTotalLength()),next=program.strokes[i+1];
    if(next && frame<next.start){const b=new svgPathProperties(next.d).getPointAtLength(0),t=smooth((frame-s.end)/(next.start-s.end));return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};}
    if(!next){const t=smooth((frame-s.end-10)/35);return {x:a.x+(2100-a.x)*t,y:a.y+(1350-a.y)*t};}
  }
  return null;
}
