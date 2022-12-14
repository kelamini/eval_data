from pycocotools.coco import COCO
import os
import json


path = "/home/kelaboss/datasets/coco/annotations/instances_val2017.json"
save_name = "classes_self.json"

if os.path.exists(save_name):
    os.remove(save_name)
cov2017 = COCO(path)

cat_ids = cov2017.getCatIds()
# print(cat_ids)
# cats = cov2017.loadCats(cat_ids)

classes_json = {}
for i, catid in enumerate(cat_ids):
    cats = cov2017.loadCats(catid)[0]["name"]
    classes_json.update({int(catid):cats})

    # print(catid, cats)

with open(save_name, "w", encoding="utf8") as wp:
    json.dump(classes_json, wp, indent=2)
