import os
import json
import argparse
from tqdm import tqdm_gui


def add_anno():

    with open(old_file, "r", encoding="utf8") as ofp:
        old_data = json.load(ofp)

    with open(new_file, "r", encoding="utf8") as nfp:
        new_data = json.load(nfp)

    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-old', '--old_file', default='old_coco_data.json', type=str, help="")
    parser.add_argument('-new', '--new_file', default='new_coco_data.json', type=str, help="")

    arg = parser.parse_args()

    old_file = arg.old_file
    new_file = arg.new_file

    add_anno(old_file, new_file)