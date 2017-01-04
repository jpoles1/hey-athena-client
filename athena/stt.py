"""
Basic Speech-To-Text tools are stored here
"""

import pyaudio
import speech_recognition
#import snowboydecoder
#wake_detector = snowboydecoder.HotwordDetector("snowboy.pmdl", sensitivity=0.5)

from athena import settings, tts, log
from sophie_sphinx import SpeechDetector

from sphinxbase.sphinxbase import Config, Config_swigregister
from pocketsphinx.pocketsphinx import Decoder


def init():
    # Create a decoder with certain model
    config = Decoder.default_config()
    config.set_string('-logfn', settings.POCKETSPHINX_LOG)
    config.set_string('-hmm',   settings.ACOUSTIC_MODEL)
    config.set_string('-lm',    settings.LANGUAGE_MODEL)
    #config.set_string('-dict',  settings.POCKET_DICT)
    config.set_string('-dict',  settings.POCKET_DICT)
    # Decode streaming data
    global wake_decoder, decoder, p, threshold, sphinx_speech
    decoder = Decoder(config)
    wake_decoder = Decoder(config)
    wake_decoder.set_keyphrase('wakeup', settings.WAKE_UP_WORD)
    wake_decoder.set_search('wakeup')
    p = pyaudio.PyAudio()

    sphinx_speech = SpeechDetector(decoder)
    # r.recognize_google(settings.LANG_4CODE)


def listen_keyword():
    """ Passively listens for the WAKE_UP_WORD string """
    with tts.ignore_stderr():
        global wake_decoder, p
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=1024)
        stream.start_stream()
        p.get_default_input_device_info()

    log.info("Waiting to be woken up... ")
    wake_decoder.start_utt()
    while True:
        buf = stream.read(1024)
        wake_decoder.process_raw(buf, False, False)
        if wake_decoder.hyp() and wake_decoder.hyp().hypstr == settings.WAKE_UP_WORD:
            wake_decoder.end_utt()
            break

def active_listen():
    """
    Actively listens for speech to translate into text
    :return: speech input as a text string
    """
    with tts.ignore_stderr():
        global decoder, p
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=1024)
        stream.start_stream()
        p.get_default_input_device_info()
        tts.play_mp3("double-beep.mp3")
    log.info("Listening for command... ")
    decoder.start_utt()
    oldstr = ""
    i = 0;
    while i<10:
        buf = stream.read(1024)
        decoder.process_raw(buf, False, False)
        if decoder.hyp():
            curstr = decoder.hyp().hypstr;
            print("Heard (i=", i, "): ", curstr)
            if not buf:
                break
            if curstr == oldstr:
                i+=1;
            else:
                i=0
            oldstr = curstr
            i+=1;
    decoder.end_utt()
    words = []
    [words.append(seg.word) for seg in decoder.seg()]
    print(words)
    print(oldstr)
    return
