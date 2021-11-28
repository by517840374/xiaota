#！ /usr/bin/env python
# -*-.coding: utf-8 -*-

import sys
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
import wave

from api.xfyun.base_api import RoleBase

tts, outfile = "", ""


class TTS(RoleBase):
    """
    语音合成 TTS :Text to Speech
    """
    def __init__(self, Text, OutFile, wavFile=None):
        super(TTS, self).__init__()
        self.Text = Text
        self.OutFile = OutFile
        self.wavFile = wavFile
        self.ws_url = 'wss://tts-api.xfyun.cn/v2/tts'
        self.api = "tts"
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "sfl": 1, "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}


    def pcm2wav(self, pcmfile, wavfile, channels=1, rate=16000):
        with open(pcmfile, 'rb') as fp:
            pcmdata = fp.read()
        with wave.open(wavfile, 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(16 // 8)
            wav.setframerate(rate)
            # 写入
            wav.writeframes(pcmdata)

    def towav(self):
        """
        这里是分割pcm的路径，把转换为WAV格式的放到同目录下；可自行指定路径
        """
        if self.wavFile is None:
            splits = str(self.OutFile).split('/')
            splits.pop(-1)
            splits.append("demo.wav")
            self.wavFile = '/'.join(splits)
        self.pcm2wav(self.OutFile, self.wavFile)


def on_message(ws, message):
    try:
        global outfile
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        #print(message)
        if status == 2:
            #print("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            #print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:

            with open(outfile, 'ab') as f:
                f.write(audio)

    except Exception as e:
        print("receive msg,but parse exception:", e)


def on_error(ws, error):
    pass


def on_close(ws):
    pass


def on_open(ws):
    def run(*args):
        global outfile
        d = {"common": tts.CommonArgs,
             "business": tts.BusinessArgs,
             "data": tts.Data,
             }
        d = json.dumps(d)
        ws.send(d)
        if os.path.exists(outfile):
            os.remove(outfile)

    thread.start_new_thread(run, ())


def synthesize(text, out_file, wavfile):
    global tts, outfile
    outfile = out_file
    tts = TTS(Text=text, OutFile=out_file, wavFile=wavfile)
    tts.run(on_message, on_error, on_close, on_open)
    tts.towav()


if __name__ == "__main__":
    synthesize('你好呀，我好喜欢你啊。', os.getcwd() + "/demo.mp3", None)

