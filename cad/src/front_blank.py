from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/front_blank.step")
@glb(out="../GLB/front_blank.glb")
@stl(out="../STL/front_blank.stl",mesh_tolerance=0.0004)
@threemf(out="../3MF/front_blank.3mf",mesh_tolerance=0.0004)
def front_blank():
    self_check()
    shape=panel_shape(False)
    return print_pose(shape,"front_blank")
if __name__=="__main__":
    front_blank()

