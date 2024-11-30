# import imageio
# imageio.plugins.ffmpeg.download()

import requests, time, hashlib, urllib.request, re, json
from moviepy.editor import *
import os, sys

from utils.yaml_parse import DatabaseManager

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

start_time = 0
db_manager = DatabaseManager()


def check_folder():
    # 检查文件夹是否被创建：
    if not os.path.exists(db_manager.download_path):
        os.makedirs(db_manager.download_path)


def download_video(bv_number):
    if os.path.exists(f"{db_manager.download_path}{bv_number}.mp4"):
        print("视频已存在，跳过下载")
        return bv_number
    try:
        # Step 1: 请求元数据，使用了zhouql.vip的接口，感谢！
        meta_url = f"https://bili.zhouql.vip/meta/{bv_number}"
        meta_response = requests.get(meta_url)
        meta_data = meta_response.json()

        # 检查元数据请求是否成功
        if meta_data["code"] != 0:
            print("元数据请求失败:", meta_data["message"])
            return

        # 提取cid和aid
        cid = meta_data["data"]["cid"]
        aid = meta_data["data"]["aid"]
        print(f"获取的cid: {cid}, aid: {aid}")

        # Step 2: 请求下载链接
        download_url = f"https://bili.zhouql.vip/download/{aid}/{cid}"
        download_response = requests.get(download_url)
        download_data = download_response.json()
        print(f"下载数据: {download_data}")

        # 检查下载链接请求是否成功
        if download_data["code"] != 0:
            print("下载链接请求失败:", download_data["message"])
            return

        # 获取视频下载URL
        video_url = download_data["data"]["durl"][0]["url"]
        print(f"视频下载链接: {video_url}")

        # Step 3: 下载视频
        video_response = requests.get(video_url, stream=True, headers=HEADERS)

        # 定义保存视频的文件名
        check_folder()

        file_name = fr"{db_manager.download_path}{bv_number}.mp4"

        # 获取总大小
        total_size = int(video_response.headers.get('content-length', 0))
        downloaded_size = 0  # 已下载大小

        # 保存视频到本地并显示进度条
        with open(file_name, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)

                    # 计算进度
                    percent_complete = downloaded_size / total_size * 100
                    # 打印进度条
                    progress = int(percent_complete // 2)  # 控制进度条宽度
                    if int(round(percent_complete, 2) * 100) % 100 == 0:
                        # print(int(round(percent_complete,2)*100))
                        sys.stdout.write(f"\r下载进度: [{'#' * progress}{' ' * (50 - progress)}] {percent_complete:.2f}%")
                        sys.stdout.flush()

        print(f"\n视频已成功下载到: {file_name}")
        return bv_number


    except Exception as e:
        print("发生错误:", str(e))
