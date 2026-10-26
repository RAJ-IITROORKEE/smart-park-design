from cadgen import step, glb
from design import *
@step(out="../STEP/lid.step")
@glb(out="../GLB/lid.glb")
def lid():
    self_check()
    shape=lid_shape()
    return print_pose(shape,"lid")
if __name__=="__main__":
    lid()

