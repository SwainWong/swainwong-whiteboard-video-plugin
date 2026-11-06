import React from 'react';
// Original editable editorial illustration. Shared paths feed both static and drawn versions.
export const ink='#293744';
export const colors={yellow:'#dbac4d',blue:'#578ca4',red:'#bc6857',green:'#789987'};
export type ArtShape={d:string;fill:string;stroke?:string;strokeWidth?:number};
const tire=(x:number)=>`M ${x-24} 194 a 24 24 0 1 0 48 0 a 24 24 0 1 0 -48 0`;
const hub=(x:number)=>`M ${x-12} 194 a 12 12 0 1 0 24 0 a 12 12 0 1 0 -24 0`;
const body={d:'M 20 168 Q 20 153 41 149 L 76 104 Q 86 93 108 92 L 202 92 Q 220 93 234 107 L 272 143 L 307 153 Q 322 157 324 173 L 321 194 L 293 197 Q 289 164 266 164 Q 240 164 237 198 L 108 198 Q 103 164 79 164 Q 52 164 50 197 L 25 192 Z',fill:colors.yellow};
const glass={d:'M 86 109 L 140 108 L 140 141 L 62 141 Z M 153 108 L 197 108 Q 211 108 220 118 L 245 141 L 153 141 Z',fill:'#c7e0e6'};
export const carEssentialShapes:ArtShape[]=[body,glass,{d:tire(79),fill:ink},{d:tire(266),fill:ink},{d:hub(79),fill:'#c4ced4'},{d:hub(266),fill:'#c4ced4'}];
export const carShapes:ArtShape[]=[body,glass,
 {d:'M 33 168 L 51 166 M 290 162 L 314 169 M 115 182 L 225 182',fill:'none',stroke:'#f7dfa7',strokeWidth:4},
 {d:'M 147 147 L 147 185 M 235 149 L 239 159 M 117 155 L 131 155 M 208 155 L 222 155',fill:'none',strokeWidth:2.5},
 {d:'M 244 135 L 258 135 L 258 146 L 244 147 Z',fill:ink},
 {d:'M 24 168 L 41 168 L 39 179 L 22 178 Z',fill:'#bc6857'},
 {d:'M 302 169 L 322 173 L 320 182 L 301 180 Z',fill:'#f8f3df'},
 {d:'M 109 195 L 236 195 M 23 188 L 47 190 M 295 190 L 319 188',fill:'none',strokeWidth:3},
 {d:tire(79),fill:ink},{d:tire(266),fill:ink},
 {d:hub(79),fill:'#c4ced4'},{d:hub(266),fill:'#c4ced4'},
 {d:'M 79 185 V 203 M 70 194 H 88 M 266 185 V 203 M 257 194 H 275',fill:'none',strokeWidth:2},
 {d:'M 89 118 L 131 118 M 161 118 L 198 118',fill:'none',stroke:'#f7fbfc',strokeWidth:3}];
