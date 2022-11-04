import os
import shutil
import json
from pycocotools.coco import COCO
import argparse
from tqdm import tqdm


def add_img(old_file, new_file):
    old_coco_data = COCO(old_file)

    with open(old_file, "r", encoding="utf8") as ofp:
        old_data = json.load(ofp)

    with open(new_file, "r", encoding="utf8") as nfp:
        new_data = json.load(nfp)
    
    # 添加新的 图像
    old_images = old_data["images"]
    new_images = new_data["images"]

    img_ids = old_coco_data.getImgIds()
    image_max_index = max(img_ids)


    print("add images begin")
    for new_image in tqdm(new_images):
        new_image["id"] += image_max_index

        old_images.append(new_image)

    # 添加新的 类别
    old_cats = old_data["categories"]
    new_cats = new_data["categories"]

    cat_ids = old_coco_data.getCatIds()
    cat_max_index = max(cat_ids)

    print("add category begin")
    for new_cat in tqdm(new_cats):
        new_cat["id"] += cat_max_index
        
        old_cats.append(new_cat)

    # 添加新的 annotation
    old_annos = old_data["annotations"]
    new_annos = new_data["annotations"]

    anno_ids = old_coco_data.getAnnIds()
    anno_max_index = max(anno_ids)

    print("add annotations begin")
    for new_anno in tqdm(new_annos):
        anno_max_index += 1
        new_anno["id"] = anno_max_index
        new_anno["image_id"] += image_max_index
        new_anno["category_id"] += cat_max_index

        old_annos.append(new_anno)        

    # 写入 json 文件
    with open("merge_add_img_cat_anno.json", "w", encoding="utf8") as wp:
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
