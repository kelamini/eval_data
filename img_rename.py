import os
import shutil
import datetime
from PIL import Image
import tqdm
import argparse


def is_image(file_name):
    img_suffix = ["png", "jpg", "jpeg", "bmp"]
    if str(file_name).split(".")[-1] in img_suffix:
        return True
    
    return False


def image_rename(dir_path, cnt=1, work_name="face"):
    """
    重命名图像名称
    """
    date = datetime.date.today()
    strdate = str(date.year) + str(date.month) + str(date.day)
    for root, dirs, files in os.walk(dir_path):
        img_files = [file_name for file_name in files if is_image(file_name)]
        for file in img_files:
            file_path = os.path.join(root, file)
            imgs_suffix = str(file).split(".")[-1]
            rename_file = f"{work_name}_{strdate}_{cnt}.{imgs_suffix}"
            file_rename_path = os.path.join(root, rename_file)
            try:
                shutil.move(file_path, file_rename_path)
                cnt += 1
            except OSError:
                pass
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d', '--dir_path', default='images', type=str, help="")
    parser.add_argument('-c', '--cnt', default=1, type=int, help="")
    parser.add_argument('-w', '--work_name', default='FaceDetection', type=str, help="")


    arg = parser.parse_args()

    dirpath = arg.dir_path
    cnt = arg.cnt
    work_name = arg.work_file
    

    image_rename(dirpath, cnt, work_name)
