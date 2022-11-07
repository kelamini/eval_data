import os
import json
import argparse


def compare_bbox(bbox1, bbox2):
    try:
        bbox1_list = [float(i) for i in bbox1]
        bbox2_list = [float(j) for j in bbox2]
        if bbox1 == bbox2:
            return True

        return False
    except:
        print("Compare Error!!!")


def merge_gt(root_dir, gt_list, save_file):
    data_list = []  # 存放所有的 gt 数据
    for gt_file in gt_list:
        gt_path = os.path.join(root_dir, gt_file)
        if not os.path.exists(gt_path):
            raise ValueError(f"not exist {gt_path}")
        with open(gt_path, "r") as rp:
            data = json.load(rp)
        data_list.append(data)

    # 比对所有数据
    img_ids = {}        # img_id: img_info
    categories_ids = {}  # cat_id: cat_info
    anno_ids = {}       # anno_id: anno_info
    for data in data_list:
        # 比对 images
        dic_img_id = {}  # old img_id: new img_id
        for img_info in data["images"]:
            cur_img_id = img_info["id"]     # img_id
            if cur_img_id not in img_ids:   # 当前 img_id 不同于之前的 img_id
                img_ids[cur_img_id] = img_info
            else:   # 当前的 img_id 与之前的 img_id 相同
                if img_info["file_name"] == img_ids[cur_img_id]["file_name"]:   # img_name 也相同
                    continue
                else:   # img_name 不相同, 说明 有新的 image
                    new_id = max(img_ids.keys()) + 1
                    dic_img_id[cur_img_id] = new_id
                    img_ids[new_id] = img_info

        # 比对 categories
        dic_categories_id = {}  # old cat_id: new cat_id
        for categories_info in data["categories"]:
            cur_categories_id = categories_info["id"]
            if cur_categories_id in categories_ids:
                if categories_info["name"] == categories_ids[cur_categories_id]["name"]:
                    continue
                else:
                    new_id = max(categories_ids.keys()) + 1
                    dic_categories_id[cur_categories_id] = new_id
                    categories_ids[new_id] = categories_info
            else:
                categories_ids[cur_categories_id] = categories_info

        # 比对 annotations
        dic_anno_id = {}  # old anno_id: new anno_id
        for anno_info in data["annotations"]:
            if anno_info["image_id"] in dic_img_id:
                anno_info["image_id"] = dic_img_id[anno_info["image_id"]]
            if anno_info["category_id"] in dic_categories_id:
                anno_info["category_id"] = dic_categories_id[anno_info["category_id"]]
            cur_anno_id = anno_info["id"]
            if cur_anno_id in anno_ids:
                if compare_bbox(anno_info["bbox"], anno_ids[cur_anno_id]["bbox"]):
                    continue
                else:
                    new_id = max(anno_ids.keys()) + 1
                    dic_anno_id[cur_anno_id] = new_id
                    anno_ids[new_id] = anno_info
            else:
                anno_ids[cur_anno_id] = anno_info

    json_dict = dict(
        images=list(img_ids.values()),
        annotations=list(anno_ids.values()),
        categories=list(categories_ids.values()),
        info="",
        license=[],
    )
    save_path = os.path.join(root_dir, save_file)
    with open(save_path, 'w', encoding="utf8") as wp:
        json.dump(json_dict, wp, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--root_dir", type=str, default="", help="")
    parser.add_argument("-gt", "--gt_list", nargs="+", default="", help="")
    parser.add_argument("-s", "--save_file", type=str,
                        default="merge_gt.json", help="")

    args = parser.parse_args()

    root_dir = args.root_dir
    gt_list = args.gt_list
    save_file = args.save_file

    merge_gt(root_dir, gt_list, save_file)
