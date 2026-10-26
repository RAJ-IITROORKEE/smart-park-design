from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/product_status.step")
@glb(out="../GLB/product_status.glb")
def product_status():
    self_check()
    shape=product_shape(False)
    return shape
if __name__=="__main__":
    product_status()

