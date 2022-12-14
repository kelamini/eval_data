import os
import os.path as osp
from PIL import Image
import numpy as np
import base64
from tqdm import tqdm
from pycocotools.coco import COCO

from utils.io import make_save_path, read_json_file, read_txt_file, write_json_file, write_txt_file


def img_encode_b64(img_path):
    with open(img_path, "rb") as bf:
        img_data = bf.read()
    base64_data = base64.b64encode(img_data)
    base64_str = str(base64_data, encoding="utf-8")

    return base64_str


def obtain_img_wh(imgpath):
    imgs = Image.open(imgpath)
    img_w, img_h = imgs.size

    return img_w, img_h


def xcycwh2xywh(points, imgshape):
    """
    function: x_center, y_center, w, h -> x, y, w, h
    """
    yolo_xc, yolo_yc, yolo_w, yolo_h = points

    coco_x = (yolo_xc - yolo_w / 2) * imgshape[0]
    coco_y = (yolo_yc - yolo_h / 2) * imgshape[1]
    coco_w = yolo_w * imgshape[0]
    coco_h = yolo_h * imgshape[1]

    return coco_x, coco_y, coco_w, coco_h


def xywh2xcycwh(points, imgshape):
    coco_xc, coco_yc, coco_w, coco_h = points
    yolo_xc = (coco_xc + coco_w / 2) / imgshape[0]
    yolo_yc = (coco_yc + coco_h / 2) / imgshape[1]
    yolo_w = coco_w / imgshape[0]
    yolo_h = coco_h / imgshape[1]

    return yolo_xc, yolo_yc, yolo_w, yolo_h


def xyxy2xywh(points):
    x1, y1, x2, y2 = points
    coco_x, coco_y = min(x1, x2), min(y1, y2)
    coco_w, coco_h = max(x1, x2) - min(x1, x2), max(y1, y2) - min(y1, y2)

    return coco_x, coco_y, coco_w, coco_h


def xcycwh2xyxy(points, imgshape):
    yolo_xc, yolo_yc, yolo_w, yolo_h = points

    x_min = (yolo_xc - yolo_w / 2) * imgshape[0]
    y_min = (yolo_yc-yolo_h/2) * imgshape[1]
    x_max = (yolo_xc+yolo_w/2)*imgshape[0]
    y_max = (yolo_yc+yolo_h/2)*imgshape[1]

    return x_min, y_min, x_max, y_max


def xywh2xyxy(points):
    coco_x, coco_y, coco_w, coco_h = points
    x1, y1 = coco_x, coco_y
    x2, y2 = coco_x + coco_w, coco_y + coco_h

    return x1, y1, x2, y2


def xyxy2xcycwh(points, imgshape):
    x1, y1, x2, y2 = points
    yolo_xc = 0.5 * (x1 + x2) / imgshape[0]
    yolo_yc = 0.5 * (y1 + y2) / imgshape[1]
    yolo_w = (x2 - x1) / imgshape[0]
    yolo_h = (y2 - y1) / imgshape[1]

    return yolo_xc, yolo_yc, yolo_w, yolo_h


