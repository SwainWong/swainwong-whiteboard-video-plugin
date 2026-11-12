export {DrawCar} from './Drawing';
export {Letters} from './Letters';
export {Branch,validateBranchNodes} from './Branch';
export type {BranchNode,BranchEdge} from './Branch';
export {StageBoard,validateStageBoard} from './StageBoard';
export type {Stage} from './StageBoard';
export {planDrawing} from './contracts';
export type {NarrationCue,Stroke} from './contracts';
/** JSON image nodes adapter: caller supplies an already resolved URL (staticFile for local assets). */
import React from 'react';import {BranchNode} from './Branch';
export type ImageNode={id:string;x:number;y:number;width:number;height:number;src:string};
export function imageNodes(nodes:ImageNode[]):BranchNode[]{return nodes.map(n=>{if(!n.src)throw Error('Image source required');return {...n,content:React.createElement('image',{href:n.src,width:n.width,height:n.height,preserveAspectRatio:'xMidYMid meet'})}})}

export {PalmPlace} from './PalmPlace';
export type {PalmPlaceProps} from './PalmPlace';

export {WhiteboardRecipe} from './Root';
export type {RecipeScene,SceneNode,GlyphData} from './scene';
export {validateScene,validateNodes,drawingPlan,defaultDrawScale} from './scene';
export {PenDrawing} from './PenDrawing';
export {validatePen,strokeProgress,penTip} from './PenProgram';
export type {PenProgram,PenLayer,PenStroke} from './PenProgram';
