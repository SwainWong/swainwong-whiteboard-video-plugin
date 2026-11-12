import React, {useId} from 'react';
import {staticFile,useCurrentFrame} from 'remotion';
import {PenProgram,strokeProgress,penTip} from './PenProgram';
import {Hand} from './Hand';

export const PenDrawing=({program}:{program:PenProgram})=>{
  const frame=useCurrentFrame(),prefix=useId().replace(/:/g,'_'),tip=penTip(program,frame);
  return <><svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>{program.layers.map((layer,i)=>{
    const clip=`${prefix}-clip-${i}`,mask=`${prefix}-mask-${i}`;
    const strokes=program.strokes.filter(s=>s.layer===layer.id).map(s=>{
      const progress=strokeProgress(s,frame);
      // Do not emit a round-cap dot before contact. No filled backing path or completion fade.
      return progress<=0?null:<path key={s.id} d={s.d} fill="none" stroke={layer.image?'white':s.color} strokeWidth={s.width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1-progress}/>;
    });
    return <g key={layer.id}><defs>{layer.clip&&<clipPath id={clip}><path d={layer.clip}/></clipPath>}{layer.image&&<mask id={mask} maskUnits="userSpaceOnUse" x={0} y={0} width={1920} height={1080}>{strokes}</mask>}</defs><g clipPath={layer.clip?`url(#${clip})`:undefined}>{layer.image?<image href={staticFile(layer.image.src)} x={layer.image.x} y={layer.image.y} width={layer.image.width} height={layer.image.height} preserveAspectRatio="xMidYMid meet" mask={`url(#${mask})`}/>:strokes}</g></g>;
  })}</svg>{tip&&<Hand x={tip.x} y={tip.y}/>}</>;
};
