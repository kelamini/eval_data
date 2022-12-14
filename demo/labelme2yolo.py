from utils.format_converter import labelme2yolo
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-l', '--labelme_file_dir', default='', type=str, help="")
    parser.add_argument('-c', '--classes_file_path', default='', type=str, help="")
    parser.add_argument('-s', '--save_dir', type=str, default='', help="")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    
    labelme_file_dir = args.labelme_file_dir
    classes_file_path = args.classes_file_path
    save_dir = args.save_dir
    
    labelme2yolo(labelme_file_dir, classes_file_path, save_dir)
    