import os
import os.path as osp
import json
import cv2 as cv
from tqdm import tqdm
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="")
    
    parser.add_argument("-j", "--json_dir", type=str, default="/home/kelaboss/admin1_data/path/selt_result/result_demo/N-vnp-1min", help="")
    parser.add_argument("-i", "--img_dir", type=str, default="/home/kelaboss/admin1_data/path/selt_result/img_demo/N-vnp-1min", help="")

    args = parser.parse_args()

    return args


def read_json_file(filepath):
    with open(filepath, "r", encoding="utf8") as fp:
        data = json.load(fp)

    return data


def write_json_file(filepath, info):
    with open(filepath, "w", encoding="utf8") as fp:
        json.dump(info, fp, indent=2)

def process_name(args):
    jsonfile_dir = args.json_dir
    img_dir = args.img_dir

    imgfile_list = sorted(os.listdir(img_dir))
    for filename in tqdm(imgfile_list):
        imgpath = osp.join(img_dir, filename)
        img = cv.imread(imgpath)
        imgshape = img.shape
        jsonpath = osp.join(jsonfile_dir, filename.replace("jpg", "json"))
        try:
            json_data = read_json_file(jsonpath)
        except:
            continue
        
        json_data["imageWidth"] = imgshape[1]
        json_data["imageHeight"] = imgshape[0]
        json_data["imageData"] = None
        json_data["imagePath"] = filename
            
        write_json_file(jsonpath, json_data)
        try:
            del(json_data["imgageData"])
            
        except:
            continue


if __name__ == "__main__":
    opts = get_args()

    process_name(opts)
