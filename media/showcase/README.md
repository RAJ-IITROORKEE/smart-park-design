# SmartPark Revision D showcase

The showcase uses the repository’s actual CAD and PCB renders. The MP4 is 20.5 seconds, landscape, with a silent 20.5-second GIF preview (800 × 450, 7 fps, 2.2 MB) and a poster image.

## Files

- [Video](brag.mp4)
- [Poster](brag.jpg)
- [Silent GIF preview](preview.gif)
- [Plan and storyboard](brag-plan.md)
- [Composition brief](composition-brief.md)
- [Share copy](share-copy.txt)
- [HyperFrames composition source](composition/index.html)

## Rebuild

Run these commands from the SmartPark repository root in PowerShell. Rebuilding requires Node.js/npx plus FFmpeg and FFprobe on PATH; the supplied composition was rendered with HyperFrames 0.8.205.

    Push-Location media/showcase/composition
    npx --yes hyperframes check
    npx --yes hyperframes preview --background
    npx --yes hyperframes render --quality delivery --output ../brag.mp4
    Pop-Location

After rendering, extract a settled hero frame and bake it into frame 0:

    ffmpeg -y -ss 1.4 -i media/showcase/brag.mp4 -frames:v 1 -update 1 -q:v 2 media/showcase/brag.jpg
    ffmpeg -y -i media/showcase/brag.mp4 -i media/showcase/brag.jpg -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart media/showcase/brag.poster.mp4
    Move-Item -LiteralPath media/showcase/brag.poster.mp4 -Destination media/showcase/brag.mp4 -Force

Build the silent full-length GIF preview from the finished MP4:

    ffmpeg -y -i media/showcase/brag.mp4 -t 20.5 -vf "fps=7,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -an -loop 0 media/showcase/preview.gif

## Asset credits

Music: “Happy Beats & Business Moves Vol. 12” by Sascha Ende, from [ende.app](https://ende.app/en/song/12881-happy-beats-business-moves-vol-12). The track page identifies the license as [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); this showcase credits the artist in the end card and share copy.

Sound effects: Kenney CC0 effects from the bundled /brag skill assets. Product and PCB imagery is copied from the repository’s own CAD renders: previews/05-images/ and previews/01-pcb/.

The composition’s local media dependencies are kept under composition/assets/; HyperFrames itself runs through npx and installs no node_modules in this design repository.
