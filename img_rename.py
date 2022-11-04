import os
import shutil
import datetime
from PIL import Image
from tqdm import tqdm
import argparse


def is_image(file_name):
    img_suffix = ["png", "jpg", "jpeg", "bmp"]
    if str(file_name).split(".")[-1] in img_suffix:
        return True
    
    return False


def image_rename(dir_path, cnt=1, work_name="FaceDetection"):
    """
    重命名图像名称
    """
    save_path = os.path.join(os.path.dirname(dir_path), f"{work_name}_images")
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.mkdir(save_path)
    print(f"rename images save to: {save_path}")

    date = datetime.date.today()    # 获取当前日期
    strdate = str(date.year) + str(date.month) + str(date.day)  # 将日期转换为字符串拼接在一起
    # 遍历图像路径
    for root, dirs, files in os.walk(dir_path):
        print(f"for: {root}")
        img_files_list = [file_name for file_name in files if is_image(file_name)]   # 图像的名称列表
        # 遍历图像
        for img_file in tqdm(img_files_list):
            file_path = os.path.join(root, img_file)    # 图像的路径
            imgs_suffix = str(img_file).split(".")[-1]  # 图像文件的后缀名
            rename_file = f"{work_name}_{strdate}_{cnt}.{imgs_suffix}"  # 重命名图像的名称
            file_rename_path = os.path.join(save_path, rename_file)  # 重命名图像的路径
            try:
                shutil.copy(file_path, file_rename_path)
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
    work_name = arg.work_name
    

    image_rename(dirpath, cnt, work_name)
