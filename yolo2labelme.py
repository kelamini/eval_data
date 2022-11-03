import os
import shutil
import json
from PIL import Image
import base64
import argparse
from tqdm import tqdm


def img_encode_b64(img_path):
    with open(img_path, "rb") as bf:
        img_data = bf.read()
    base64_data = base64.b64encode(img_data)
    base64_str = str(base64_data, encoding="utf-8")

    return base64_str


def yolo2labelme(txt_path, classes_file, img_path, save_path, shapeType="rectangle"):
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.mkdir(save_path)

    #
    with open(classes_file, "r", encoding="utf-8") as cfp:
        classes = cfp.readlines()

    # 针对 coco 数据集
    classes_list = [str(i) for i in range(91)]
    for cla in classes:
        cla_id, cla_label = cla.rstrip("\n").split("-")
        cla_id = int(cla_id)
        classes_list[cla_id] = cla_label

    # # 针对自定义数据集
    # classes_list = []
    # for cla in classes:
    #     classes_list.append(cla.rstrip("\n"))


    # 迭代 yolo 的 txt 文件
    img_id = 1
    for img_file in tqdm(sorted(os.listdir(img_path))):
        txt_file = img_file.replace("jpg", "txt").replace("png", "txt")
        
        imgpath = os.path.join(img_path, img_file)
        txtpath = os.path.join(txt_path, txt_file)
        # print(f"img_file: {img_file} \t txt_file: {txt_file}")

        imgs = Image.open(imgpath)
        img_w, img_h = imgs.size
        img_data = img_encode_b64(imgpath)
        try:
            with open(txtpath, "r", encoding="utf8") as fp:
                # 获取文件内容
                txtcontent = fp.readlines()
        except:
            jsonset = {"version": "",
                   "flags": {},
                   "shapes": [],
                   "imagePath": img_file,
                   "imageData": img_data,
                   "imageHeight": img_h,
                   "imageWidth": img_w}
            # print(f"{imgpath} not found txt file to compare")
            continue

        shapes = []
        for line in txtcontent:
            line = line.rstrip("\n").split(" ")
            line = [float(i) for i in line]
            
            cat_id = int(line[0])
            cat_label = classes_list[cat_id]

            if shapeType == "rectangle":
                yolo_xc, yolo_yc = line[1], line[2]
                yolo_w, yolo_h = line[3], line[4]
                x_min = (yolo_xc-yolo_w/2)*img_w
                y_min = (yolo_yc-yolo_h/2)*img_h
                x_max = (yolo_xc+yolo_w/2)*img_w
                y_max = (yolo_yc+yolo_h/2)*img_h
                
                points = [[x_min, y_min], [x_max, y_max]]

            shapes.append({"label": cat_label,
                           "points": points,
                           "group_id": None,
                           "cat_id": cat_id,
                           "shape_type": shapeType,
                           "flags": {}})
        
        jsonset = {"version": "",
                   "flags": {},
                   "img_id": img_id,
                   "shapes": shapes,
                   "imagePath": img_file,
                   "imageData": img_data,
                   "imageHeight": img_h,
                   "imageWidth": img_w}

        savepath = os.path.join(save_path,
                                txt_file.split(".")[0]+".json")

        if os.path.exists(savepath):
            os.remove(savepath)

        with open(savepath, "a", encoding="utf8") as wp:
            json.dump(jsonset, wp, indent=2)

        img_id += 1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--txt_path", type=str, default="yolo_data", help="")
    parser.add_argument("-c", "--classes_file", type=str, default="classes.txt", help="")
    parser.add_argument("-i", "--img_path", type=str, default="images", help="")
    parser.add_argument("-s", "--save_path", type=str, default="yolo2labelme_result", help="")
    parser.add_argument("-st", "--shapeType", type=str, default="rectangle", help="")

    args = parser.parse_args()

    # 存放 txt 文件夹的路径
    txt_path = args.txt_path
    classes_file = args.classes_file
    # 存放 图像文件夹的路径
    img_path = args.img_path
    # 存放 保存的 json 文件的文件夹的路径
    save_path = args.save_path
    # 
    shapeType = args.shapeType

    # 执行 txt 文件 转 json 文件
    yolo2labelme(txt_path, classes_file, img_path, save_path, shapeType)
