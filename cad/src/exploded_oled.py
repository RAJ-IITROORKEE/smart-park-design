from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/exploded_oled.step")
@glb(out="../GLB/exploded_oled.glb")
def exploded_oled():
    self_check()
    shape=product_shape(True,True)
    return shape
if __name__=="__main__":
    exploded_oled()

