# Subsystems

Electrical blocks grouped by the revision-d deterministic schematic generator.

## Controller stack

U1 represents the XIAO ESP32-S3 with Wio-SX1262 stacked above it. The carrier connects the XIAO outer header pads; the Wio radio signals remain internal to the stack.

## Battery harness

BT1 and J3 are the off-board protected LiPo and its JST-PH2 pigtail, wired to J4, a symbol for the XIAO underside BAT pads rather than a carrier connector.

## HC-SR04 interface

J1 carries 5V_SENSOR, TRIG, ECHO, and GND. U4 buffers the module echo to 3.3 V GPIO; XIAO D0/GPIO1 drives the trigger directly.

## 5V sensor supply

U2 boosts 3V3 to a GPIO4-enabled 5V_SENSOR rail for the sensor and optional RGB pixel, with TI reference feedback and bypassing.

## Optional OLED

J2 is a 4-pin 3.3 V I2C header with board pullups. The selected display is GoldenMorning GME12864-11 (Robu 617725); confirm the delivered module matches its drawing.

## Optional RGB

U3 shifts XIAO D6 data to switched 5V_SENSOR for the pixel. Pulldowns and a series resistor keep the pixel stable during power transitions.

## Bring-up test points

TP1–TP5 expose 3V3, GND, 5V_SENSOR, HC_ECHO, and ECHO_GPIO during controlled validation.
