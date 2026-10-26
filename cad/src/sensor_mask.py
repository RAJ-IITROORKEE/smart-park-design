from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/sensor_mask.step")
@glb(out="../GLB/sensor_mask.glb")
@stl(out="../STL/sensor_mask.stl",mesh_tolerance=0.0004)
@threemf(out="../3MF/sensor_mask.3mf",mesh_tolerance=0.0004)
def sensor_mask():
    self_check()
    shape=mask_shape()
    return print_pose(shape,"sensor_mask")
if __name__=="__main__":
    sensor_mask()

