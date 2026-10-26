from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/light_pipe.step")
@glb(out="../GLB/light_pipe.glb")
@stl(out="../STL/light_pipe.stl",mesh_tolerance=0.0004)
@threemf(out="../3MF/light_pipe.3mf",mesh_tolerance=0.0004)
def light_pipe():
    self_check()
    return print_pose(light_pipe_shape(),"light_pipe")
if __name__=="__main__":
    light_pipe()
