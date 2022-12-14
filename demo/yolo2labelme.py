from utils.format_converter import yolo2labelme
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-y', '--yolo_file_dir', default='', type=str, help="")
    parser.add_argument('-i', '--img_file_dir', default='', type=str, help="")
    parser.add_argument('-c', '--classes_file_path', default='../configs/classes_coco.json', type=str, help="")
    parser.add_argument('-s', '--save_dir', type=str, default='', help="")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    
    yolo_file_dir = args.yolo_file_dir
    img_file_dir = args.img_file_dir
    classes_file_path = args.classes_file_path
    save_dir = args.save_dir
    
    yolo2labelme(yolo_file_dir, img_file_dir, classes_file_path, save_dir)
    