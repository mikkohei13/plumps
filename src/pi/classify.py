
 
# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to classify objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#import argparse
#import io
#import time
import numpy as np
#import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

#from datetime import datetime
#from time import sleep


def saveImageSimple(cropImage):
    filePath = "./test/224.jpg"
    cropImage.save(filePath, quality=100, subsampling=0)

    print("saved", filePath) # log DEBUG
    return True


def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']

    # "output" is list of probablilities, in the same order as labels are in dict.txt
    output = scale * (output - zero_point)

  # "ordered" is list of numbers that show the order of each probability in "output"
  ordered = np.argpartition(-output, top_k)

#  print("ordered ", ordered)
#  print("output", output)

#  best = ordered[0]
#  all = [(labels[i], output[i]) for i in ordered[:top_k]]
#  print(best, all)

  return output
#  return ordered # labels
#  return output


def formatOutput(output, labels):
  all = {}
  labelNumber = 0
  for i in output:
    all[labels[labelNumber]] = i
    labelNumber = labelNumber + 1

  bestKey = max(all, key=lambda key: all[key])
  bestVal = all[bestKey]
#  print("best", best)
  # TODO: return best key and value as second return value

  return bestKey, bestVal, all


# Main function
def classify(cropFrame):
    print("Here")

#    width = 224
#    height = 224

    # Hardcoded args
#    model = './models/tflite-plumps1_20210328/model.tflite'
#    labels = './models/tflite-plumps1_20210328/dict.txt'

    model = './models/tflite-plumps2_20210330/model.tflite'
    labels = './models/tflite-plumps2_20210330/dict.txt'


    # TODO: Do this only once, pass to the function?
    labels = load_labels(labels)

    interpreter = Interpreter(model)
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']

    cropImage = Image.fromarray(cropFrame)
    cropImage = cropImage.resize((width, height), Image.ANTIALIAS)

#    success = saveImageSimple(cropImage) # test

    results = classify_image(interpreter, cropImage, 1)
#    print("Results array ", results)

    bestKey, bestVal, all = formatOutput(results, labels)
    print("res: ", bestKey, bestVal, all)

#    label_id, prob = results[0]

#    print(labels[label_id], prob)

#    return labels[label_id], prob
    return bestKey, bestVal, all
