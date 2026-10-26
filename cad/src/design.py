"""SmartPark Rev D parametric mechanical pilot; millimetres, Z up."""
from __future__ import annotations
from pathlib import Path
import json, math
from cadgen import build123d as bd
from cadgen import read_step

ROOT=Path(__file__).resolve().parents[1]
W,L,H,T=70.0,66.0,48.0,2.4
D=H-44.0
CLIP_T=1.6
HOOK_SHIFT=-4.8
PCB_Z=21.5
COPPER_SEAT_LIFT=0.035
XIAO_HEADER_AIR_GAP=0.6
MOUNTS=[(-28.5,-22),(28.5,-22),(-28.5,22),(28.5,22)]
SENSOR_Y=17.5
CAN_PITCH=26.0
OLED_DZ=3.0
OLED_ACTIVE_Z=24.6+OLED_DZ
PCB_STEP=ROOT.parents[0]/"outputs"/"board.step"

def box(x,y,z,dx,dy,dz):
    return bd.Pos(x,y,z)*bd.Box(dx,dy,dz,align=(bd.Align.MIN,)*3)

def cyl(x,y,z,d,h):
    return bd.Pos(x,y,z)*bd.Cylinder(d/2,h,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))

def rounded(w,l,h,z=0,r=3,x=0,y=0):
    return bd.Pos(x,y,z)*bd.extrude(bd.RectangleRounded(w,l,r),amount=h)

def named(s,n,c):
    s.label=n; s.color=bd.Color(c); return s

def tooth(y):
    profile=bd.Plane.XZ*bd.Polygon((32.1,28.0+D+HOOK_SHIFT),(33.5,29.4+D+HOOK_SHIFT),(33.5,30.4+D+HOOK_SHIFT),(32.1,30.4+D+HOOK_SHIFT),align=None)
    return bd.Pos(0,y-3.5,0)*bd.extrude(profile,amount=7,dir=(0,1,0))

