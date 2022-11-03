from pycocotools.coco import COCO
import os


path = "/home/kelaboss/datasets/coco/annotations/instances_val2017.json"
save_name = "classes_self.txt"

if os.path.exists(save_name):
    os.remove(save_name)
cov2017 = COCO(path)

cat_ids = cov2017.getCatIds()
# print(cat_ids)
# cats = cov2017.loadCats(cat_ids)

for i, catid in enumerate(cat_ids):
    cats = cov2017.loadCats(catid)[0]["name"]

    # print(catid, cats)

    with open(save_name, "a", encoding="utf8") as wp:
        wp.write(f"{cats}\n")
