import os
import ast
import numpy as np


# 计算交集
def intersect(box_a, box_b):
    x_min = np.max([box_a[0], box_b[0]])
    x_max = np.min([box_a[2], box_b[2]])
    y_min = np.max([box_a[1], box_b[1]])
    y_max = np.min([box_a[3], box_b[3]])

    inter_area = (x_max - x_min) * (y_max - y_min)
    if x_max-x_min < 0 or y_max-y_min < 0:
        inter_area = 0

    return inter_area

# 计算 box 的 iou
def box_iou(box_a, box_b):
    inter = intersect(box_a, box_b)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - inter
    return inter / union

# 计算 kpt 的 loss
def kpt_loss(pre_point, gt_point, W, H):
    difflist = []
    for prei, gti in zip(range(0, len(pre_point)+2, 2), range(0, len(pre_point)+3, 3)):
        x_diff = ((pre_point[prei] - gt_point[gti])/W)**2
        y_diff = ((pre_point[prei+1] - gt_point[gti+1])/H)**2
        difflist.append(np.sqrt(x_diff+y_diff))
    
    return np.sum(difflist) / 5.0


# 获取真实数据
def obt_gt_data(gtpath):
    with open(gtpath, "r", encoding="utf8") as gf:
        gtdata = gf.readlines()
    
    gt_imgnamelist = []
    gt_dataset = {}
    for row in gtdata:
        if "#" in row:
            datalist = []
            img_name = row.split(" ")[-3]
            gt_imgnamelist.append(img_name)
        else:
            data = list(map(float, row.split(" ")))
            datalist.append(data)
        gt_dataset[img_name] = datalist
    
    return gt_imgnamelist, gt_dataset

# 获取预测数据
def obt_pre_data(prepath):
    with open(prepath, "r", encoding="utf8") as pf:
        predata = pf.readlines()
    
    pre_imgnamelist = []
    pre_dataset = {}
    for row in predata:
        img_name = row.split(";")[0].split("/")[-2]+"/"+row.split(";")[0].split("/")[-1]
        pre_imgnamelist.append(img_name)
        try:
            boxes = ast.literal_eval(row.split(";")[1].split("=")[-1])
            kpts = ast.literal_eval(row.split(";")[2].split("=")[-1])
        except:
            boxes = []
            kpts = []
        
        datalist = []
        for box, kpt in zip(boxes, kpts):
            
            data = list(map(float, box+kpt))
            datalist.append(data)
        pre_dataset[img_name] = datalist


    return pre_imgnamelist, pre_dataset

# 评估
def eval_loss(gt_info, pre_info):
    # 获取一幅图像上的数据 取预测数据与真实数据进行比对
    TP, FP, FN = 0, 0, 0
    kptlosslist = []
    all_gtdatalen, all_predatalen = 0, 0
    gt_nodata = 0
    for imgname in pre_info:
        if imgname in gt_info:
            # TP, FP, FN = 0, 0, 0
            gt_data = np.array(gt_info[imgname])
            pre_data = np.array(pre_info[imgname])
            FN += len(gt_data) - len(pre_data)  # 真实数据中有但没有预测到
            all_gtdatalen += len(gt_data)   # 获取所有真实数数的数量
            all_predatalen += len(pre_data) # 获取所有预测数据的数量
            # if len(gt_data) == 0:
            #     print(gt_data)
            # 循环处理单个预测框及关键点
            for pre_single in pre_data:
                boxioulist = []     # 存放 单个预测框与所有真实框的 iou
                # 真实数据不为空
                if len(gt_data) != 0:
                    # 比对所有真实框
                    for gt_single in gt_data:
                        boxiou = box_iou(pre_single[:4], gt_single[:4])
                        boxioulist.append(boxiou)
                    
                    # if len(boxioulist) != 0:
                    box_iou_max = np.max(boxioulist)   # 比对结果 iou 最大的框 其 iou 值
                    maxindex = np.argmax(boxioulist)  # 获取 iou 最大 的索引 用于比对该框对应的关键点
                    # 该 框 iou 符合阈值 比对其关键点
                    if box_iou_max > 0.5 and -1 not in gt_data[maxindex]:
                        W, H = gt_data[maxindex][2] - gt_data[maxindex][0], gt_data[maxindex][3] - gt_data[maxindex][1]
                        kptloss = kpt_loss(pre_single[5:], gt_data[maxindex][4:], W, H)
                        # print(len(gt_data[maxindex][4:-1]), len(pre_single[5:]), kptloss)
                        kptlosslist.append(kptloss)
                        
                        TP += 1
                    else:
                        FP += 1
                # gt 中 image 没有数据
                else:
                    gt_nodata += 1
        
            # precision = 0
            # recall = 0
            # if TP != 0:
            #     precision  = TP / (TP + FP)
            #     recall = TP / (TP + FP + FN)
            # print(f"""for {imgname} has:
            #         pre_box_total: {len(pre_data)}
            #         gt_box_total: {len(gt_data)}
            #         TP: {TP}
            #         FP: {FP}
            #         FN: {FN}
            #         kpt_loss: {kptlosslist}
            #         precision: {precision}
            #         recall: {recall}""")
        
        else:
            print(f"{imgname} is not match any gt data")

        # jsonset = {}
        # jsonset["ImageName"] = imgname
        # processdata = {}
        # processdata["TP"] = TP
        # processdata["FP"] = FP
        # processdata["FN"] = FN
        # processdata["KptLoss"] = kptlosslist
        # processdata["Precision"] = precision
        # processdata["Recall"] = recall

        # jsonset["Data"] = processdata

    precision = 0
    recall = 0
    if TP != 0:
        precision  = TP / (TP + FP)
        recall = TP / (TP + FN)
        mkptloss = np.sum(kptlosslist)/len(kptlosslist)
        F1 = 2*(precision*recall/(precision+recall))
    
    print(f"""for all image has:
                    pre_box_total: {all_predatalen-gt_nodata}
                    gt_box_total: {all_gtdatalen-gt_nodata}
                    TP: {TP}
                    FP: {FP}
                    FN: {FN}
                    kpt_loss: {mkptloss}
                    precision: {precision}
                    recall: {recall}
                    F1-score: {F1}""")


if __name__ == "__main__":
    gt_path = "label.txt"
    pre_path = "wider_eval_yolox.txt"

    _, gt_dataset = obt_gt_data(gt_path)
    # print(gt_dataset)
    _, pre_dataset = obt_pre_data(pre_path)
    # print(pre_dataset)

    eval_loss(gt_dataset, pre_dataset)
