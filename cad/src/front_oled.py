from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/front_oled.step")
@glb(out="../GLB/front_oled.glb")
def front_oled():
    self_check()
    shape=panel_shape(True)
    return print_pose(shape,"front_oled")
if __name__=="__main__":
    front_oled()

