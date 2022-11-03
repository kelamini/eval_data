import os
from PIL import Image
import shutil
import argparse


def is_image(file_name):
    img_suffix = ["png", "jpg", "jpeg", "bmp"]
    if str(file_name).split(".")[-1] in img_suffix:
        return True
    
    return False

def filter_bad(dir_path, save_bad_path):
    """
    去除已损坏图片
    """
    filter_dir = os.path.join(os.path.dirname(dir_path), save_bad_path)
    if not os.path.exists(filter_dir):
        os.mkdir(filter_dir)
    
    filter_number = 0
    for root, dirs, files in os.walk(dir_path):
        img_files = [file_name for file_name in files if is_image(file_name)]
        for file in img_files:
            file_path = os.path.join(root, file)
            try:
                Image.open(file_path).load()
            except OSError:
                shutil.move(file_path, filter_dir)
                filter_number += 1
    
    return filter_number


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d', '--dir_path', default='images', type=str, help="")
    parser.add_argument('-b', '--bad_path', default='badimages', type=str, help="")


    arg = parser.parse_args()

    dirpath = arg.dir_path
    savebadpath = arg.bad_path


    filter_bad(dirpath, savebadpath)
