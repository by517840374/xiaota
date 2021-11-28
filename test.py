#！ /usr/bin/env python
# -*-.coding: utf-8 -*-
import os
import wave
import time
import pyaudio
from api.baidu.unit_api import get_robot_msg
from api.xfyun.asr_api import distinguish
from api.xfyun.tts_api import synthesize
from ctypes import *
from contextlib import contextmanager

fname = "api/xfyun/demo.wav"
outfile = "temp/ttt.wav"

def py_error_handler(filename, line, function, err, fmt):
    pass


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)


@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass


def play_audio_file(fname):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    with no_alsa_error():
        audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()


asr_msg = distinguish(fname)
print(asr_msg)
tts_msg_lst = get_robot_msg(asr_msg)
print(tts_msg_lst)
import random
tts_msg = random.choice(tts_msg_lst)
synthesize(tts_msg, fname, outfile)
print(outfile)
play_audio_file(outfile)
# os.popen("sudo python3 %s %s %s" % (tts_path, tts_msg, fname))