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
    config.set_string('-dict',  settings.POCKET_DICT)
    # Decode streaming data
    global wake_decoder, decoder, p, threshold, sphinx_speech
    wake_decoder = Decoder(config)
    wake_decoder.set_keyphrase('wakeup', settings.WAKE_UP_WORD)
    wake_decoder.set_search('wakeup')

    #config.set_string('-lm',    "1444.lm")
    #config.set_string('-dict',  "1444.dic")

    decoder = Decoder(config)
    p = pyaudio.PyAudio()

    sphinx_speech = SpeechDetector(decoder)
    threshold = sphinx_speech.setup_mic()
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
    i = 0;
    while True:
        buf = stream.read(1024)
        wake_decoder.process_raw(buf, False, False)
        if wake_decoder.hyp() and wake_decoder.hyp().hypstr == settings.WAKE_UP_WORD:
            wake_decoder.end_utt()
            break
        i+=1;
        if i%600 == 0:
            sphinx_speech.setup_mic()
            log.info("Recalibrated. Waiting to be woken up... ")
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
    return sphinx_speech.run()
