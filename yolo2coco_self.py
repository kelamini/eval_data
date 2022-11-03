import os
from PIL import Image
import json
from tqdm import tqdm
import argparse


def yolo2coco(txt_path, img_path, classes_file, save_file):
    # 从文件中 获取 类别与类别 ID 的对应关系
    with open(classes_file, "r", encoding="utf-8") as cfp:
        classes = cfp.readlines()

    cat_list = []

    # # 针对 coco 数据集
    # classes_list = [str(i) for i in range(91)]
    # for cla in classes:
    #     cla_id, cla_label = cla.rstrip("\n").split("-")
    #     cla_id = int(cla_id)
    #     classes_list[cla_id] = cla_label
    #     cat_list.append({"id": cla_id,
    #                       "name": cla_label,
    #                       "supercategory": ""})

    # 针对自定义数据集
    for cla_id, cla in enumerate(classes):
        cla_name = cla.rstrip("\n")
    cat_list.append({"id": cla_id,
                          "name": cla_name,
                          "supercategory": ""})



    # 迭代 yolo 的 txt 文件
    success = 0
    img_id = 1
    anno_id = 1
    img_list = []
    anno_list = []
    for img_file in tqdm(sorted(os.listdir(img_path))):
        txt_file = img_file.replace("jpg", "txt").replace("png", "txt")
        
        imgpath = os.path.join(img_path, img_file)
        txtpath = os.path.join(txt_path, txt_file)
        # print(f"img_file: {img_file} \t txt_file: {txt_file}")

        imgs = Image.open(imgpath)
        img_w, img_h = imgs.size

        img_list.append({"id": img_id,
                         "width": img_w,
                         "height": img_h,
                         "file_name": img_file})

        try:
            success += 1
            with open(txtpath, "r", encoding="utf8") as fp:
                # 获取文件内容
                txtcontent = fp.readlines()
        except:
            img_id += 1
            continue

        for line in txtcontent:
            line = line.rstrip("\n").split(" ")
            line = [float(i) for i in line]
            
            cat_id = int(line[0])

            yolo_xc, yolo_yc = line[1], line[2]
            yolo_w, yolo_h = line[3], line[4]
            coco_x = (yolo_xc-yolo_w/2)*img_w
            coco_y = (yolo_yc-yolo_h/2)*img_h
            coco_w = yolo_w*img_w
            coco_h = yolo_h*img_h
                
            bbox = [coco_x, coco_y, coco_w, coco_h]
            area = coco_w*coco_h
            segmentation = [coco_x, coco_y, coco_x+coco_w, coco_y, coco_x+coco_w, coco_y+coco_h, coco_x, coco_y+coco_h]

            anno_list.append({"id": anno_id,
                           "image_id": img_id,
                           "category_id": cat_id,
                           "segmentation": segmentation,
                           "area": area,
                           "bbox": bbox,
                           "iscrowd": 0})
            
            anno_id += 1
        
        img_id += 1

    cocoset = {"info": {},
                "flags": {},
                "images": img_list,
                "annotations": anno_list,
                "categories": cat_list,
                "licenses": []}

    if os.path.exists(save_file):
        os.remove(save_file)

    with open(save_file, "w", encoding="utf8") as wp:
        json.dump(cocoset, wp, indent=2)
    print("success:", anno_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-t', '--txt_path', default='yolo_data', type=str, help="")
    parser.add_argument('-i', '--img_path', default='images', type=str, help="")
    parser.add_argument('-c', '--classes_file', default='classes.txt', type=str, help="")
    parser.add_argument('-s', '--save_file', type=str, default='yolo2coco_result.json', help="")

    arg = parser.parse_args()

    txt_path = arg.txt_path
    img_path = arg.img_path
    classes_file = arg.classes_file
    save_file = arg.save_file

    yolo2coco(txt_path, img_path, classes_file, save_file)