export const Car=()=> <g stroke={ink} strokeWidth={3.2} strokeLinejoin="round" strokeLinecap="round">{carShapes.map((s,i)=><path key={i} {...s}/>)}</g>;
export const Person=({mood='happy',shirt=colors.blue}:{mood?:string,shirt?:string})=><g stroke={ink} strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round">
 <path d="M 116 265 L 106 402 L 137 402 L 154 293 L 169 402 L 201 402 L 189 265 Z" fill="#344755"/>
 <path d="M 113 401 L 136 401 L 137 421 L 94 421 Q 93 410 113 401 Z M 172 401 L 199 401 Q 219 410 216 421 L 172 421 Z" fill="#27313a"/>
 <path d="M 119 398 L 133 398 M 177 398 L 195 398" fill="none" stroke="#8495a0"/>
 <path d="M 107 151 Q 86 155 76 181 L 60 245 L 78 254 L 110 203 L 111 276 L 191 276 L 193 202 L 215 238 L 235 228 L 218 181 Q 207 155 187 151 Z" fill={shirt}/>
 <path d="M 132 142 L 132 163 L 151 181 L 171 162 L 170 141 Z" fill="#ddad89"/>
 <path d="M 129 154 L 151 180 L 136 193 L 118 161 Z M 174 154 L 151 180 L 168 192 L 187 162 Z" fill="#eef1e9"/>
 <path d="M 151 181 L 151 270 M 119 234 L 137 234 M 178 229 L 188 226 M 114 267 L 187 267" fill="none" strokeWidth={2}/>
 <path d="M 69 244 L 81 250 L 79 271 Q 75 284 66 280 L 59 272 Q 55 267 61 255 Z M 216 232 L 231 225 L 242 241 Q 245 251 235 255 Q 229 259 222 247 Z" fill="#e6b995"/>
 <path d="M 112 93 Q 103 82 101 98 Q 102 116 113 117 M 188 93 Q 201 82 201 99 Q 200 114 190 117" fill="#e6b995"/>
 <path d="M 113 65 Q 111 37 151 35 Q 191 37 190 69 L 187 118 Q 179 145 153 149 Q 126 145 116 120 Z" fill="#e8bd99"/>
 <path d="M 112 96 L 107 67 Q 104 40 127 31 Q 149 18 178 30 Q 202 34 196 62 L 190 95 L 182 61 Q 154 76 123 58 L 119 96 Z" fill="#34414b"/>
 <path d="M 121 49 Q 151 60 181 43 M 123 83 L 138 81 M 162 81 L 179 84" fill="none" strokeWidth={2.3}/>
 <path d="M 128 94 L 134 94 M 166 94 L 172 94 M 150 96 L 147 114 L 155 116" fill="none" strokeWidth={3}/>
 {mood==='wow'?<path d="M 145 128 Q 153 120 161 128 L 159 138 L 148 138 Z" fill="#985b49"/>:mood==='sad'?<path d="M 140 131 Q 151 123 163 131" fill="none"/>:<path d="M 139 127 Q 151 137 165 125" fill="none" strokeWidth={2.5}/>}
 <path d="M 125 112 L 131 115 M 174 111 L 179 108" fill="none" stroke="#c58e73" strokeWidth={2}/>
 </g>;
export const Factory=()=> <g stroke={ink} strokeWidth={3.2} strokeLinejoin="round" strokeLinecap="round">
 <path d="M 28 238 V 123 L 103 151 V 119 L 177 149 V 117 L 284 153 V 238 Z" fill={colors.blue}/>
 <path d="M 46 127 L 50 36 H 76 L 80 139 Z" fill="#bc6857"/>
 <path d="M 49 44 H 77 M 49 57 H 77 M 48 91 H 78" fill="none" strokeWidth={2}/>
 <path d="M 28 157 L 103 180 L 177 177 L 284 178 V 238 H 28 Z" fill="#739ead"/>
 <path d="M 28 123 L 103 151 M 103 119 L 177 149 M 177 117 L 284 153" fill="none" strokeWidth={5}/>
 {[44,102,160,218].map(x=><g key={x}><path d={`M ${x} 184 h 42 v 25 h -42 Z`} fill="#c9dce1"/><path d={`M ${x+21} 185 v 23 M ${x+2} 196 h 38`} fill="none" strokeWidth={1.7}/></g>)}
 <path d="M 130 238 V 214 H 174 V 238 M 130 222 H 174 M 130 230 H 174 M 20 240 H 294" fill="#d3dee0" strokeWidth={2.5}/>
 <path d="M 37 218 V 232 M 279 183 V 229 M 111 154 V 173 M 185 152 V 172" fill="none" stroke="#496b7b" strokeWidth={2}/>
 </g>;
export const Card=({x=0,y=0,children,width=580,height=390}:any)=><g transform={`translate(${x} ${y})`}><rect x={8} y={10} width={width} height={height} rx={8} fill="#d4c8b6" opacity={.5}/><rect width={width} height={height} rx={8} fill="#fffdf5" stroke={ink} strokeWidth={2.5}/>{children}</g>;
// Compatibility only. Production PalmPlace uses calibrated photographic palm-real.png.
export const Palm=()=>null;
