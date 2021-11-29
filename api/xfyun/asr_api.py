#！ /usr/bin/env python
# -*-.coding: utf-8 -*-

import websocket
import datetime
import hashlib
import base64
import sys
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
from api.xfyun.base_api import RoleBase

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识
MSG = []
asr = ""


class ASR(RoleBase):
    def __init__(self, AudioFile):
        super(ASR, self).__init__()
        self.AudioFile = AudioFile
        self.ws_url = "wss://ws-api.xfyun.cn/v2/iat"
        self.api = "iat"
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 0, "vad_eos": 10000}


def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            global MSG
            _msg = ""
            for i in data:
                for w in i["cw"]:
                    _msg += w["w"]
            MSG.append(_msg)
    except Exception as e:
        print("receive msg,but parse exception:", e)


def on_open(ws):
    def run(*args):
        global asr
        frameSize = 8000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(asr.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": asr.CommonArgs,
                         "business": asr.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())


def on_error(ws, error):
    pass


def on_close(ws):
    pass


def distinguish(audio_file):
    global MSG, asr
    asr = ASR(AudioFile=audio_file)
    asr.run(on_message, on_error, on_close, on_open)
    return MSG


if __name__ == '__main__':
    distinguish("./demo.wav")