def yolo2coco(yolo_file_dir, img_file_dir, classes_file_path, save_dir, save_coco_file):
    """
    @ functions: 
    @ yolo_file_dir: yolo 格式的文件夹路径
    @ img_file_dir: 原图像的文件夹路径
    @ classes_file_path: 类别名称与类别 id 对应的 json 文件路径
    @ save_dir: 保存最终结果的文件夹路径
    @ save_coco_file: 保存文件的名称
    """
    # 文件保存的路径
    savedir = make_save_path(save_dir)
    os.makedirs(savedir)
    print("save to: ", savedir)

    # 从文件中 获取 类别名称与类别 ID 的对应关系
    classes_dict = read_json_file(classes_file_path)
    
    coco_category_list = []
    for key, value in classes_dict.items():
        cla_id = int(key)
        coco_category_list.append({
            "id": cla_id,
            "name": value,
            "supercategory": ""
            })

    # 迭代 yolo 的 txt 文件
    img_list = []
    anno_list = []
    anno_id = 0
    img_file_list = sorted(os.listdir(img_file_dir))
    for img_id, img_name in enumerate(tqdm(img_file_list)):
        imgpath = os.path.join(img_file_dir, img_name)  # image 文件路径
        txtpath = os.path.join(yolo_file_dir, img_name.replace("jpg", "txt"))     # txt 文件路径

        # 获取 image 的 宽、高
        imgshape = obtain_img_wh(imgpath)

        img_list.append({"id": img_id,
                         "width": imgshape[0],
                         "height": imgshape[1],
                         "file_name": img_name})

        try:
            txtcontent = read_txt_file(txtpath)
        except:
            continue

        for line in txtcontent:
            line = line.rstrip("\n").split(" ")
            bboxes = [float(i) for i in line]   
            
            coco_x, coco_y, coco_w, coco_h = xcycwh2xywh(bboxes[1:5], imgshape)
        
            bbox = [coco_x, coco_y, coco_w, coco_h]
            area = coco_w * coco_h
            segmentation = [coco_x, coco_y, coco_x+coco_w, coco_y, coco_x+coco_w, coco_y+coco_h, coco_x, coco_y+coco_h]

            cat_id = int(bboxes[0])

            group_id = None
            if len(bboxes) >= 6:
                group_id = bboxes[5]
            
            is_verify = None
            if len(bboxes) >= 7:
                is_verify = bboxes[6]

            anno_list.append({
                "id": anno_id,
                "image_id": img_id,
                "category_id": cat_id,
                "is_verify": is_verify,
                "group_id": group_id,
                "segmentation": segmentation,
                "area": area,
                "bbox": bbox,
                "iscrowd": 0})
            anno_id += 1
    
    cocoset = {
        "info": {},
        "flags": {},
        "images": img_list,
        "annotations": anno_list,
        "categories": coco_category_list,
        "licenses": []}

    save_path = osp.join(savedir, save_coco_file)
    write_json_file(save_path, cocoset)


def coco2yolo(coco_file_path, save_dir):
    # 文件保存的路径
    savedir = make_save_path(save_dir)
    os.makedirs(savedir)
    print("save to: ", savedir)
    
    json_coco = COCO(coco_file_path)
    img_data = json_coco.loadImgs(json_coco.getImgIds())

    for img in tqdm(img_data):
        img_id = img["id"]
        imgshape = [img["width"], img["height"]]
        img_name = osp.basename(img["file_name"])

        anno_ids = json_coco.getAnnIds(img_id)

        for anno_id in anno_ids:
            annos = json_coco.loadAnns(anno_id)
            for anno in annos:
            
                cat_id = anno["category_id"]
        
                yolo_xc, yolo_yc, yolo_w, yolo_h = xywh2xcycwh(anno["bbox"], imgshape)
 
                group_id = -1
                if hasattr(anno, "group_id"):
                    group_id = anno["group_id"]
                
                is_verify = -1
                if hasattr(anno, "is_verify"):
                    is_verify = anno["is_verify"]

                txt_data = f"{cat_id} {yolo_xc} {yolo_yc} {yolo_w} {yolo_h} {group_id} {is_verify}\n"

                save_path = os.path.join(save_path, img_name.replace("jpg", "txt"))
                write_txt_file(save_path, txt_data)


