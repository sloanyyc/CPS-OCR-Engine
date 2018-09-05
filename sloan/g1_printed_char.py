#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import copy
import random
import numpy as np

import os
import shutil

class DataAugmentation(object):
  def __init__(self,noise=True,dilate=True,erode=True):
    self.noise = noise
    self.dilate = dilate
    self.erode = erode

  @classmethod 
  def add_noise(cls,img):
    for i in range(random.randint(30, 100)): #添加点噪声
      temp_x = random.randint(2,img.shape[0]-2)
      temp_y = random.randint(2,img.shape[1]-2)
      img[temp_x-1][temp_y] = 255
      img[temp_x][temp_y-1] = 255
      img[temp_x][temp_y] = 255
      img[temp_x+1][temp_y] = 255
      img[temp_x][temp_y+1] = 255
    return img

  @classmethod
  def add_erode(cls,img): 
    # 先膨胀2后侵蚀4
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2, 2))    
    img = cv2.dilate(img,kernel) 
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3, 3))    
    img = cv2.erode(img,kernel) 
    return img

  @classmethod
  def add_dilate(cls,img):
    # 先侵蚀2后膨胀4
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2, 2))    
    img = cv2.erode(img,kernel) 
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3, 3))    
    img = cv2.dilate(img,kernel) 
    return img

  def do(self,im):
    if self.noise and random.random()<0.5:
      im = self.add_noise(im)
    if random.random()<0.5:
      if self.dilate:
        im = self.add_dilate(im)
    else:
      if self.erode:
        im = self.add_erode(im)
    return im

# 检查字体文件是否可用
class FontCheck(object):

  def __init__(self, lang_chars, width=32, height=32):
    self.lang_chars = lang_chars
    self.width = width
    self.height = height

  def do(self, font_path):
    width = self.width
    height = self.height
    try:
      for i, char in enumerate(self.lang_chars):
        img = Image.new("RGB", (width, height), "black") # 黑色背景
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, int(height * 0.9),)
        # 白色字体
        draw.text((0, 0), char, (255, 255, 255), font=font)
        data = list(img.getdata())
        sum_val = 0
        for i_data in data:
          sum_val += sum(i_data)
        if sum_val < 2:
          return False
    except:
      print("fail to load:%s" % font_path)
      traceback.print_exc(file=sys.stdout)
      return False
    return True

class FontDrawImage(object):
  def __init__(self,font_path, width=128, height=128):
    self.width = width
    self.height = height
    self.font = ImageFont.truetype(font_path, int(self.height * 0.8))

  def do(self, ch):
    img = Image.new("RGB", (self.width, self.height), "black")
    draw = ImageDraw.Draw(img)
    # 白色字体
    draw.text((random.randint(3, int(self.height*0.2)*2), random.randint(3, int(self.height*0.2))), 
      ch, (255, 255, 255), font=self.font)
    return img

dataAugmentation = DataAugmentation()#dilate=False,erode=False)

fontDrawImage = []

font_dir = '../ocr/chinese_fonts/'
verified_font_paths = []
## search for file fonts
font_check = FontCheck({'a':'a'}) 
for font_name in os.listdir(font_dir):
  path_font_file = os.path.join(font_dir, font_name)
  if font_check.do(path_font_file):
    verified_font_paths.append(path_font_file)
    fontDrawImage.append(FontDrawImage(path_font_file))

shutil.rmtree('dataset')
for c in range(33, 127):
  os.makedirs('dataset/train/%05d'%(c-33))
  os.makedirs('dataset/test/%05d'%(c-33))
  cnt = 0
  for x in range(0,10):
    for y in range(0, 20):
      img = fontDrawImage[y].do(str(chr(c)))
      img = img.rotate(random.randint(-15, 15))
      data = list(img.getdata())
      np_img = np.asarray(data, dtype='uint8')
      np_img = np_img[:, 0]
      np_img = np_img.reshape((img.width, img.height))
      out_im = dataAugmentation.do(np_img)
      if (cnt < 20):
        cv2.imwrite('dataset/test/%05d/%d.png'%(c-33, cnt), out_im)
      else:
        cv2.imwrite('dataset/train/%05d/%d.png'%(c-33, cnt), out_im)
      cnt += 1
      # img = Image.fromarray(out_im.astype('uint8')).convert('RGB')
      # img = img.resize((img.width/4, img.height/4))
      # img.show()












