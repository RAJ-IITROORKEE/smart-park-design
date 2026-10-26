from cadgen import step, stl, glb, threemf
from design import *
@step(out="../STEP/fit_coupon.step")
@glb(out="../GLB/fit_coupon.glb")
@stl(out="../STL/fit_coupon.stl",mesh_tolerance=0.0004)
@threemf(out="../3MF/fit_coupon.3mf",mesh_tolerance=0.0004)
def fit_coupon():
    self_check()
    shape=coupon_shape()
    return print_pose(shape,"fit_coupon")
if __name__=="__main__":
    fit_coupon()

