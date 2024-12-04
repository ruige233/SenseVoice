from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os
import time

from utils.yaml_parse import ConfigManager

db_manager = ConfigManager()


def flv_mp3(source_file):
    print(f"mp3转换文件：{source_file}")
    mp3_file = f"{source_file}.mp3"
    if os.path.exists(mp3_file):
        print("mp3已存在，跳过转换")
        return mp3_file
    # 将FLV视频文件加载为一个VideoFileClip对象
    clip = VideoFileClip(source_file)
    # 提取音频部分
    audio = clip.audio
    os.makedirs(db_manager.download_path, exist_ok=True)
    # 将音频保存为一个文件（例如MP3），写入conv文件夹
    audio.write_audiofile(mp3_file)
    print(f"mp3转换完成：{mp3_file}")
    os.remove(source_file)
    return mp3_file


def split_mp3(filename, folder_name, slice_length=45000, target_folder=db_manager.download_path):
    # 加载MP3文件
    audio = AudioSegment.from_mp3(filename)

    # 计算分割的数量
    total_slices = len(audio) // slice_length

    # 确保目标文件夹存在
    os.makedirs(os.path.join(target_folder, folder_name), exist_ok=True)

    for i in range(total_slices):
        # 分割音频
        start = i * slice_length
        end = start + slice_length
        slice = audio[start:end]

        # 构建保存路径
        slice_filename = f"{folder_name}/{i + 1}.mp3"
        slice_path = os.path.join(target_folder, slice_filename)

        # 导出分割的音频片段
        slice.export(slice_path, format="mp3")
        print(f"Slice {i} saved: {slice_path}")


# 运行切割函数
def run_split(name):
    # 运行转换
    return flv_mp3(name)

    # 运行切割
    # split_mp3(f"audio/conv/{folder_name}.mp3", folder_name)
    # return folder_name
