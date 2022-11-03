import os
import json
import argparse
from tqdm import tqdm


def labelme2coco(labelme_path, classes_file, save_file):
    with open(classes_file, "r", encoding="utf8") as tf:
        classes = tf.readlines()
    
    cat_list = []

    # 针对自定义数据集
    classes_list = []
    for cla_id, cla in enumerate(classes):
        cla_name = cla.rstrip("\n")
        classes_list.append(cla_name)
    cat_list.append({"id": cla_id+1,
                          "name": cla_name,
                          "supercategory": ""})

    imgs_list = []
    annos_list = []

    labelme_file_list = sorted(os.listdir(labelme_path))
    for img_id, labelmefile in enumerate(tqdm(labelme_file_list)):
        laabelmepath = os.path.join(labelme_path, labelmefile)
        with open(laabelmepath, "r", encoding="utf8") as jf:
            labelmedata = json.load(jf)

        img_name = os.path.basename(labelmedata["imagePath"])
        img_width = labelmedata["imageWidth"]
        img_height = labelmedata["imageHeight"]

        imgs_list.append({"id": img_id+1,
                          "width": img_width,
                          "height": img_height,
                          "file_name": img_name, })

        labelmeshapes = labelmedata["shapes"]
        for anno_id, shape in enumerate(labelmeshapes):
            cat_label = shape["label"]
            cat_id = classes_list.index(cat_label)

            x1, y1, x2, y2 = shape["points"][0][0], shape["points"][0][1], shape["points"][1][0], shape["points"][1][1]
            coco_x, coco_y = min(x1, x2), min(y1, y2)
            coco_w, coco_h = max(x1, x2)-min(x1, x2), max(y1, y2)-min(y1, y2)
            coco_area = coco_w*coco_h

            annos_list.append({"id": anno_id+1,
                               "image_id": img_id+1,
                               "category_id": cat_id,
                               "segmentation": [x1, y1, x2, y1, x2, y2, x1, y2],
                               "area": coco_area,
                               "bbox": [coco_x, coco_y, coco_w, coco_h],
                               "iscrowd": 0})

    coco_file = {"info": {},
                 "license": [],
                 "images": imgs_list,
                 "annotations": annos_list,
                 "categories": cat_list}

    if os.path.exists(save_file):
        os.remove(save_file)
    with open(save_file, "w", encoding="utf8") as fp:
        json.dump(coco_file, fp, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--labelme_path', type=str, default='labelme_data', help="")
    parser.add_argument('-c', '--classes_file', type=str, default='classes.txt', help="")
    parser.add_argument('-s', '--save_file', type=str, default='labelme2coco_result.json', help="")

    arg = parser.parse_args()

    labelme_path = arg.labelme_path
    classes_file = arg.classes_file
    save_file = arg.save_file

    labelme2coco(labelme_path, classes_file, save_file)
