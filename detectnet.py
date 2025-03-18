#!/usr/bin/env python3

import sys
import argparse

from angle_calculations import *
from angle_display import *
from Focuser import *

from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput, Log, cudaAllocMapped, cudaCrop, cudaResize, cudaConvertColor

WIDTH = 2432
HEIGHT = 2048

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, 
                                 epilog=detectNet.Usage() + videoSource.Usage() + videoOutput.Usage() + Log.Usage())

parser.add_argument("input", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.3, help="minimum detection threshold to use")
parser.add_argument('--bus', type=int, default=7, help='Bus integer value')
parser.add_argument('--ptz', action='store_true', help='PTZ boolean flag')
parser.add_argument('--flip-output', type=int, default=180, help='Flip the output image by 180 degrees')
parser.add_argument('--model', type=str, default='models/drone/ssd-mobilenet.onnx', help='Path to the model file')
parser.add_argument('--labels', type=str, default='models/drone/labels.txt', help='Path to the labels file')
parser.add_argument('--input-width', type=int, default=2432, help='Input width of the video stream')
parser.add_argument('--input-height', type=int, default=2048, help='Input height of the video stream')


try:
	args = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

TEST_PTZ_SUPPORT = args.ptz

# create video sources and outputs
input = videoSource(args.input, argv=sys.argv)
output = videoOutput(args.output, argv=sys.argv)

# hardcoded object detection network parameters
net = detectNet(model=args.model, labels=args.labels,
                input_blob="input_0", output_cvg="scores", output_bbox="boxes",
                threshold=args.threshold)

# Initialize real time angle display
rtpA = RealTimeAnglePlotting()

# Update angles
def update_3d_visualization(angles):
    rtpA.set_angles(angles)

# Send the angular coordinates to the PTZ support after converting them to the
# appropriate format
def angle2PTZ(focuser, elevation, azimut):
    X_angle, Y_angle = azimut, elevation
    if azimut > 0:
        Y_angle = 180 - elevation
        X_angle = 180 - azimut
    else:
        X_angle = azimut * -1
        
    #print("X_angle : {:.2f}, Y_angle : {:.2f}".format(X_angle, Y_angle))
    #print("azimut : {:.2f}, elevation : {:.2f}".format(azimut, elevation))
    focuser.set(Focuser.OPT_MOTOR_X, int(X_angle))
    focuser.set(Focuser.OPT_MOTOR_Y, int(Y_angle))

def main_loop():
    focuser = Focuser(args.bus)
    focuser.set(Focuser.OPT_MODE,0x0001)
    
    CYCLE_LOOP = 10
    CYCLE = 0
    
    # process frames until EOS or the user exits
    while True:
        # capture the next image
        img_input = input.Capture()

        if img_input is None: # timeout
            continue

        # crop left and right black bands
        roi = (192, 0, 2240, 2048) #left top right bottom
        img = cudaAllocMapped(width=roi[2]-roi[0], height=roi[3]-roi[1], format=img_input.format)
        cudaCrop(img_input, img, roi)

        # detect objects in the image (with overlay)
        detections = net.Detect(img, overlay=args.overlay)

        # print the detections
        #print("detected {:d} objects in image".format(len(detections)))

        # compute angle coordinates of all detected objects
        angles = []
        CYCLE += 1
        for detection in detections:
            coord_x, coord_y = detection.Center[0], detection.Center[1]
            elevation = get_elevation(coord_x, coord_y, WIDTH, HEIGHT)
            azimut = get_azimut(coord_x, coord_y, WIDTH, HEIGHT)
            angles.append((elevation, azimut))
            #print(" Class N°" + str(detection.ClassID) + " ==> elevation : {:.2f}, azimut : {:.2f}".format(elevation, azimut))

        if CYCLE >= CYCLE_LOOP:
            CYCLE = 0
            if TEST_PTZ_SUPPORT and angles:
                angle2PTZ(focuser, angles[0][0], angles[0][1])

        # update angles
        update_3d_visualization(angles)

        # resize the processed image
        img_output = cudaAllocMapped(width=700, height=700, format=img.format)
        cudaResize(img, img_output)

        # render the image
        output.Render(img_output)

        # update the title bar
        output.SetStatus("{:s} | Network {:.0f} FPS".format(args.network, net.GetNetworkFPS()))

        # print out performance info
        #net.PrintProfilerTimes()
  
        # exit on input/output EOS
        if not input.IsStreaming() or not output.IsStreaming():
            break


# Start the main loop in a seperate thread
import threading
threading.Thread(target=main_loop, daemon=True).start()

# Start the visualization of angular coordinates
plt.show()
