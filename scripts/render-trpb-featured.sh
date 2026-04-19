#!/usr/bin/env bash
set -euo pipefail

mamba run -n pymol-render pymol -cq scripts/render-trpb-featured.pml

python - <<'PY'
from PIL import Image, ImageFilter

src = "assets/images/posts/trpb-local-fitness-diffusion/trpb-5e0k-ribbon-featured@2x.png"
out = "assets/images/posts/trpb-local-fitness-diffusion/trpb-5e0k-ribbon-featured.png"

im = Image.open(src).convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
im = Image.alpha_composite(bg, im)
im = im.resize((1200, 627), Image.Resampling.LANCZOS)
im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=45, threshold=3))
im.convert("RGB").save(out, optimize=True, quality=95)
PY

rm -f 5e0k.cif assets/images/posts/trpb-local-fitness-diffusion/trpb-5e0k-ribbon-featured@2x.png
