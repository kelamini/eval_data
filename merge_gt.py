import argparse
import json
import os

from pycocotools.coco import COCO
from tqdm import tqdm


def compare_bbox(bbox):
    try:
        bbox_list = [int(i) for i in bbox]

        return str(bbox_list)
    except:
        print("Compare Error!!!")


def merge_gt(root_dir, gt_list, save_file):
    data_list = []  # 存放所有的 gt 数据
    for i, gt_file in enumerate(gt_list):
        gt_path = os.path.join(root_dir, gt_file)
        if not os.path.exists(gt_path):
            raise ValueError(f"not exist {gt_path}")
        with open(gt_path, "r", encoding="utf8") as rp:
            data = json.load(rp)
        data_list.append(data)
        print(f'{i}: images_len-{len(data["images"])}, annos_len-{len(data["annotations"])}, cats_len-{len(data["categories"])}')

    # 比对所有数据
    cat_dict = {}  # cat_id: cat_info
    img_dict = {}        # img_name: img_info
    anno_dict = {}       # anno_id: anno_info

    dic_cat_id = {}  # old cat_id: new cat_id
    dic_img_id = {}  # old img_id: new img_id
    dic_anno_id = {}    # bbox_id: new anno_id

    img_id = 0
    anno_id = 0

    for i, data in enumerate(data_list):
        coco_data = COCO(gt_list[i])

        # 比对 categories
        
        for cat_info in data["categories"]:
            cur_cat_id = cat_info["id"]
            if cur_cat_id in cat_dict:
                if cat_info["name"] == cat_dict[cur_cat_id]["name"]:
                    continue
                else:
                    new_id = max(cat_dict.keys()) + 1
                    dic_cat_id[cur_cat_id] = new_id
                    cat_dict[new_id] = cat_info
            else:
                cat_dict[cur_cat_id] = cat_info

        # 比对 images
        
        for img_info in tqdm(data["images"]):
            cur_img_id = img_info["id"] # 当前 img_id
            anno_list = coco_data.loadAnns(coco_data.getAnnIds(cur_img_id)) # 当前 img_id 对应的所有 annotations
            
            cur_img_name = img_info["file_name"]    # 获取当前 img_name
            if cur_img_name not in img_dict:   # 当前 img_name 不同于之前的 img_name (新加的 image)
                img_info["id"] = img_id
                dic_img_id[cur_img_id] = img_id    # 将 img_name 与 新 img_id 对应
                img_dict[cur_img_name] = img_info    # 此时 img_id 已经更新

            img_id += 1

            # 比对 annotations
            
            for anno_info in anno_list:
                # 更新 img_id 和 anno_id
                bbox_id = compare_bbox(anno_info["bbox"])
                if bbox_id not in dic_anno_id: # 新添加了 image
                    anno_info["image_id"] = dic_img_id[anno_info["image_id"]]
                    dic_anno_id[bbox_id] = anno_id
                    anno_info["id"] = anno_id

                    anno_id += 1
                    
                else:   # 还是原来的 image
                    anno_info["image_id"] = img_dict[cur_img_name]["id"]
                    anno_info["id"] = dic_anno_id[bbox_id]
                
                anno_dict[anno_info["id"]] = anno_info
    
    json_dict = dict(
        images=list(img_dict.values()),
        annotations=list(anno_dict.values()),
        categories=list(cat_dict.values()),
        info="",
        license=[],
    )
    
    print(f'merge: images_len-{len(json_dict["images"])}, annos_len-{len(json_dict["annotations"])}, cats_len-{len(json_dict["categories"])}')
    
    save_path = os.path.join(root_dir, save_file)
    with open(save_path, 'w', encoding="utf8") as wp:
        json.dump(json_dict, wp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--root_dir", type=str, default="", help="")
    parser.add_argument("-gt", "--gt_list", nargs="+", default="", help="")
    parser.add_argument("-s", "--save_file", type=str, default="merge_gt.json", help="")

    args = parser.parse_args()

    root_dir = args.root_dir
    gt_list = args.gt_list
    save_file = args.save_file

    merge_gt(root_dir, gt_list, save_file)
