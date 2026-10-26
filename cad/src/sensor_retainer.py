from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/sensor_retainer.step")
@glb(out="../GLB/sensor_retainer.glb")
@stl(out="../STL/sensor_retainer.stl",mesh_tolerance=0.0004)
@threemf(out="../3MF/sensor_retainer.3mf",mesh_tolerance=0.0004)
def sensor_retainer():
    self_check()
    shape=sensor_retainer_shape()
    return print_pose(shape,"sensor_retainer")
if __name__=="__main__":
    sensor_retainer()

