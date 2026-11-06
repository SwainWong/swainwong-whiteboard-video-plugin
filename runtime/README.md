# Whiteboard runtime

Node 22+, Python 3, FFmpeg/FFprobe are required. This directory is self-contained; it does not read the previous research project or installed plugin caches.

```
npm ci
npx tsc --noEmit
node tests/scene.test.cjs
python3 render-all.py
```

`render-all.py` produces the eleven named examples, renders D10 last, and regenerates its completed-stage PNGs from the other ten actual outputs. Generated output, snapshots and machine evidence belong in the project, not a second plugin source copy. `out/validation.json` records render hashes and decode results; they do not establish human viewing/listening acceptance. These mechanism examples have no audio.

For your own scene, use JSON containing `{ "scene": { ... } }`:

```
node check-scene.cjs examples/image-replacement.json
npx remotion render src/index.ts WhiteboardRecipe out/custom.mp4 --props examples/image-replacement.json
```

`check-scene.cjs` also accepts an unwrapped scene for validation. Rendering uses the wrapper. The canonical TypeScript interface is `src/scene.ts`; import `src/library.ts` for components. `WhiteboardRecipe` rejects missing effect-specific inputs instead of silently drawing the example car or SALE lettering. Titles are optional ordinary reading labels; a user scene has no example footer.

- D01: `draw.paths` ordered paths and `draw.cue`, optionally drawing coordinates/scale/fill frame.
- D02: completed `objects` plus the same drawing inputs.
- D03: `objects` with entry `timing`.
- D04/D05: `objects` move up/left; `draw` supplies the next sketch. Translation distance is fixed at 1200/800 px at 1920×1080.
- D06: `objects`, optional calibrated `contact` and enter/release/exit timing. The bundled generated photographic palm is not a live-action recording.
- D07: `objects` remain underneath; `foreground` fades in at its own absolute placements.
- D08/D11: `glyphs: {width,height,minY?,glyphs:[{x,d}]}` containing prepared font outline paths, optional six-digit hex `color`. D08 fills glyph interiors; D11 fills a stable hand-shaped background. Glyph paths use upward y coordinates; height and optional minY declare vertical bounds. The full glyph group fits within 1100×400 without stretching, including a single tall glyph. No arbitrary text-to-handwriting conversion is claimed.
- D09: `nodes: [{id,x,y,width,height,object}]` and `edges: [{from,to}]`. Prepared cartoon or image content is interchangeable. Only downward graph edges with >=100 px vertical clearance are supported; no general obstacle router.
- D10: `stages` must contain completed snapshot identities and provenance. It only zooms from the last stage to a single vertical canvas; it never invents missing stages and exposes no tour mode.

Each `SceneNode` has optional x/y/scale and an `asset`. Asset types: `builtin` (car/person/factory/document), `image` (public-relative src, positive width/height), `paths` (ordered SVG path objects), `group` (child SceneNodes). Remote URLs and path traversal are rejected. Import images into your project's public folder first. Source images need appropriate usage rights and enough resolution; only explicit `paths` can be truly drawn stroke by stroke. A photo is placed/faded rather than falsely treated as handwritten vectors.

A cue is `{id,start,end,readHold}` in 30fps composition frames. Drawing computes path length, enforces its declared speed budget and requires enough complete-object time. User paths are never silently truncated. Reduce complete objects or prepare a simpler complete sketch if rejected. Scene duration must include hold and hand exit. The computed drawing plan sets fillAt to the reading-hold deadline by default; explicit fillAt must lie between drawEnd and that deadline. D04/D05 new drawing starts after the board movement finishes. The render remains deterministic and uses no hand opacity fade. Cross-composition editing still owns its handoff; the library does not pretend to have a global whole-film hand planner.

`examples/` includes actual image, overlay, custom ordered-stroke and alternate background-color calls. The single horizontal path in ordered-strokes is an intentional writing primitive; full Chinese handwriting requires externally prepared ordered character strokes.

Font outline source: the bundled SALE glyph paths were regenerated from Noto Sans Bold, SIL OFL 1.1; font and license are in `public/fonts`, hash/source recorded in `provenance.json`. Example Chinese reading labels use available system Chinese fonts; supply suitable licensed fonts in the host project for consistent non-macOS text appearance.

## Browser runtime

Remotion and its CLI are pinned together at 4.0.540. On the development Mac, the newly downloaded Headless Shell crashed before composition loading; the already installed Chrome successfully rendered. `render-all.py` accepts `REMOTION_BROWSER_EXECUTABLE` and passes it to Remotion's official `--browser-executable` option. Set this to your own compatible browser executable if necessary; the package contains no machine-specific browser path. Direct CLI calls can use the same official flag. This browser fallback is part of the recorded runtime evidence, not a claim that every host browser has been tested.
