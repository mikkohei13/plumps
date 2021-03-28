
from datetime import datetime

import cv2
#import numpy as np

def calculateCropSize(xMin, xMax, yMin, yMax):

    cropWidth = xMax - xMin
    cropHeight = yMax - yMin

    return cropWidth, cropHeight


def calculateCropSize_SKIP_LARGE(xMin, xMax, yMin, yMax):

    # Set max size for crop to be saved. Anything larger than this is skipped, in order not to get lot of full sky images without objects. Allow large images in order to get training material of empty sky.
    maxWidth = 400
    maxHeight = 400

    cropWidth = xMax - xMin
    cropHeight = yMax - yMin

    if (cropWidth > maxWidth or cropHeight > maxHeight):
        continueProcess = False
        print("Skipping  image size ", cropWidth, cropHeight)
    else:
        continueProcess = True

    return continueProcess, cropWidth, cropHeight


def handleFrame(frame, background_frame, directory, filename, returnCrop, width, height, frameNumber):

    # Save every nth frame
    if (frameNumber % 2000 == 0):
        fullFrameFilename = "./fulls/" + filename + ".jpg"
        cv2.imwrite(fullFrameFilename, frame)

    """
    Use OpenCV to detect areas in frame that differ from background_frame
    """

    directory = "./" + directory + "/"

    now = datetime.now()
    filetime = now.strftime("%Y-%m-%dT%H-%M-%S.") + now.strftime("%f")[0:1]

    frameColor = frame # Preserve color image


    # There are two options for detecting changed pixels:

    # A) Absolute difference in grayscale image
    # This finds also objects that are lighter than sky, but leaves redundant areas on the crops, where bird disappeared compared to previous image.
    '''
    diffFrameGray = cv2.absdiff(
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
    )
    '''

    # B) Relative difference
    # This crops images to the birds only, but cannot find objects brighter than the sky.
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    background_frame = cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
    diffFrameGray = cv2.subtract(background_frame, frame)


    # Invert, so we can find the white items
    # TODO: Can this be included in the threshold function, to save processing time?
    diffFrameGray = cv2.bitwise_not(diffFrameGray)

    # Levels: brighest point is white, darkest is black.
    cv2.normalize(diffFrameGray, diffFrameGray, 0, 255, cv2.NORM_MINMAX)

    # Threshold
    thresholdStart = 10
    thresholdStep = 5
    minPixels = 30  # Minimum number of black pixels we want

    pixels = 0

    while pixels < minPixels:
        thresholdValue, newFrame = cv2.threshold(diffFrameGray, thresholdStart, 255, cv2.THRESH_BINARY_INV)

        pixels = cv2.countNonZero(newFrame)
        print(str(pixels), end = " ")

        thresholdStart = thresholdStart + thresholdStep

    print(" px")

    # Find contours
    # Different versions of openCV return different number of values, so have to check 2 and 3 return values
    # TODO: Would it be faster the other way around on Pi?
    try:
        contours, hierarchy = cv2.findContours(newFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    except ValueError:
        contourFrame, contours, hierarchy = cv2.findContours(newFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    padding = 20    # How much padding we want around the dark part of the object
    contourCount = 0

    allX = []
    allY = []
    allW = []
    allH = []

    contourCount = 0
    for c in contours:

        x,y,w,h = cv2.boundingRect(c)
#        print("contour",x,y,w,h) # debug

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


    cropWidth, cropHeight = calculateCropSize(xMin, xMax, yMin, yMax)
#    if not continueProcess:
#        return True


    # Advanced padding
    widthPadding = 0
    heightPadding = 0
    targetSize = 224    # Tensorflow Lite default(?)

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


#    continueProcess, cropWidth, cropHeight = calculateCropSize(xMin, xMax, yMin, yMax)
#    if not continueProcess:
#        return True


    # If smaller than target size, add more padding
    # TODO Maybe: if reaches image limit, shift crop so that can get 224 x 224 pixels.

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


#    continueProcess, cropWidth, cropHeight = calculateCropSize(xMin, xMax, yMin, yMax)
#    if not continueProcess:
#        return True

    # Here cropFrame is Numpy array
    cropFrame = frameColor[yMin:yMax, xMin:xMax]

    if returnCrop:
        print("returning frame")
        return cropFrame

    else:
        cropFilePath = directory + filename + "_crop.jpg"
        cv2.imwrite(cropFilePath, cropFrame)
        print("wrote frame")
        return True


