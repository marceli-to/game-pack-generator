# Review: closer to the sheets, and optimisation (2026-11-19)

Scan of the generator code plus a close look at the guard (sheet, comparison sheet, three.js test load, the game's
screenshot `characters/report/wk1-01`). Nothing was changed. Tests: 94 passed, 1 skipped (103 s).

Each finding says whether it was **measured** or is a **judgement by eye**.

## Summary

The gap to the sheets is mostly not in the pipeline code. It is in three things the code neither measures nor
enforces:

1. **Too many, too narrow facets.** The sheet's limbs have 6–8 sides with broad flat planes; ours have 14–20.
2. **Too much shading contrast.** Our darkest olive is about 35 % as bright as our lightest; the sheet's is about 75 %.
3. **Smooth tubes where the sheet has kinks** (knees, cuffs, jaw planes), and the fit tool cannot add them.

Speed is not a problem anywhere (Blender starts in 0.5 s, the slowest step is the fit at ~20 s). The useful
optimisation is in the GLB: fewer ring sides would roughly halve vertices and file size as a side effect.

## A. Closer to the sheets

### A1. Ring density: parts use 14–20 sides, the sheet uses 6–8 (highest value)

- **Measured:** tinfox `STYLE.md` §3 says "heads, limbs, torsos 8–12 sides". The guard's parts use 16 (torso,
  `rrect(seg=3)`), 14 (sleeves, legs), 16 (pads) and 20 (head, `N = 20`). 26 tinfox part scripts use these counts.
  Nothing in `check_part` or `validate` checks the guide.
- **By eye:** in the sheet a thigh shows about three planes from the front, a sleeve about three. In the three.js
  test load and in the game screenshot our figures show vertical stripes on every limb, the torso and the face.
  The stripes are the most visible difference in the game.
- PROGRESS already says this ("few, large, deliberate planes") and that guard v4 (more sides) "barely shows", but
  the parts were left at the v4 counts.
- **Test (cheap, no code):** copy the guard's body parts, set `seg=3` → `seg=1` (8 sides, a chamfered rectangle)
  and the head to 10–12 points, rebuild, and compare in three.js next to the sheet.
- **Code, if the test convinces:**
  - A soft `validate` rule: share of surface area in faces narrower than ~3 cm whose neighbour meets them at less
    than ~20° (a "banding" number), with a per-style limit.
  - A ring helper with unequal sides (broad front, back and side planes, narrow chamfers), since `P.ring` spaces
    points evenly and `P.rrect` rounds every corner alike.
- Side effect: about 5,650 → roughly 3,000 triangles for the guard (estimate).

### A2. Shading contrast is about three times the sheet's

- **Measured** (olive pixels, 5th to 95th percentile by brightness):
  - Sheet: `#515623` … `#6E7230`.
  - Our guard in the three.js viewer: `#292C04` … `#757B31`.
  - Palette cell 29 is `#666B32`, so the base colour is right; the spread comes from light and AO.
- Two sources, not separated yet:
  - `shading.ao` (tinfox: strength 1.0, floor 0.2, power 2, 0.3 m). Floor 0.2 lets a corner go to 20 %.
  - The light in `viewer/viewer.html`, and in the game (its screenshot is as dark in the shadows).
- **Test:** export the guard with AO strength 0.5 / floor 0.5 and view it under the game's light. If the game's
  light is the main cause, it is a brief for the game (more ambient / hemisphere light on figures), not a generator
  change.

### A3. Forms the sheet has and the lofts don't

**By eye**, from the guard sheet:

- Trousers widen to a knee break and taper into the boot; ours are straight tubes.
- The sleeve ends in a broad rolled cuff with a clear step; boots have a separate toe cap and a tall cuff.
- The face is a few planes (cheek, jaw, a flat chin); ours is a rounded superellipse.
- The cap is fuller and sits lower and further forward.

These are part-script work, and the reason the scripts miss them is A4.

### A4. Parts are written blind to the sheet

- **Measured in code:** `build_part` renders the part with a stick figure only. The sheet comes in later, in
  `compare_reference`, on the whole character. Ring numbers are typed in after reading a grid by eye (the measuring
  scripts live in `workspace/`, outside the repo).
- **Proposal 1: a `measure_reference` job.** From the reference crops it returns, per body region and height, the
  outline in metres: half width from the front view, front and back depth from the side view. Colour classes
  (already in `lib/fit.py`) separate the arm from the torso. The part author starts from those numbers, including
  the kinks.
- **Proposal 2: sheet outline in the part preview.** `build_part` takes the character's reference and draws the
  sheet's outline behind the part at the same scale.

