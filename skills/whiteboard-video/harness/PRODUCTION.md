# Production harness: organic narrated whiteboard

These are reusable authoring and review requirements, not claims that the runtime automatically enforces visual quality. Apply PEN-SEMANTICS-CANVAS.md first for full films; select compatible D01–D11 mechanisms afterward. User overrides are explicit in the project brief. Never turn a single project's news claims, voice selection or duration into universal defaults.

## Inputs and handoffs

Brief → factual script → timed sentence cues → semantic visual groups → prepared assets and paths → animation timeline → rendered candidate → evidence-bound review → publishing package.

Required project records:
- Brief: topic, audience, language for voice/captions/review, aspect ratio, target duration, brand assets, engine, approval scope.
- Claim ledger: exact statement, primary source URL, publication date, event date, research cutoff, verified/uncertain/analysis status. Never reuse a past video's election results as current facts.
- Cue map: sentence ID, exact narration, audio start/end, visual group IDs, reveal mechanism, required/optional objects, draw/hold/transition windows.
- Asset manifest: identity, referenceOnly/runtimeAsset/orderedPaths/existingFinishedSnapshot role, provenance, rights status, recognizable subject, dimensions and anchors.
- Review: candidate hash, engine version, checked time windows, still inspection, continuous normal-speed motion viewing, actual listening, synchronization and owner acceptance recorded separately.

## Visual grammar: mandatory

P01. Apply DRAWING-STYLE.md (swaintalk-bold-flat-cartoon-v1): bold near-black contours, opaque saturated flat colors and expressive adult editorial cartoons. Believable structure permits caricature; named subjects retain recognizable identity. Thin pale line art, stick figures and dense painted scenes do not satisfy this default.
P02. Every complete spoken content sentence has at least one new relevant cartoon drawing, outline-traced subject, or pen-brush-revealed picture action timed to that sentence. Segment by spoken sentences, not subtitle fragments or paragraph-length audio files. Each sentence needs its own event ID and explicit subject/meaning; one event cannot cover an entire paragraph. Existing drawings may remain, but a static hold, caption, keyword card, camera move or unrelated decoration alone does not count. Related sentences may extend the same organic scene through new semantic objects/details; do not cut to a new page or reset the hand for every sentence. Hook sentences may instead use relevant footage; still photos use a pen-linked mask. Brand name/slogan is the explicit original-logo exception. If timing is insufficient, revise wording, voice timing or complete secondary detail; do not silently drop sentence coverage.
P03. Arrange unequal organic clusters on an extensible canvas. Vary scale, placement and drawing direction around semantic relationships. Do not make every stage a neat row, equal grid or repeated left-to-right checklist. Keep intentional whitespace and readable hierarchy.
P04. No visible 1–6 drawing-order numbers. Production IDs stay in metadata. Legitimate data values remain permitted.
P05. Use multiple purposeful marker colors, consistently across meanings. Do not force every object to blue. Background highlight colors are configurable; strokes have irregular but controlled edges, not perfect rounded rectangle pills. Stable seeded irregularity must not shimmer frame to frame.
P06. Pictures supplement drawings at comparable object scale, each tied to a specific spoken idea. Do not give a third-party photo an entire stage by default or use an unrelated photo as decoration. Required image coverage must be tracked explicitly.
P07. Every explicitly identified person, organization, brand and product must retain recognizable identity. Use the appropriate original mark, identity-preserving portrait or distinctive product form, grounded in project-supplied references. Consult real references for silhouette and distinctive details; never substitute a generic person or generic car. Avoid invented product features or depicting an illustration as documentary footage.

## Animation and timing: mandatory

P08. Pre-plan action order and the next pen destination. One continuous hand trajectory spans nearby strokes, words, arrows and objects. Contact during drawing, lift during travel, smooth acceleration, hold when useful. No per-object fade-out, offscreen reset or teleport. Exit only at a deliberate scene/segment boundary.
P09. Board text and vector arrows need real ordered paths when called handwritten. Captions are a separate readable screen-space layer and may be typed. Outline tracing, true handwriting, raster wipe and prebuilt placement must be labeled as different mechanisms.
P10. A generated board is a reference or finished image, not an editable stroke program. Prepare separate semantic groups, masks or paths for the chosen mechanism; never claim that a whole-image wipe proves handwriting. User-requested handwriting cannot silently downgrade to a wipe.
P11. Sync animation to the actual final narration audio. Let key objects appear near the relevant words and remain readable. If over budget, reduce complete secondary objects or redundant words; do not truncate required objects or use frantic pen speed. Regenerate timing after voice changes.
P12. Under the strict full-film profile, original photos/logos are revealed only by a local pen-linked brush mask. No pop/settle, automatic fade or hand placement. Keep original image identity and label the mechanism as raster brush reveal, not recovered drawing strokes. D06 remains a standalone placement recipe only. Generated photographic arms must not be described as real footage.
P13. Keep outline-then-letter-fill and outline-then-background-color as distinct recipes. Draw endpoint objects before curved connecting arrows; arrowheads must meet paths cleanly and not cross labels or subjects. Nodes can be illustrations or real images, not just colored boxes. Respect current routing limits.
P14. Infinite canvas may grow in any direction during explanation. Final long-canvas overview is specifically vertical and uses actual completed stage snapshots with frame/hash provenance. Preserve camera continuity. Do not invent historical stages, enlarge only the final page, or restore the rejected ten-stage continuous-tour effect.

