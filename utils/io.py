from pathlib import Path
import glob
import json
import re


def increment_path(path, exist_ok=False, sep='', mkdir=False):
    # Increment file or directory path, i.e. runs/exp --> runs/exp{sep}2, runs/exp{sep}3, ... etc.
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(''), path.suffix) if path.is_file() else (path, '')
        dirs = glob.glob(f"{path}{sep}*")  # similar paths
        matches = [re.search(rf"%s{sep}(\d+)" % path.stem, d) for d in dirs]
        i = [int(m.groups()[0]) for m in matches if m]  # indices
        n = max(i) + 1 if i else 2  # increment number
        path = Path(f"{path}{sep}{n}{suffix}")  # increment path
    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory
    return path


def make_save_path(savedir, name="exp"):
    save_dir = increment_path(Path(savedir) / name, exist_ok=False)
    print(f"The resault save to {save_dir}\n")

    return save_dir


def read_json_file(filepath, mode="r"):
    with open(filepath, mode, encoding="utf8") as fp:
        json_data = json.load(fp)

    return json_data


def write_json_file(filepath, data, mode="w", indent=2):
    with open(filepath, mode, encoding="utf8") as fp:
        json.dump(data, fp, indent)


def read_txt_file(filepath, mode="r"):
    with open(filepath, mode, encoding="utf8") as fp:
        data = fp.readlines()

    return data


def write_txt_file(filepath, data, mode="w"):
    with open(filepath, mode, encoding="utf8") as fp:
        fp.write(data)
