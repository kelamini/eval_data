import os
import json
import argparse
from tqdm import tqdm


def labelme2coco(labelme_path, classes_file, save_file):
    # 获取 classes.txt 文件内容
    with open(classes_file, "r", encoding="utf8") as tf:
        classes = tf.readlines()
    
    cat_list = []

    # 保证 cat_id 与 cat_name 对应
    classes_list = [str(i) for i in range(91)]
    for cla in classes:
        cla_id, cla_label = cla.rstrip("\n").split("-")
        cla_id = int(cla_id)
        classes_list[cla_id] = cla_label
        cat_list.append({"id": cla_id,
                          "name": cla_label,
                          "supercategory": ""})

    imgs_list = []
    annos_list = []

    labelme_file_list = sorted(os.listdir(labelme_path))
    for img_id, labelme_file in enumerate(tqdm(labelme_file_list)):
        laabelme_path = os.path.join(labelme_path, labelme_file) # labelme 的 json 文件的路径
        with open(laabelme_path, "r", encoding="utf8") as jf:
            labelmedata = json.load(jf)

        # img_id = labelmedata["img_id"]
        img_name = os.path.basename(labelmedata["imagePath"])
        img_width = labelmedata["imageWidth"]
        img_height = labelmedata["imageHeight"]

        imgs_list.append({"id": img_id,
                          "width": img_width,
                          "height": img_height,
                          "file_name": img_name, })

        labelmeshapes = labelmedata["shapes"]
        for anno_id, shape in enumerate(labelmeshapes):
            # anno_id = shape["anno_id"]  # annotation 的编号
            is_modify = shape["is_modify"]  # 是否 通过 labelme 修改 确定为 gt 
            
            cat_label = shape["label"]  # category 的名称
            cat_id = classes_list.index(cat_label)  # category 的编号

            x1, y1, x2, y2 = shape["points"][0][0], shape["points"][0][1], shape["points"][1][0], shape["points"][1][1]
            coco_x, coco_y = min(x1, x2), min(y1, y2)   # 目标框左上角坐标
            coco_w, coco_h = max(x1, x2)-min(x1, x2), max(y1, y2)-min(y1, y2)   # 目标框宽、高
            coco_area = coco_w*coco_h   # 目标框面积

            annos_list.append({"id": anno_id,
                               "image_id": img_id,
                               "category_id": cat_id,
                               "is_modify": is_modify,
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
