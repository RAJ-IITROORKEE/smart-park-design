from cadgen import step, glb
from design import *
@step(out="../STEP/base.step")
@glb(out="../GLB/base.glb")
def base():
    self_check()
    shape=base_shape()
    return print_pose(shape,"base")
if __name__=="__main__":
    base()