def labelme2coco(labelme_file_dir, img_file_dir, classes_file_path, save_dir, save_coco_file):
    # 文件保存的路径
    savedir = make_save_path(save_dir)
    os.makedirs(savedir)
    print("save to: ", savedir)

    # 从文件中 获取 类别名称与类别 ID 的对应关系
    classes_dict = read_json_file(classes_file_path)
    
    cat_list = []
    cat_name_id = {}    # cat_name: cat_id
    # 保证 cat_id 与 cat_name 对应
    for key, value in classes_dict.items():
        cla_id = int(key)
        cat_name_id[value] = cla_id
        cat_list.append({"id": cla_id,
                          "name": value,
                          "supercategory": ""})

    imgs_list = []
    annos_list = []
    anno_id = 0
    img_file_list = sorted(os.listdir(img_file_dir))
    for img_id, img_name in enumerate(tqdm(img_file_list)):
        image_path = osp.join(img_file_dir, img_name)
        
        # 获取 image 的 宽、高
        imgshape = obtain_img_wh(image_path)

        imgs_list.append({"id": img_id,
                          "width": imgshape[0],
                          "height": imgshape[1],
                          "file_name": img_name
                         })
        try:
            labelme_file_path = os.path.join(labelme_file_dir, img_name.replace("jpg", "json"))  # labelme 的 json 文件的路径
            labelme_data = read_json_file(labelme_file_path)
        except:
            continue

        shapes = labelme_data["shapes"]
        for shape in shapes:
            # anno_id = shape["anno_id"]  # annotation 的编号
            if hasattr(shape, "is_verify"):
                is_verify = shape["is_verify"]  # 是否 通过 labelme 修改 确定为 gt 
            
            if hasattr(shape, "group_id"):
                group_id = shape["group_id"]
            
            cat_label = shape["label"]  # category 的名称
            # cat_label = "person"
            cat_id = cat_name_id[cat_label]  # category 的编号

            x1, y1, x2, y2 = shape["points"][0][0], shape["points"][0][1], shape["points"][1][0], shape["points"][1][1]
            points = np.array(shape["points"]).flatten()
            point = [float(i) for i in points]
            coco_x, coco_y, coco_w, coco_h = xyxy2xywh(point)

            coco_area = coco_w * coco_h   # 目标框面积

            annos_list.append({"id": anno_id,
                            "image_id": img_id,
                            "category_id": cat_id,
                            "is_verify": is_verify,
                            "group_id": group_id,
                            "segmentation": [x1, y1, x2, y1, x2, y2, x1, y2],
                            "area": coco_area,
                            "bbox": [coco_x, coco_y, coco_w, coco_h],
                            "iscrowd": 0})
            anno_id += 1
    
    
    cocoset = {"info": {},
                 "license": [],
                 "images": imgs_list,
                 "annotations": annos_list,
                 "categories": cat_list}


    save_path = osp.join(savedir, save_coco_file)
    write_json_file(save_path, cocoset)


def yolo2labelme(yolo_file_dir, img_file_dir, classes_file_path, save_dir):
    # 文件保存的路径
    savedir = make_save_path(save_dir)
    os.makedirs(savedir)
    print("save to: ", savedir)

    # 从文件中 获取 类别名称与类别 ID 的对应关系
    classes_dict = read_json_file(classes_file_path)

    # 迭代 yolo 的 txt 文件
    img_file_list = sorted(os.listdir(img_file_dir))
    for img_name in tqdm(img_file_list):
        imgpath = os.path.join(img_file_dir, img_name)  # img 的路径
        txtpath = os.path.join(yolo_file_dir, img_name.replace("jpg", "txt"))  # txt 的路径
        # print(f"img_file: {img_file} \t txt_file: {txt_file}")

        # 获取 image 的 宽、高
        imgshape = obtain_img_wh(imgpath)

        # img_data = img_encode_b64(imgpath)  # 对 img 编码
        img_data = None

        yolo_txt = read_txt_file(txtpath)

        shapes = []
        for line in yolo_txt:
            line = line.rstrip("\n").split(" ")
            line = [float(i) for i in line]
            
            cat_id = str(int(line[0]))   # 类别的编号
            cat_label = classes_dict[cat_id]    # 类别的名称
            
            x_min, y_min, x_max, y_max = xcycwh2xyxy(line[1:5], imgshape)
            points = [[x_min, y_min], [x_max, y_max]]
            
            group_id = None
            if len(line) >= 6:
                group_id = int(line[5])

            is_verify = None
            if len(line) >= 7:
                is_verify = int(line[6])

            shapes.append({
                "label": cat_label,
                "is_verify": is_verify,
                "points": points,
                "group_id": group_id,
                "shape_type": "rectangle",
                "flags": {}
                })
        
        jsonset = {
            "version": "",
            "flags": {},
            "shapes": shapes,
            "imagePath": img_name,
            "imageData": img_data,
            "imageHeight": imgshape[1],
            "imageWidth": imgshape[0]
            }

        savepath = os.path.join(savedir, img_name.replace("jpg", "json"))
        write_json_file(savepath, jsonset)