## Engine and brand handoff

For full-film delivery, apply PRESENTATION.md and explicitly select OpenFilm, ChatCut or both; do not infer a platform from a prior project. Record exact positions and versions in the brief. This is an optional project-local integration, not a bundled dependency or a promise of native support. Keep world drawings/camera separate from fixed logo, subtitles and progress UI. Never expose local access tokens in public packages.

## Thumbnail and publishing

- Input: final topic, accurate title, approved artwork, original channel logo, output dimensions, placement choice.
- Output: upload-ready thumbnail, editable/generation source or prompt, title, description, chapters, sources and package manifest.
- SwainTalk profile confirmed in this production: recognizable editorial portraits/products, white ground, bold black short headline on yellow marker accent, red/cream channel logo at extreme bottom-right below the collar. This is a brand profile, not a universal illustration requirement. Use small edge padding, do not cut the logo or cover a face/collar; latest explicit placement overrides earlier proposals.
- Make narrowly scoped revisions and retain previous versions. Preserve the actual logo; generated redraws require visual comparison and must not be called pixel-identical composites.
- Descriptions may be energetic through concrete questions and stakes. If at least 150 English words are requested, count the main prose separately from chapters, links and hashtags. Match every promised topic to the video.
- No invented collapse, cancelled contracts, proven robot autonomy, election outcome or guaranteed investment return. Distinguish fact, company claim and prediction. Do not imply a midterm removes the president.
- Check current official YouTube community, election misinformation, advertiser suitability and discovery guidance when asked to assess publishing risk. Do not invent a forbidden-word list or guarantee reach/monetization. Ad restriction, policy removal and recommendation outcomes are different findings.
- Prepare upload files without publishing unless authorized. A disclaimer cannot repair a false statement in narration. Changes to spoken claims require updating voice, captions, timing and affected visual windows.

## Acceptance gates and failure handling

G1 Content: each material factual claim has evidence; uncertain claims qualified or removed. Missing source is a content issue, not a keyword issue.
G2 Coverage: every content sentence in the final narration inventory has a unique qualifying timed visual action and subject/meaning. No intentional-hold exemption. Run check_production.py in plan mode before batch rendering; missing cues block that batch, then delivery mode and actual per-sentence listening/viewing before acceptance.
G3 Assets: identities recognizable, sources recorded, drawable paths available for actual handwritten actions; missing inputs stop only the affected effect.
G4 Timing: required draw + travel + hold fits its cue window. No truncated object, jittery hand or repetitive disappearance.
G5 Layout: inspect full-resolution and small output; no collisions, equal-grid fatigue, accidental numbered sequence, hidden captions or logo.
G6 Continuity: watch cross-object, cross-stage and overview transitions continuously at normal speed; inspect contact points and matching reveal progress.
G7 Delivery: render/decode and audio checks bind to the exact candidate hash. Audio listening and picture-to-speech fit require actual review, not only ffprobe or stills. Report unchecked areas honestly.
G8 Publishing: thumbnail/title/description reflect the same candidate; chapter times match; count and save final copy; preserve evidence cutoff.

On failure return rule ID, affected cue/time, observed problem, evidence and minimum repair. Recheck changed windows after rerender. Never mark authoring rules as automatic checks merely because this document exists.

## Hook → spoken brand → illustrated explanation (mandatory)

H01. Start with 3–5 complete spoken sentences introducing today's topic, stakes or question. Each has topic-specific footage, cartoon action or a relevant image. No channel announcement, logo, watermark, slogan or branded opener during this hook. A title alone does not satisfy the visual mapping.
H02. Only after the last hook sentence completes, enter the SwainTalk brand station, then the body. Keep the hook on the global audio clock. Do not force old narration/caption timings to survive a changed opening; regenerate affected audio, subtitles, chapters and progress.
B01. The intro speaks “SwainTalk. Follow the tech. Follow the money.” using the selected voice. Align channel-name audio to readable original Logo and each slogan phrase to its visible text. These words must actually exist in the final narration; an unrelated topic voice-over under the logo does not satisfy this requirement.
B02. Use final audio phrase timings, not assumed 0–4 second brand presets. Retain readable brand content throughout the corresponding spoken phrase and exit only after the complete slogan and natural release. Outro brand speech, when present, follows the same alignment rule. Do not manufacture audio approval from metadata.

Project handoff: `production.json` + hashed `narration.json` (final audio identity and all complete sentence cues) + visual events/asset identities + brand phrase windows. See [executable contract](../../../docs/PRODUCTION-CHECK.md). `presentation.json` must reference `production_path`; presentation validation also runs these checks, so omitting the production map cannot produce a configuration PASS.

Plan checks enforce declared counts, mappings, timing and source identities. Delivery checks additionally require candidate/timeline identities and actual review records bound to narration, brand timing and visual events. They do not watch/listen or judge semantic similarity themselves. Never fabricate PASS rows; unchecked or failing rows keep delivery unaccepted. A sentence inventory must be checked against the full actual narration; combining three sentences into one record is not compliance.

## Full-stroke, literal-entity and world-canvas contract

Execute [PEN-SEMANTICS-CANVAS](PEN-SEMANTICS-CANVAS.md): every board element including text and color has a pen program; named entities have references; world-space bounds and continuous camera routes replace fixed slots/pages. Run production v2 plan/delivery checks. Old automatic fill and fade recipes cannot satisfy this stricter full-film profile.
