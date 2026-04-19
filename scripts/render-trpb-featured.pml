fetch 5e0k, async=0
remove solvent
hide everything
show cartoon

bg_color white
set ray_opaque_background, on
set orthoscopic, on
set antialias, 3
set ray_trace_mode, 0
set ray_trace_gain, 0.08
set ray_shadow, on
set depth_cue, 0
set ambient, 0.40
set direct, 0.72
set reflect, 0.18
set specular, 0.22
set shininess, 32
set cartoon_fancy_helices, 1
set cartoon_smooth_loops, 1
set cartoon_flat_sheets, 0
set cartoon_sampling, 16

set_color accent_blue, [0.220, 0.240, 0.960]
set_color soft_gray, [0.76, 0.78, 0.82]
set_color pale_gray, [0.88, 0.90, 0.93]

color pale_gray, all
color soft_gray, chain A+C+E+G+I+K
color accent_blue, chain B
set cartoon_transparency, 0.72, not chain B

orient chain B
turn x, 10
turn y, -28
turn z, -5
zoom chain B, 4.2

ray 1600, 836
png assets/images/posts/trpb-local-fitness-diffusion/trpb-5e0k-ribbon-featured@2x.png, dpi=320
quit
