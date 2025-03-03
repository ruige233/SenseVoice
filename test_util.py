import os
from unittest import TestCase

from util import convert_mp3_to_text, convert_mp3_to_file
from utils.exAudio import flv_mp3


class Test(TestCase):
    def test_convert_mp3_to_text(self):
        find_mp3_files('D:\\360MoveData\\Users\\Administrator\\Desktop\\时间管理10堂课')


def find_mp3_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            fileType = os.path.splitext(file)[1].lower()
            if fileType == '.mp3' or fileType == '.m4a' or fileType == '.wav':
                print('Found mp3 file:', os.path.join(root, file))
                print('converter to', convert_mp3_to_file(os.path.join(root, file), True))
