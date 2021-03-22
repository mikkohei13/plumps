
from datetime import datetime

import cv2
import numpy as np

#import predict_helper

"""
Have to compare frames, to get rid of clouds, dark parts of the sky etc. But it's no use for getting rid of noise.

TODO:
See how well AI finds ribbons
If finds, 
- use AI to find birds, with low threshold
- handle only those, to 
-- crop to bird. How?


"""

def test(frame):
    print("test F")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print("gray")
    cv2.imwrite("./crops/test.jpg", frame)
    print("saved")


def handleFrame(frame, background_frame, directory, filename, saveCrops, saveImages, width, height):
    """
    Use OpenCV to detect areas in frame that differ from background_frame
    """

    directory = "./" + directory + "/"

    now = datetime.now()
    filetime = now.strftime("%Y-%m-%dT%H-%M-%S.") + now.strftime("%f")[0:1]


    frameColor = frame # Preserve color image


    # Thre are two options for detecting changed pixels:

    # A) Absolute difference in grayscale image
    # This finds also objects that are lighter than sky, but leaves redundant areas on the crops
    '''
    diffFrameGray = cv2.absdiff(
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
    )
    '''

    # B) Relative difference
    # This crops images to the birds only, but cannot find objects brighter than sky
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    background_frame = cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
    diffFrameGray = cv2.subtract(background_frame, frame)


    # Invert, so we can find the white items
    # TODO: Can this be included in the threshold function, to save processing time?
    diffFrameGray = cv2.bitwise_not(diffFrameGray)

    # Levels: brighest point is white, darkest is black.
    cv2.normalize(diffFrameGray, diffFrameGray, 0, 255, cv2.NORM_MINMAX)

    # Threshold
    theStart = 10
    theStep = 5
    minPixels = 30
    pixels = 0

    while pixels < minPixels:
        thresholdValue, newFrame = cv2.threshold(diffFrameGray, theStart, 255, cv2.THRESH_BINARY_INV)

        pixels = cv2.countNonZero(newFrame)
        print(str(pixels), end = "px ")

        theStart = theStart + theStep

    print("")

    # Find contours
    # Different versions of openCV return different number of values
    try:
        contours, hierarchy = cv2.findContours(newFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    except ValueError:
        contourFrame, contours, hierarchy = cv2.findContours(newFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    contourCount = 0
    padding = 20

    allX = []
    allY = []
    allW = []
    allH = []

    contourCount = 0
    for c in contours:

        #c = max(contours, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(c)
#        print("contour",x,y,w,h)

        # bottom left
        allX.append(x)
        allY.append(y)

        # top right
        allX.append(x+w)
        allY.append(y+h)

        contourCount = contourCount + 1
    
    print(contourCount, " contours")

    xMin = min(allX)
    yMin = min(allY)
    xMax = max(allX)
    yMax = max(allY)

#    print("Before padding: ", xMin, xMax, yMin, yMax)

    # Advanced padding
    widthPadding = 0
    heightPadding = 0
    targetSize = 224

    # First apply basic padding to get space around the detected pixels
    xMin = xMin-padding
    if xMin < 0:
        xMin = 0
    xMax = xMax+padding
    if xMax > width:
        xMax = width

    yMin = yMin-padding
    if yMin < 0:
        yMin = 0
    yMax = yMax+padding
    if yMax > height:
        yMax = height

    # Calculate size of the crop with basic padding
    cropWidth = xMax - xMin
    cropHeight = yMax - yMin

    # If smaller than target size, add more padding
    if cropWidth < targetSize:
        widthPadding = (targetSize - cropWidth) / 2

    if cropHeight < targetSize:
        heightPadding = (targetSize - cropHeight) / 2

    xMin = xMin - widthPadding
    if xMin < 0:
        xMin = 0
    xMax = xMax + widthPadding
    if xMax > width:
        xMax = width

    yMin = yMin - heightPadding
    if yMin < 0:
        yMin = 0
    yMax = yMax + heightPadding
    if yMax > height:
        yMax = height

    xMin = int(xMin)
    xMax = int(xMax)
    yMin = int(yMin)
    yMax = int(yMax)

#    print("After padding: ", xMin, xMax, yMin, yMax)

    # Basic padding
    '''
    xMin = xMin-padding
    if xMin < 0:
        xMin = 0
    xMax = xMax+padding
    if xMax > width:
        xMax = width

    yMin = yMin-padding
    if yMin < 0:
        yMin = 0
    yMax = yMax+padding
    if yMax > height:
        yMax = height
    '''

    # Image dimensions
    finalWidth = xMax - xMin
    finalHeight = yMax - yMin

    # Save only if small image
    # TODO: Lift this limitation when using AI to infer. Now this misses large flocks!
    if (finalWidth < 400 and finalHeight < 400):

        cropFrame = frameColor[yMin:yMax, xMin:xMax]
        cropFilePath = directory + filename + "_crop.jpg"
    #    print(cropFilePath)

        cv2.imwrite(cropFilePath, cropFrame)
        print("SAVED")
    else:
        print("skipped")

    return True

