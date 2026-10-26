from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/oled_retainer.step")
@glb(out="../GLB/oled_retainer.glb")
@stl(out="../STL/oled_retainer.stl",mesh_tolerance=0.0004)
@threemf(out="../3MF/oled_retainer.3mf",mesh_tolerance=0.0004)
def oled_retainer():
    self_check()
    shape=oled_retainer_shape()
    return print_pose(shape,"oled_retainer")
if __name__=="__main__":
    oled_retainer()

