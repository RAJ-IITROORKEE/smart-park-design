from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/exploded_status.step")
@glb(out="../GLB/exploded_status.glb")
def exploded_status():
    self_check()
    shape=product_shape(False,True)
    return shape
if __name__=="__main__":
    exploded_status()

