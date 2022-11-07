import os
import shutil
from pycocotools.coco import COCO
import argparse
import tqdm


def coco2labelme(json_cocofile, save_path):

    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.mkdir(save_path)
    
    json_coco = COCO(json_cocofile)
    img_data = json_coco.loadImgs(json_coco.getImgIds())

    for img in tqdm.tqdm(img_data):
        img_id = img["id"]
        img_width = img["width"]
        img_height = img["height"]
        img_name = img["file_name"]

        anno_ids = json_coco.getAnnIds(img_id)

        for anno_id in anno_ids:
            anno = json_coco.loadAnns(anno_id)[0]
            
            cat_id = anno["category_id"]
    
            bbox = anno["bbox"]
            box_x_center = (bbox[0]+bbox[2]/2)/img_width
            box_y_center = (bbox[1]+bbox[3]/2)/img_height
            box_width = bbox[2]/img_width
            box_height = bbox[3]/img_height

            txt_data = f"{cat_id} {box_x_center} {box_y_center} {box_width} {box_height}\n"

            save_txt_file = os.path.join(save_path, str(img_name).split(".")[0]+".txt")

            with open(save_txt_file, "a", encoding="utf8") as tp:
                tp.write(txt_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json_file', default='old_coco_data.json', type=str, help="")
    parser.add_argument('-s', '--save_path', type=str, default='coco2yolo_result', help="")

    arg = parser.parse_args()

    json_file = arg.json_file
    save_path = arg.save_path

    coco2labelme(json_file, save_path)
