import os
import cv2 as cv
import argparse


"""
视频抽帧
python extact_frame.py -v "video path" -s "save path" -n 50
"""


def video_ext_frame(path, savepath, numframe=50):
    if not os.path.exists(savepath):
        os.mkdir(savepath)
        
    # 获取所有视频的列表
    videolist = os.listdir(path)
    for i, video in enumerate(videolist):
        # 视频文件的名字，不包含后缀
        videoname = video.split(".")[0]
        # videoname = str(i)
        # 视频文件的路径
        videopath = os.path.join(path, video)
        # 获取图像帧
        cap = cv.VideoCapture(videopath)
        # 如果没有打开视频文件，则报错并退出
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        # 用于抽取帧的计数
        cnt = 0
        videosavepath = os.path.join(savepath, videoname)
        print(videosavepath)
        if not os.path.exists(videosavepath):
            os.makedirs(videosavepath)
        
        while True:
            cnt += 1
            # 逐帧捕获
            ret, frame = cap.read()
            
            # 读取帧错误将报错，并退出
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            
            # 计数为 numframe 的倍数将被抽出
            if cnt % numframe == 0:
                picture = os.path.join(videosavepath, f"{videoname}_{cnt}.jpg")
                cv.imwrite(picture, frame)

        cap.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("-v", "--video_path", type=str, default="./video", help="")
    parser.add_argument("-s", "--save_path", type=str, default="./videoframe", help="")
    parser.add_argument("-n", "--num_frame", type=int, default=50, help="")

    args = parser.parse_args()
    videopath = args.video_path
    savepath = args.save_path
    numframe = args.num_frame
    video_ext_frame(videopath, savepath, numframe)
