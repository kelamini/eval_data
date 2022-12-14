from utils.format_converter import coco2yolo
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-c', '--coco_file_path', default='', type=str, help="")
    parser.add_argument('-s', '--save_dir', type=str, default='', help="")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    coco_file_path = args.coco_file_path
    save_dir = args.save_dir
    
    coco2yolo(coco_file_path, save_dir)
    