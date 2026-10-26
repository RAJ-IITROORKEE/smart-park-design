# Local SmartPark toolchain

The parent tools folder holds installed support runtimes separately from the final design. It contains Copperhead, KiCad helper configuration, CAD and DfAM Python environments, FreeRouting and SolidCraft.

## Active project paths

The local Copperhead MCP repository and helper scripts now point at this retained SmartPark-XIAO-HCSR04-RevD-Final folder. SolidCraft's allowed directory now points at its cad subfolder. Restart or reconnect those MCP servers before using them so an already running server does not retain the removed legacy path.

The final models were generated with cadgen 0.7.10 and build123d 0.11.1, and are viewed through Text-to-CAD. The editable mechanical sources are Python files under cad/src. They are not SolidCraft native history documents.

## Rebuild and documentation

Native PCB commands require the matching KiCad Python environment. CAD builds and preview model exports require the retained cadenv interpreter; render_preview_images.py uses Playwright from that environment. The Word guide builder uses the bundled Codex document Python runtime with python-docx and Pillow.

Run scripts/build_delivery_guide.py from the design root to regenerate the guide and convenience copies. The guide builder preserves the existing native design. scripts/build_preview_models.py exports enclosure only assemblies and a PCB GLB from the frozen STEP geometry. scripts/verify_delivery.py checks hashes, copies, local Markdown targets and runtime arithmetic.

The packaged LibreOffice renderer was unavailable on this Windows host. The guide was rendered with an isolated hidden Microsoft Word instance, then the PDF pages were rasterized and visually reviewed. Only the requested final DOCX and Markdown are shipped; temporary PDF and page images were removed after review.

## Historical reports

Some retained verification JSON files record the original revision-d working path. They are evidence of checks on those files at that time, not live file links. Their hashes bind the unchanged geometry retained here. Sources and rebuild tools use project relative paths where practical; installed tool paths are specific to this workstation.
