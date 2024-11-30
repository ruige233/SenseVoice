import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

from utils.downBili import download_video
from utils.exAudio import run_split, flv_mp3
from utils.yaml_parse import DatabaseManager

model_dir = "iic/SenseVoiceSmall"
db_manager = DatabaseManager()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                  'Safari/537.36'}

model = AutoModel(
    # model_dir：模型名称，或本地磁盘中的模型路径。
    model=model_dir,
    # trust_remote_code=True,
    # remote_code="./model.py",
    # vad_model：表示开启 VAD，VAD 的作用是将长音频切割成短音频，此时推理耗时包括了 VAD 与 SenseVoice 总耗时，为链路耗时，如果需要单独测试 SenseVoice 模型耗时，可以关闭 VAD 模型。
    vad_model="fsmn-vad",
    # vad_kwargs：表示 VAD 模型配置，max_single_segment_time:表示vad_model 最大切割音频时长，单位是毫秒 mS。
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",
)


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
    convert_log(bv[2:], get_video_title(), video_link, result)


def convert_log(bv, video_name, url, result):
    convert_log_file = db_manager.convert_log + time.strftime('%Y%m%d') + '.json'

    # 检查文件夹是否被创建：
    if not os.path.exists(db_manager.convert_log):
        os.makedirs(db_manager.convert_log)

    if not os.path.exists(convert_log_file):
        with open(convert_log_file, 'w', encoding="utf-8") as file:
            json.dump([], file, indent=4)

    # 读取现有数据
    with open(convert_log_file, 'r', encoding="utf-8") as file:
        data = json.load(file)

    # 添加新的记录
    data.append({'timestamp': time.strftime('%H%M%S'), 'bv号': bv, '视频名称': video_name, '视频链接': url, '转换结果': result})

    # 将更新后的数据写回文件
    with open(convert_log_file, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def process_video(bv):
    print("=" * 10)
    print("正在下载视频...")
    filename = download_video(str(bv))
    print("=" * 10)
    return generate(flv_mp3(filename))


# generate
def generate(file):
    res = model.generate(
        # input=f"{model.model_path}/example/en.mp3",
        input=file,
        cache={},
        language="auto",  # "zh", "en", "yue", "ja", "ko", "no  speech"
        # use_itn：输出结果中是否包含标点与逆文本正则化。
        use_itn=True,
        # batch_size_s 表示采用动态 batch，batch 中总音频时长，单位为秒 s。
        batch_size_s=60,
        # merge_vad：是否将 vad 模型切割的短音频碎片合成，合并后长度为merge_length_s ，单位为秒 s。
        merge_vad=True,
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    print(text)
    return text


def get_video_title():
    try:
        response = requests.get(user_input, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "标题未找到"
        return title
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return ''
    except Exception as e:
        print(f"解析错误: {e}")
        return ''


if __name__ == "__main__":
    user_input = input("输入B站视频链接: ")
    start_time = time.time()
    get_video_text(user_input)
    print(f"方法执行耗时: {time.time() - start_time} 秒")
