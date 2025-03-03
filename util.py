import json
import os
import subprocess
import sys
import time
import markdown

from bs4 import BeautifulSoup
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from funasr import AutoModel

from utils.yaml_parse import ConfigManager

config_manager = ConfigManager()


def convert_log(bv, video_name, url, result):
    convert_log_file = config_manager.convert_log + time.strftime('%Y%m%d') + '.json'

    if not os.path.exists(convert_log_file):
        if not os.path.exists(config_manager.convert_log):
            os.makedirs(config_manager.convert_log)
        with open(convert_log_file, 'w', encoding="utf-8") as file:
            json.dump([], file, indent=4)

    # 读取现有数据
    with open(convert_log_file, 'r', encoding="utf-8") as file:
        data = json.load(file)

    # 添加新的记录
    data.append({'timestamp': time.strftime('%H:%M:%S'), 'bv号': bv, '视频名称': video_name, '视频链接': url, '转换结果': result})

    # 将更新后的数据写回文件
    with open(convert_log_file, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def convert_log_md(bv, video_name, url, result):
    convert_log_file = config_manager.convert_log + time.strftime('%Y%m%d') + '.md'

    if not os.path.exists(convert_log_file):
        if not os.path.exists(config_manager.convert_log):
            os.makedirs(config_manager.convert_log)
        with open(convert_log_file, 'w', encoding="utf-8") as file:
            json.dump(None, file, indent=4)

    # 读取现有数据
    with open(convert_log_file, 'r', encoding="utf-8") as file:
        content = file.read()

    new_content = markdown.markdown(str(BeautifulSoup(
        f'''<br/>
            <h1>{video_name}</h1>
            <p>bv号/视频简介：{bv}</p>
            <p>视频链接: {url}</p>
            <p>转换时间: {time.strftime('%H:%M:%S')}</p>
            <p>转换结果: {result}</p>
            <br/>''', 'html.parser')))

    # 将更新后的数据写回文件
    with open(convert_log_file, 'w', encoding="utf-8") as file:
        file.write(content + new_content)


# 进度条
def progress_bar(current, total, bar_length=50):
    percent_complete = current / total * 100
    # sys.stdout.write(f"\r下载进度:{current}/{total} {percent_complete:.2f}%")
    # 打印进度条
    progress = int(percent_complete // 2)  # 控制进度条宽度
    # if int(round(percent_complete, 2) * 100) % 100 == 0:
    # print(int(round(percent_complete,2)*100))
    sys.stdout.write(f"\r下载进度: [{'#' * progress}{' ' * (50 - progress)}] {percent_complete:.2f}%({current}/{total})")
    sys.stdout.flush()


# <editor-fold desc="MP5生成文本">
model_dir = "iic/SenseVoiceSmall"
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


# convert_mp3_to_text
def convert_mp3_to_text(file, keepOriginalFile=False):
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
    print('识别成功：', text)
    if not keepOriginalFile:
        os.remove(file)
    return text


def convert_mp3_to_file(file, keepOriginalFile=False, output_file=None):
    text = convert_mp3_to_text(file, keepOriginalFile)
    if output_file is None:
        output_file = file + '.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return output_file
    # </editor-fold>


def merge_videos(input_files, output_file):
    # 构建FFmpeg命令
    command = [
        'ffmpeg',
        '-i', 'concat:' + '|'.join(input_files),  # 连接输入文件
        '-c', 'copy',  # 复制流而不重新编码
        output_file  # 输出文件
    ]
    subprocess.run(command, check=True)
