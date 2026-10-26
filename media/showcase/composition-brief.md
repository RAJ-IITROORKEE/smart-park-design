# HyperFrames Composition Brief: SmartPark Revision D

## Objective

Create a polished landscape showcase of the actual SmartPark Revision D indoor parking-sensor pilot design. Use supplied CAD and PCB renders as the product, with no fabricated hardware imagery and no narration.

## Output

- Composition directory: media/showcase/composition/
- Rendered video: media/showcase/brag.mp4
- Poster frame: media/showcase/brag.jpg, baked into video frame 0
- Silent looping preview: media/showcase/preview.gif
- Format: landscape — 1920 × 1080 at 30 fps
- Duration: 20.5 seconds

## Source material

- Project root: this SmartPark design repository.
- Product description and claim boundaries: README.md; detailed pilot and fit assumptions in docs/SmartPark-RevD-Build-Guide.md.
- Main CAD sources: previews/05-images/product_oled.png, product_status.png, electronics_stack.png, exploded_oled.png, parts-review.png, and pcb-only.png.
- PCB imagery: previews/01-pcb/pcb-front.png and pcb-back.png.
- Product name: SmartPark Revision D.
- Core angle: one indoor parking bay, measured from a ceiling-mounted pilot sensor.
- Copy that must appear:
  - “One bay. Read from above.”
  - “Designed for indoor ceilings up to 2.8 m.”
  - “OLED · 7 printed parts”
  - “Status-only · 6 printed parts”
  - github.com/RAJ-IITROORKEE/smart-park-design
  - “Rev D · indoor pilot”
  - “Unbuilt design · firmware and gateway not included”

## Creative direction

- Tone preset: polished.
- Creative direction: measured engineering product film.
- Angle and storyboard: follow brag-plan.md.
- Hook: the real OLED case render beside “One bay. Read from above.”
- Avoid generic SaaS language, invented sensors or working-display content, faux deployment scenes, and unsupported performance claims.

## Visual identity

- Background: #EEF3F5
- Text: #183849
- Accent: #168B8D
- Supporting text: #395461
- Display type: Playfair Display 900
- Body type: Montserrat 400/700
- Metadata: IBM Plex Mono 400/700
- Source-specific visual assets: all product and board images copied from the SmartPark repository into composition/assets/images/.
- Composition style: light, technical, calm; sparse measurement rules and layout guides frame the real imagery.

## Storyboard summary

1. One bay — 3.2s — OLED product render and hook.
2. Ceiling mount — 3.9s — status-only enclosure and the 2.8 m design envelope.
3. Inside the enclosure — 4.4s — exploded render, electronics stack, module labels.
4. Two case variants — 4.2s — OLED and status-only renders with 7/6 printed-part counts.
5. Files to build from — 4.8s — real PCB copper views, repository CTA, unbuilt-design note.

## Audio

- Bed: assets/music/happy-beats-business-moves-vol-12-by-ende-dot-app.mp3, Vol. 12 by Sascha Ende.
- License and attribution: Creative Commons Attribution 4.0; music credit is included on the end card and in media/showcase/README.md. Source: https://ende.app/en/song/12881-happy-beats-business-moves-vol-12.
- Cue source: assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json; use strong cues near 8.74s, 13.11s, and 17.47s. No beat snap may shorten readable holds.
- SFX: selected after the visual timing, from bundled CC0 Kenney interface/impact assets; keep them sparse and quiet.
- Audio-reactive: none. Music informs pacing and transitions; the product imagery stays calm and legible.

## HyperFrames instructions

Use one standalone composition in composition/index.html, one paused seekable GSAP timeline, and finite clips timed to the 20.5-second root. Use the supplied assets only for product or board imagery. Keep all required text readable, preserve the caveat that this is an unbuilt indoor pilot, and run npx hyperframes check before final render.
