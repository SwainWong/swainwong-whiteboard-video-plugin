import {svgPathProperties} from 'svg-path-properties';
export type XY=[number,number];
export const clamp=(x:number)=>Math.min(1,Math.max(0,x));
const cache=new Map<string,InstanceType<typeof svgPathProperties>>();
export const property=(d:string)=>{if(!cache.has(d))cache.set(d,new svgPathProperties(d));return cache.get(d)!};
export const point=(d:string,t:number)=>{const p=property(d);const a=p.getPointAtLength(p.getTotalLength()*clamp(t));return [a.x,a.y] as XY};
export const poly=(pts:XY[])=>'M '+pts.map(p=>p.join(' ')).join(' L ');
