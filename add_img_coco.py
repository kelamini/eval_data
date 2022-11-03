import os
import shutil
import json
import argparse
from pycocotools.coco import COCO
from tqdm import tqdm


def add_img(old_file, new_file):
    old_coco_data = COCO(old_file)

    with open(old_file, "r", encoding="utf8") as of:
        old_data = json.load(of)

    with open(new_file, "r", encoding="utf8") as nf:
        new_data = json.load(nf)
    
    # 添加新的 图像
    old_images = old_data["images"]
    new_images = new_data["images"]

    img_ids = old_coco_data.getImgIds()
    image_max_index = max(img_ids)

    print("add images begin")
    for new_image in tqdm(new_images):
        image_max_index += 1
        new_image["id"] = image_max_index
        old_images.append(new_image)

    # 写入 json 文件
    with open("merge_add_img.json", "w", encoding="utf8") as wp:
        json.dump(old_data, wp)

    print("over!!!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-old', '--old_file', default='old_coco_data.json', type=str, help="")
    parser.add_argument('-new', '--new_file', default='new_coco_data.json', type=str, help="")

    arg = parser.parse_args()

    old_file = arg.old_file
    new_file = arg.new_file

    add_img(old_file, new_file)