def coco2labelme(coco_file_path, save_dir):
    # 文件保存的路径
    savedir = make_save_path(save_dir)
    os.makedirs(savedir)
    print("save to: ", savedir)
    
    json_coco = COCO(coco_file_path)
    img_coco_data = json_coco.loadImgs(json_coco.getImgIds())

    for img in tqdm.tqdm(img_coco_data):
        img_id = img["id"]
        img_width = img["width"]
        img_height = img["height"]
        img_name = img["file_name"]
        img_data = None
        # img_data = img_encode_b64(os.path.join(img_file_dir, img_name))

        anno_ids = json_coco.getAnnIds(img_id)
        
        shapes = []
        for anno_id in anno_ids:
            anno = json_coco.loadAnns(anno_id)[0]
            
            cat_id = anno["category_id"]
            cat_label = json_coco.loadCats(cat_id)[0]["name"]
    
            x1, y1, x2, y2 = xywh2xyxy(anno["bbox"])
            points = [[x1, y1], [x2, y2]]
            
            is_verify = None
            if hasattr(anno, "is_verify"):
                is_verify = anno["is_verify"]

            group_id = None
            if hasattr(anno, "group_id"):
                group_id = anno["group_id"]

            shapes.append({"label": cat_label,
                           "is_verify": is_verify,
                           "points": points,
                           "group_id": group_id,
                           "shape_type": "rectangle",
                           "flags": {}})
        
        jsonset = {"version": "",
                        "flags": {},
                        "shapes": shapes,
                        "imagePath": img_name,
                        "imageData": img_data,
                        "imageHeight": img_height,
                        "imageWidth": img_width}
        
        save_json_file = os.path.join(savedir, img_name.replace("jpg", "json"))
        write_json_file(save_json_file, jsonset)


def labelme2yolo(labelme_file_dir, classes_file_path, save_dir):
    # 文件保存的路径
    savedir = make_save_path(save_dir)
    os.makedirs(savedir)
    print("save to: ", savedir)

    # 从文件中 获取 类别名称与类别 ID 的对应关系
    classes_dict = read_json_file(classes_file_path)
    
    
    
    classes_list = {}
    for id in classes_dict:
        # print(id)
        classes_list[classes_dict[id]] = id

    json_file_list = sorted(os.listdir(labelme_file_dir))
    for filename in tqdm(json_file_list):
        jsonfilepath = osp.join(labelme_file_dir, filename)
        json_data = read_json_file(jsonfilepath)

        imgshape = [json_data["imageWidth"], json_data["imageHeight"]]

        shapes = json_data["shapes"]
        if len(shapes) == 0:
            save_txt_file = os.path.join(save_dir, filename.replace("json", "txt"))
            with open(save_txt_file, "a", encoding="utf8") as tp:
                    tp.write("")
        for shape in shapes:
            label = shape["label"]
            cotegory_id = classes_list[label]
            
            yolo_xc, yolo_yc, yolo_w, yolo_h = xyxy2xcycwh(shape["points"], imgshape)

            group_id = -1
            if hasattr(shape, "group_id"):
                group_id = shape["group_id"]

            is_verify = -1
            if hasattr(shape, "is_verify"):
                is_verify = shape["is_verify"]

            txt_data = f"{cotegory_id} {yolo_xc} {yolo_yc} {yolo_w} {yolo_h} {group_id} {is_verify}\n"

            save_path = os.path.join(save_dir, filename.replace("json", "txt"))
            write_txt_file(save_path, txt_data, mode="a")
 
