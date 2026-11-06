/** All times are frames on the composition clock. Never speed up past the declared pen budget. */
export type Stroke={d:string;fill:string;optional?:boolean;stroke?:string;strokeWidth?:number};
export type NarrationCue={id:string;start:number;end:number;readHold:number};
export function planDrawing(cue:NarrationCue, lengths:number[], pixelsPerFrame=14, travelFrames=5, requiredCount=lengths.length){
 if(![cue.start,cue.end,cue.readHold,travelFrames,requiredCount].every(Number.isInteger)||!Number.isFinite(pixelsPerFrame)||travelFrames<0||requiredCount<1||requiredCount>lengths.length||cue.readHold>=cue.end-cue.start||!cue.id||!Number.isFinite(cue.start)||!Number.isFinite(cue.end)||cue.start<0||cue.end<=cue.start||cue.readHold<0||pixelsPerFrame<=0)throw Error('Invalid narration cue');
 const deadline=cue.end-cue.readHold;let cursor=cue.start;
 const strokes=lengths.map((length,index)=>{if(!Number.isFinite(length)||length<=0)throw Error('Invalid path length'); const duration=Math.max(6,Math.ceil(length/pixelsPerFrame));const selected=cursor+duration<=deadline;if(!selected&&index<requiredCount)throw Error('Essential drawing exceeds cue budget: simplify the whole object or place a finished image');const start=cursor;if(selected)cursor+=duration+travelFrames;return {index,start,end:start+duration,selected}});
 return {cue,strokes,omitted:strokes.filter(s=>!s.selected).map(s=>s.index),drawEnd:Math.max(cue.start,...strokes.filter(s=>s.selected).map(s=>s.end)),deadline};
}
export const clamp=(x:number)=>Math.max(0,Math.min(1,x));export const smooth=(x:number)=>{x=clamp(x);return x*x*(3-2*x)};
