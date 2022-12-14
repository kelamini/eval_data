import os
import sys
import shutil
from PIL import Image
import tqdm
import cv2
import numpy as np


def hash_img(imgpath, imgsize = 100):
    """
    计算图片的特征序列
    """
    a = []  # 存储图片的像素
    hash_value = ''  # 特征序列
    width, height = imgsize, imgsize  # 图片缩放大小
    
    img = Image.open(imgpath)
    img = img.resize((width, height))  # 图片缩放为width×height

    for y in range(img.height):
        b = []
        for x in range(img.width):
            pos = x, y
            color_array = img.getpixel(pos)  # 获得像素
            color = sum(color_array)/3  # 灰度化
            b.append(int(color))
        a.append(b)

    for y in range(img.height):
        avg = sum(a[y])/len(a[y])  # 计算每一行的像素平均值
        for x in range(img.width):
            if a[y][x] >= avg:  # 生成特征序列,如果此点像素大于平均值则为1,反之为0
                hash_value += '1'
            else:
                hash_value += '0'

    return hash_value

def similar(path1, path2):
    """
    求相似度
    """
    hash1 = hash_img(path1)  # 计算 img1 的特征序列
    hash2 = hash_img(path2)  # 计算 img2 的特征序列

    if len(hash1) == len(hash2):
        differnce = 0
        hashlenth = len(hash1)
        for i in range(hashlenth):
            differnce += abs(int(hash1[i])-int(hash2[i]))
        similar = 1-(differnce/hashlenth)
    else:
        print(f"coculate false")
        similar = None

    return similar


if __name__ == "__main__":
    img1 = "./data/imgs/similar1.jpg"
    img2 = "./data/imgs/similar2.jpg"
    print('%.1f%%' % (similar(img1, img2) * 100))
