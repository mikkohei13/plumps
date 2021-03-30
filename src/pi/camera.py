
import os
import cv2
import picamera
from picamera.array import PiRGBArray
import time
from time import sleep
import io
#from PIL import Image
#import numpy
from datetime import datetime

import analyze
import classify

'''
picamera.exc.PiCameraMMALError: Failed to enable connection: Out of resources
->
ps aux | grep -i python
kill -9 <pid>
'''

def saveFrame(cropFrame, imagesFolder, datetimeStr, label, prob):
    cropFilePath = "./" + imagesFolder + "/" + datetimeStr + "_" + label + "_" + str(prob) + ".jpg"
    cv2.imwrite(cropFilePath, cropFrame)
    print("wrote frame", cropFilePath)

def main():

    # Setup
    imagesFolder = "crops"
    havePreviousFrame = False

    sleepSeconds = 2
    frameRate = 3
    x = 0
    width = 1920
    height = 1080

    print("Starting in " + str(sleepSeconds) + " seconds")

    # Based on https://www.raspberrypi.org/forums/viewtopic.php?t=268688
    with picamera.PiCamera() as camera:

    # initialize the camera and grab a reference to the raw camera capture
        camera.resolution = (width, height)
        camera.framerate = frameRate
        rawCapture = PiRGBArray(camera, size=(width, height))

        sleep(sleepSeconds)

        # capture frames from the camera
        x = 1

        start_ms = time.time()

        for piImage in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # Note: using format=rgb results in orange sky
            # TODO: Test saving photo to see what kind the model gets

            print("frame ", x)
            frame = piImage.array
 
            rawCapture.truncate()
            rawCapture.seek(0)

            filename = str(x)

            # TODO: Check directly with prevFrame (but this is not straightforward with arrays!)
            # Here frame is piImage.array
            if havePreviousFrame:
                now = datetime.now()
                datetimeStr = now.strftime("%Y-%m-%dT%H-%M-%S.") + now.strftime("%f")[0:1]
                cropFrame = analyze.handleFrame(frame, prevFrame, imagesFolder, datetimeStr, True, width, height, x)

                '''
                Todo:
                Get frame from handleFrame, instead of saving to disk
                Convert to format understood by TF
                classify
                save if needed

                '''

                bestKey, bestVal, all = classify.classify(cropFrame)

                # TODO: sum bird values

                if bestKey != "empty":
                    saveFrame(cropFrame, imagesFolder, datetimeStr, bestKey, bestVal)
                elif all['empty'] < 0.6:
                    saveFrame(cropFrame, imagesFolder, datetimeStr, bestKey, bestVal)

#                if "empty" == bestKey:
#                    if bestVal < 0.5:
#                        saveFrame(cropFrame, imagesFolder, datetimeStr, bestKey, bestVal)
#                elif "obstacle" == bestKey:
#                    if bestVal < 0.5:
#                        saveFrame(cropFrame, imagesFolder, datetimeStr, bestKey, bestVal)
#                else:
#                    saveFrame(cropFrame, imagesFolder, datetimeStr, bestKey, bestVal)


            # Finalize
            elapsed_ms = (time.time() - start_ms) * 1000
            msPerFrame = elapsed_ms / x
            print(int(msPerFrame), "ms per frame")

            prevFrame = frame
            havePreviousFrame = True
            x = x + 1

        # TODO: How to stop properly?
        camera.stop_preview()
        camera.close()

    camera.stop_preview()
    camera.close()


if __name__ == '__main__':
  main()