def base_shape():
    s=rounded(W,L,H,r=4)-rounded(W-2*T,L-2*T,H+1,z=T,r=1.6)
    # Four cantilever release windows are on the sides, away from the OLED panel.
    for side in (-1,1):
        for y in (-14,14):
            s-=box(32.3 if side>0 else -36,y-4.1,27.7+D+HOOK_SHIFT,3.7,8.2,3.0)
    # Flat-wall bosses leave the battery footprint unobstructed.
    for x,y in MOUNTS:
        s+=cyl(x,y,2.2,5.0,PCB_Z-2.2)
        s-=cyl(x,y,PCB_Z-7,2.05,8.6)
    # Replaceable acoustic mask: no HC-SR04 mounting-hole pattern is assumed.
    s-=rounded(56.4,26.4,1.25,z=-.05,r=2,y=SENSOR_Y)
    s-=rounded(46.4,20.8,4,z=-.5,r=.6,y=SENSOR_Y)
    for x in (-25,25):
        s+=cyl(x,SENSOR_Y,1.2,5,12.9)
        s-=cyl(x,SENSOR_Y,1.1,1.65,13.7)
    for x in (-23.1,21.5):
        s+=box(x,7.5,2.4,1.6,20,10.1)
    # Pouch tray: 52 x35 clear, 1mm foam and a removable hook-and-loop strap.
    for x in (-27.8,26):
        s+=box(x,-28.5,2.3,1.8,35,2.0)
    for y in (-30.3,6.5):
        s+=box(-28,y,2.3,56,1.8,2)
    for x in (-31.4,26.2):
        a=box(x,-16.5,2.2,5.2,10,5.4)
        a-=box(x-.1,-14.7,3.5,5.4,6.4,2.2)
        s+=a
    # Modular aisle-facing OLED/blank panel.
    s-=box(-19,-35,8.8,38,6,34.8)
    for x in (-24,24):
        b=bd.Pos(x,-33,25)*bd.Rot(90,0,0)*bd.Cylinder(3,5.5,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MAX))
        s+=b
        s-=bd.Pos(x,-35,25)*bd.Rot(-90,0,0)*bd.Cylinder(.85,8,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    # USB opening is resized from the frozen electronics interface on regeneration.
    interface=ROOT.parent/"docs"/"mechanical-interface.json"
    usb=json.loads(interface.read_text()).get("usb",{}) if interface.exists() else {}
    cx=usb.get("case_x",0); cz=usb.get("case_z",36.5)
    s-=box(cx-7,29.8,cz-3.8,14,5,7.6)
    # Mount ears carry the main shell, not the snap lid.
    for side in (-1,1):
        for y in (-21,21):
            ear=rounded(14.4,12,3,z=H-.6,r=2,x=side*39.8,y=y)
            if side>0:
                poly=bd.Plane.XZ*bd.Polygon((32.8,H-14),(44,H-2.1),(44,H-.5),(32.8,H-.5),align=None)
            else:
                poly=bd.Plane.XZ*bd.Polygon((-32.8,H-14),(-44,H-2.1),(-44,H-.5),(-32.8,H-.5),align=None)
            gus=bd.Pos(0,y-4,0)*bd.extrude(poly,amount=8,dir=(0,1,0))
            s+=ear+gus
            s-=cyl(side*41,y,H-13,4.5,18)
    # Bottom RGB pixel shines downward through a straight removable light pipe.
    s-=cyl(29,0,-1,3.3,5)
    s-=box(-28.2,-34,4.8,56.4,1.6,40.4)
    s-=bd.Pos(31,0,40)*bd.Rot(0,90,0)*bd.Cylinder(3.3,7,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    return named(s.clean(),"Main shell - indoor pilot","#233442")

def lid_shape():
    s=rounded(W,L,T,z=H,r=4)
    lip=rounded(64.6,60.6,4,z=H-4,r=1.4)-rounded(61.4,57.4,5,z=H-4.5,r=.4)
    for side in (-1,1):
        for y in (-14,14):
            lip-=box(29.8 if side>0 else -33.8,y-4.2,H-5,4,8.4,6)
    s+=lip
    for side in (-1,1):
        for y in (-14,14):
            tab=box(32.1-CLIP_T,y-3.5,26.4,CLIP_T,7,H+.4-26.4)+tooth(y)
            if side<0: tab=bd.mirror(tab,about=bd.Plane.YZ)
            s+=tab
        for y in (-21,21):
            s-=box(32.3 if side>0 else -48,y-6.3,H-1,15.7,12.6,4)
    return named(s.clean(),"Snap lid - four release clips","#C9D5DB")

def mask_shape():
    s=rounded(56,26,1.2,r=1.8,y=SENSOR_Y)+rounded(46,20.4,1.0,z=1.2,r=.4,y=SENSOR_Y)
    for x in (-CAN_PITCH/2,CAN_PITCH/2):
        s-=cyl(x,SENSOR_Y,-1,17,5)
    for x in (-25,25):
        s-=cyl(x,SENSOR_Y,-1,2.2,5)
        s-=cyl(x,SENSOR_Y,1.19,5.4,1.4)
    return named(s.clean(),"Replaceable HC-SR04 acoustic mask - nominal 26mm pitch","#233442")

def sensor_retainer_shape():
    s=rounded(53,23,1.6,z=14.1,r=1,y=SENSOR_Y)-rounded(42,17.6,3,z=13.5,r=.5,y=SENSOR_Y)
    s-=box(-7,5.5,13.5,14,6,3)
    for x in (-25,25): s-=cyl(x,SENSOR_Y,13.5,2.2,3)
    return named(s.clean(),"HC-SR04 edge retainer","#71818B")

def light_pipe_shape():
    s=cyl(29,0,0,3,20)+cyl(29,0,2.4,4.5,1.2)
    return named(s.clean(),"Clear PETG status light pipe","#77D5DE")

def panel_shape(oled):
    s=box(-28,-34.8,5,56,2.4,40)
    s+=box(-18.6,-32.4,9.2,37.2,1.7,34)
    if oled:
        s-=box(-12.2,-35,OLED_ACTIVE_Z-6.75,24.4,6,13.5)
        s-=box(-14.3,-32.5,8.1+OLED_DZ,28.6,2.2,28.6)
        for x in (-14,12.4):
            for z in (8.5+OLED_DZ,35+OLED_DZ):
                s+=box(x,-32.5,z,1.6,3.0,1.6)
        for x in (-16.5,16.5):
            for z in (11.5,41.0):
                s+=box(x-2.2,-32.4,z-2.2,4.4,4.2,4.4)
                s-=bd.Pos(x,-32.4,z)*bd.Rot(-90,0,0)*bd.Cylinder(.85,5,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    for x in (-24,24):
        s-=bd.Pos(x,-35,25)*bd.Rot(-90,0,0)*bd.Cylinder(1.1,5,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    return named(s.clean(),"OLED front panel" if oled else "Blank front panel","#318D9B" if oled else "#233442")

def oled_retainer_shape():
    s=box(-20,-28.2,9.2,40,1.6,34.1)
    s-=box(-12.6,-29,13,25.2,4,24)
    s-=box(-6,-29,36,12,4,8)
    for x in (-16.5,16.5):
        for z in (11.5,41):
            s-=bd.Pos(x,-29,z)*bd.Rot(-90,0,0)*bd.Cylinder(1.1,4,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    return named(s.clean(),"OLED edge retainer","#71818B")

def electronics_shape(exploded=False,oled=False):
    children=[]
    if PCB_STEP.exists():
        pcb=read_step(PCB_STEP)
        # A board export transform is frozen by the electrical generator.
        interface=ROOT.parent/"docs"/"mechanical-interface.json"
        cfg=json.loads(interface.read_text()) if interface.exists() else {}
        tr=cfg.get("step_to_case",[-31,25,PCB_Z+COPPER_SEAT_LIFT])
        rot=cfg.get("step_rotation",[0,0,0])
        pcb=pcb.moved(bd.Location(tuple(tr),tuple(rot)))
        children.append(pcb)
    else:
        raise FileNotFoundError(f"Export the reviewed native carrier first: {PCB_STEP}")
    kit=read_step(ROOT/"imported"/"xiao-s3-wio-sx1262-stack.step")
    kit=kit.moved(bd.Location((0,14.5,39.2+COPPER_SEAT_LIFT+XIAO_HEADER_AIR_GAP)))
    kit.label="Official Seeed XIAO S3 and Wio-SX1262 stack"
    children.append(kit)
    for x in (-7.62,7.62):
        children.append(named(box(x-1.27,14.5-8.89,23.1+COPPER_SEAT_LIFT,2.54,17.78,8.5),"8.5mm female header body reference","#20282F"))
        children.append(named(box(x-1.27,14.5-8.89,31.6+COPPER_SEAT_LIFT,2.54,17.78,2.5),"2.5mm male header shoulder reference","#20282F"))
        for i in range(7):
            children.append(named(box(x-.3,14.5-7.62+2.54*i-.3,19+COPPER_SEAT_LIFT,.6,.6,18.1),"Socket pin reference","#C4A45E"))
    # Commodity sensor reference: manufacturer overall dimensions; can pitch is a fit assumption.
    sensor=named(box(-22.5,7.5,12.5,45,20,1.6),"HC-SR04 PCB reference","#21577D")
    children.append(sensor)
    for i,x in enumerate((-13,13),1):
        can=cyl(x,SENSOR_Y,.5,16,12)-cyl(x,SENSOR_Y,.4,13.8,.8)
        children.append(named(can,"HC-SR04 transducer "+str(i),"#B9C2C6"))
        children.append(named(cyl(x,SENSOR_Y,.65,13.5,.08),"Acoustic mesh "+str(i),"#27353F"))
    children.append(named(box(-5,7,14.1,10,2.5,4),"HC-SR04 right-angle harness envelope","#20282F"))
    children.append(named(rounded(51,34,5,z=3.4,r=1,x=0,y=-11),"Protected LiPo 51x34x5 reference","#8A99A4"))
    children.append(named(box(-5,-17,9,10,12,.6),"Nonconductive battery strap reference","#D9A35F"))
    sma=bd.Pos(30,0,40)*bd.Rot(0,90,0)*bd.Cylinder(3.175,13,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    nut=bd.Pos(35,0,40)*bd.Rot(0,90,0)*bd.Cylinder(4.9,1.5,align=(bd.Align.CENTER,bd.Align.CENTER,bd.Align.MIN))
    children.append(named(sma+nut,"SMA bulkhead pigtail reference - antenna not shown","#C4A45E"))
    if oled:
        children.append(named(box(-13.9,-29.5,8.75+OLED_DZ,27.8,1.2,27.5),"GoldenMorning OLED PCB reference","#21577D"))
        children.append(named(box(-13,-31.8,17.3+OLED_DZ,26,2.3,14.6),"OLED glass reference","#071E29"))
        children.append(named(box(-10.87,-31.9,19.17+OLED_DZ,21.74,.05,10.86),"OLED active-area reference","#21B4BD"))
        children.append(named(box(-5,-28.3,34.5+OLED_DZ,10,11.3,2.54),"OLED header/cable keepout","#20282F"))
    if exploded:
        children=[s.moved(bd.Location((0,0,25))) if "HC-SR04" not in s.label else s for s in children]
    return bd.Compound(children=children,label="Electronics stack - reference components marked")

def product_shape(oled=False,exploded=False):
    children=[base_shape(),mask_shape(),sensor_retainer_shape(),electronics_shape(oled=oled),light_pipe_shape()]
    lid=lid_shape()
    panel=panel_shape(oled)
    if exploded:
        lid=lid.moved(bd.Location((0,0,45)))
        panel=panel.moved(bd.Location((0,-28,0)))
        children[1]=children[1].moved(bd.Location((0,0,-18)))
        children[2]=children[2].moved(bd.Location((0,0,14)))
        children[3]=children[3].moved(bd.Location((0,0,22)))
    children.extend([lid,panel])
    if oled:
        ret=oled_retainer_shape()
        if exploded: ret=ret.moved(bd.Location((0,-15,0)))
        children.append(ret)
    return bd.Compound(children=children,label="SmartPark OLED" if oled else "SmartPark status")

def print_pose(s,name):
    if name=="lid": s=s.moved(bd.Location((0,0,0),(180,0,0)))
    elif name in ("front_oled","front_blank","oled_retainer"):
        s=s.moved(bd.Location((0,0,0),(90,0,0)))
    bb=s.bounding_box()
    return s.moved(bd.Location((-bb.min.X,-bb.min.Y,-bb.min.Z)))

def coupon_shape():
    s=box(0,0,0,46,22,2.4)
    for i,d in enumerate((16.6,17.0)):
        s-=cyl(12+i*22,11,-1,d,5)
    # Print the actual lid separately to test latch release/flex on a short test-wall coupon.
    wall=box(0,21.5,0,46,2.4,22)
    for y in (0,):
        wall-=box(18.9,20.5,4.5,8.2,5,3)
    return named(s+wall,"Aperture and latch-window fit coupon","#71818B")

def self_check():
    assert W-2*T>62 and L-2*T>50
    assert PCB_Z-2.5>18.1
    assert CAN_PITCH-16>0
    assert 26-51/2>=.5
    hook_load_length=H+.4-(30.4+D+HOOK_SHIFT)
    assert 1.5*CLIP_T*1.4/hook_load_length**2<.01
    assert H+T==50.4
    return True

