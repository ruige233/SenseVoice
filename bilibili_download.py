import re
import time

from utils.downBili import download_video
from utils.exAudio import flv_mp3
from utils.http_util import get_video_title
from utils.yaml_parse import ConfigManager
from util import convert_mp3_to_text, convert_log

config_manager = ConfigManager()


def get_video_text(video_link):
    if video_link == "":
        print("视频链接不能为空！")
        return

    pattern = r'BV[A-Za-z0-9]+'  # 正则表达式
    match = re.findall(pattern, video_link)
    match = match[0]

    print(f"视频链接: {video_link}")
    print(f"BV号: {match}")
    bv = match
    result = process_video(bv[2:])
    convert_log(bv[2:], get_video_title(url), video_link, result)


def process_video(bv):
    print("=" * 10)
    print("正在下载视频...")
    filename = download_video(str(bv))
    print("=" * 10)
    return convert_mp3_to_text(flv_mp3(filename))


if __name__ == "__main__":
    while True:
        url = input("输入B站视频链接: ")
        start_time = time.time()
        get_video_text(url)
        print(f"方法执行耗时: {time.time() - start_time} 秒")
