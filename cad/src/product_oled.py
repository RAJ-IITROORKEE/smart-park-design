from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/product_oled.step")
@glb(out="../GLB/product_oled.glb")
def product_oled():
    self_check()
    shape=product_shape(True)
    return shape
if __name__=="__main__":
    product_oled()