### A5. `compare_reference` gives one number per view

- **Measured in code:** it returns the silhouette overlap per view, nothing per region. The model has to find the
  place of a mismatch by looking at a 1536 px sheet.
- **Proposal:** add a table per region and height: sheet width vs model width in cm, signed (and depth from the
  side view). The masks are already computed, so this is a few lines of numpy.
- PROGRESS records that Marcel's fidelity brief was not adopted because better measuring "would not model better".
  I disagree for this one point: signed centimetres per region are what a part script edit needs.

### A6. The comparison pose differs from the sheet's pose, and the fit compensates

- **Measured in code:** the comparison pose only turns the upper arms down (`pose_arms`). The fit then scales
  regions to raise the score.
- **By eye, on the guard's comparison sheet:** the sheet's legs stand apart at an angle and its elbows are bent;
  the model's legs are vertical and its arms straight. The red and blue areas at the legs and hands are pose, not
  form.
- **Risk:** part of the stored fit (for example "thighs 1.13× deeper", wider torso) may be the fit paying for the
  stance. I did not measure how much.
- **Proposal:** add leg spread and elbow bend to the comparison pose, searched like `arms_down_deg`, used for
  comparing only (nothing stored in the mesh).

### A7. Limits of the fit model (lower priority than A1–A5)

**Measured in code** (`lib/fit.py`, `core.json` `fit`):

- Three stations per region, so it cannot make a knee kink or a cuff step.
- Depth scales about y = 0, front and back together. A chest that should come forward also grows backward.
- No offsets: it cannot move a cap forward or pads up, and cannot change a length.
- It runs at 256 px, about 8–9 mm per pixel for a 1.9 m figure.

Possible extensions: five stations, separate front and back depth, one offset per region. Worth doing only after
A1 and A4, because the fit scales whatever facets the parts have.

## B. Optimisation

### B1. Flat shading doubles the vertex count (measured)

- Guard GLB: 5,654 triangles, 10,816 vertices, 40 bytes each = 433 KB of the 589 KB file.
- Fewer ring sides (A1) cuts this roughly in proportion.
- Further option, needs the game: drop `NORMAL` and let three.js shade flat (`flatShading: true`), with AO per
  vertex instead of per corner. Vertices could then be shared; I estimate about 3,000 for the guard. This is a
  brief for the game, and only worth it if file size or skinning cost matters again (the game said 5.5 MB is fine).

### B2. Palette material exports double-sided (measured)

- `export-report.json`: `M_Palette` has `double_sided: true`; `lib/palette.py` never sets backface culling.
- Every part must be a closed shell (hard rule), so single-sided is safe and lets the GPU cull back faces.
- One line in `palette_material`. Painted styles already export single-sided.

### B3. Seven shipped figures carry an old palette image (measured, harmless today)

- `export-report.json` says `valid_style: false` (rule `texture`) for guard, officer, rifle guard, worker and
  players 1, 2, 4. Their `character.blend` packs the palette from before the Snowfort cells.
- I compared the embedded images with `styles/tinfox/palette.png`: 10–33 cells differ, **none of them used** by
  that figure. So they render correctly.
- Two weaknesses:
  - `export` writes the GLB and returns `ok: true` with hard style violations (only a warning line).
  - A palette change does not reach an existing `character.blend` until it is re-assembled.
- **Proposal:** `export_glb` reloads the palette image from the style before exporting, and `export` fails on hard
  violations unless told otherwise.

### B4. Pipeline speed: nothing worth changing (measured)

- Blender start: 0.5 s with a character file. One process per job is fine.
- Slowest test: the fit (21 s, ~900 Workbench renders written to PNG and read back). A numpy rasteriser would make
  it several times faster, which only matters if A7 adds many parameters.
- The dev loop builds parts one after another; they could run in parallel. Seconds, not minutes.

### B5. Small things seen on the way

- `lib/render.py` `setup()` ends with a loop over images that does nothing (`pass`).
- `assemble.py` imports `bmesh` inside `skirt_weights`.
- `apply_roles` and `weight_nearest` loop per face / per vertex in Python; fine at these sizes.

## Suggested order

1. A1 test on the guard (8-sided rings, 10–12-point head) and A2 test (softer AO), side by side with the sheet in
   three.js. An hour or two, no pipeline code. This decides the rest. Step-by-step brief below.
2. B2 and B3 (small, safe).
3. A5, then A4 (`measure_reference`), then A6.
4. Rebuild the shared body parts with the new numbers; the figures share most parts, so one pass covers all nine.
5. A7 and B1's game-side option only if still needed.

