import os
import time

import ffmpeg
import m3u8
import requests
from lxml import html

from util import convert_log, convert_mp3_to_text, progress_bar, merge_videos, convert_log_md
from utils.exAudio import flv_mp3
from utils.yaml_parse import ConfigManager

config_manager = ConfigManager()
show_log = config_manager.show_log
today = time.strftime("%Y-%m-%d", time.localtime())

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                  'Safari/537.36'}


def replace_last_segment(url, new_content):
    # 找到最后一个斜杠的位置
    last_slash_index = url.rfind('/')

    if last_slash_index == -1:
        # 如果没有找到斜杠，直接返回新的内容
        return new_content

    # 替换最后一个斜杠后面的内容
    new_url = url[:last_slash_index + 1] + new_content
    return new_url


def download_m3u8(m3u8_url, file_name, output_dir=f'{config_manager.download_path}'):
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    response = requests.get(m3u8_url)
    m3u8_content = response.text
    playlist = m3u8.loads(m3u8_content)
    if show_log:
        print(f'playlist:{playlist.playlists}, {playlist.data}')

    # playlists = [playlists.uri for playlists in playlist.playlists]
    playlists = playlist.playlists[0]
    if show_log:
        print(f'playlists:{playlists}')

    video_url = f'https://dh5.cntv.myalicdn.com{playlists.uri}'
    if show_log:
        print(f'video_url:{video_url}')
    response = requests.get(video_url)
    m3u8_content = response.text
    playlist = m3u8.loads(m3u8_content)

    if show_log:
        print(f'单个视频信息:{playlist.playlists}, {playlist.data}')

    # 获取所有媒体片段的 URL
    segment_urls = [segment.uri for segment in playlist.segments]

    if show_log:
        print(f'segment_urls:{segment_urls}')

    print('开始下载所有媒体片段')
    segment_files = []
    input_streams = []
    for i, url in enumerate(segment_urls):
        segment_response = requests.get(replace_last_segment(video_url, url))
        segment_file = os.path.join(output_dir, f'{today}segment_{i + 1}.ts')
        with open(segment_file, 'wb') as f:
            f.write(segment_response.content)
        segment_files.append(segment_file)
        input_stream = ffmpeg.input(segment_file)
        input_streams.append(input_stream)
        progress_bar(i, len(segment_urls))
    if show_log:
        print(f'所有片段下载完成:{segment_files}')
    output_file = f'{output_dir}{file_name}.ts'

    merge_videos(segment_files, output_file)
    print(f'所有片段合并完成:{output_file}')
    # 清理临时文件
    for segment_file in segment_files:
        os.remove(segment_file)
    return output_file


if __name__ == '__main__':
    base_url = 'https://tv.cctv.com/2024/12/02/VIDEQ7JTCOmuMw5T5qekYv7c241202.shtml'
    m3u8_url = 'https://dh5.cntv.lxdns.com/asp/h5e/hls/main/0303000a/3/default/bd496547c8464a0bae4d064df462313b/main.m3u8?maxbr=2048&contentid=15120519184043'
    html_content = requests.get(base_url, headers=HEADERS)
    # 解析HTML内容
    tree = html.fromstring(html_content.content)
    # 使用XPath获取内容简介
    synopsis = tree.xpath('//*[@id="page_body"]/div[1]/div[2]/div[2]/div[2]/div/ul/li[1]/p/text()')[0]
    title = tree.xpath('//*[@id="page_body"]/div[1]/div[2]/div[1]/div[2]/text()')[0]
    if show_log:
        print(f'标题:{title}, 简介:{synopsis}')
    convert_log_md(synopsis, title, base_url, convert_mp3_to_text(flv_mp3(download_m3u8(m3u8_url, title))))
    # convert_mp3_to_text(flv_mp3("2024-12-02新闻联播.ts"))
