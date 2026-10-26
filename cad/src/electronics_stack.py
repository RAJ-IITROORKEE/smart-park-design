from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/electronics_stack.step")
@glb(out="../GLB/electronics_stack.glb")
def electronics_stack():
    self_check()
    shape=electronics_shape()
    return shape
if __name__=="__main__":
    electronics_stack()