## Brief: the guard test (step 1 of the order above)

Goal: one image that lets Marcel judge whether fewer, broader facets and softer shading bring the guard visibly
closer to its sheet. Findings only: nothing shipped changes.

**Rules**

- Work on copies. The shipped guard, its spec and the shared parts stay untouched (eight other figures use them).
- No changes to `core.json`, `STYLE.md`, `styles/tinfox/style.json` or any job code. If the test convinces, the
  rules change afterwards, the `.md` first.
- Don't hand anything to the game. Don't commit the test parts or the test style.

**Setup**

1. Test character `guard-8`: copy `specs/guard/` to `specs/guard-8/` (spec `name` → `guard-8`, same reference).
2. Copy the guard's five body part scripts in `workspace/tinfox/parts/` to new names and point the test spec at
   them:
   - `head-hero-square` → `head-hero-square-8`
   - `torso-jacket-hero` → `torso-jacket-hero-8`
   - `arms-sleeves-padded-hero` → `arms-sleeves-padded-hero-8`
   - `legs-trousers-hero` → `legs-trousers-hero-8`
   - `feet-boots-big-hero` → `feet-boots-big-hero-8`
   - Hair, cap, mittens and belt stay the shipped parts in round 1.
3. Drop `fit` from the test spec for the first build (the stored fit belongs to the old shapes); refit at the end.

**Round 1: facets (the quick version)**

- Torso, sleeves, legs, pads: 8 sides (`rrect(..., seg=1)` gives a chamfered rectangle; rings built with `n=14` or
  `n=16` → `n=8`).
- Head: 10–12 points per ring instead of 20. Keep the face features.
- Boots: single chamfers.
- Build: `(unset GPG_STYLE; .venv/bin/python workspace/lib4/run.py guard-8 --build --anim --export)`.
- Check that every edited script really changed: compare the built triangle counts with the guard's (a text
  replace that misses is silent).

**Round 2: planes placed like the sheet**

Look at each part against a crop of the sheet (`specs/guard/reference/turnaround.png`), front and side, and move
the ring points so the planes sit where the sheet's do:

- Thigh and sleeve: one broad front plane, one broad outer plane, narrow chamfers between them.
- Trousers: wider at the knee break, tapering into the boot (the sheet's leg is not a straight tube).
- Sleeve: a clear step at the rolled cuff.
- Jaw and chin: straight planes to a flat chin.
- At most three rounds; stop earlier if a round changes little.

**Round 3: shading**

- AO is a style setting, so it needs a test style: copy `styles/tinfox/` to `styles/tinfox-soft/` with
  `shading.ao` strength 0.5 and floor 0.5, and a copy of the test spec `guard-8-soft` with `style: tinfox-soft`.
- A style folder that is not in the root `STYLE.md` table may fail `tests/test_style_sync.py`. Run the tests only
  with the test style moved out again (the earlier test parked its temp style in `workspace/tinfox/smooth/temp/`;
  do the same afterwards).

**Checks**

- `validate`: no hard violations.
- `pose_test` on `guard-8`: look at elbows and knees in `walk`, `run`, `crouch` and `aim_2h`. Eight sides bend more
  coarsely than sixteen; report what it looks like, with the frames.
- `fit_to_reference` on the final shapes; note the scores before and after next to the shipped guard's
  (0.80 / 0.77 / 0.79).

**Deliver**

- One image, same camera and same light for all columns, front and three-quarter view, body and a head close-up:
  sheet | shipped guard | `guard-8` | `guard-8-soft`. The page `workspace/tinfox/smooth/compare.html` already shows
  several guards side by side with `?light=room|game|dusk|dark`; use `light=game`.
- A second image for the game's lighting question: shipped guard vs `guard-8-soft` under `light=dark`.
- Numbers per variant: triangles, vertices in the GLB, GLB size, the olive tone range (5th to 95th percentile, as
  in A2), fit scores.
- A short note in PROGRESS.md: what was built, where the images are, what Marcel is asked to decide. Marcel judges
  the look; don't call it closer or not on his behalf.

**Afterwards (only on Marcel's yes)**

Rebuild the shared parts under their real names, change the segment guide and the AO values in the tinfox
`STYLE.md` and `style.json`, re-export all nine figures, and hand them over with a brief.

## Not checked

- The game's lighting code (only one screenshot).
- `lib/anim.py` and `lib/paint.py` in detail; they don't bear on the sheet match for Tinfox.
- How much of each stored `spec.fit` is pose compensation (A6).
- Whether 8-sided limbs still deform acceptably at elbows and knees in the clips.
