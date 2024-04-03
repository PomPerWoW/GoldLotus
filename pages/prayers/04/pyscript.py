
import js
from pyodide.ffi import create_proxy

document = js.document

TIMESTAMP = [0.01, 7.2]

def play_audio_at_time(time):
    audio = document.getElementById("myAudio")
    audio.currentTime = time
    audio.play()

def play1(_):
    play_audio_at_time(TIMESTAMP[0])

def play2(_):
    play_audio_at_time(TIMESTAMP[1])
    
line1 = document.getElementById("line1")
line1.addEventListener("click", create_proxy(play1))

line2 = document.getElementById("line2")
line2.addEventListener("click", create_proxy(play2))


def track_timestamp():
    audio_position = document.getElementById("myAudio").currentTime
    text_elements = {
        "line1": TIMESTAMP[0], 
        "line2": TIMESTAMP[1],
    }

    for element_id, end_time in text_elements.items():
        if audio_position > end_time:
            element = document.getElementById(element_id)
            element.style.color = "red"
        else:
            element = document.getElementById(element_id)
            element.style.color = "#4D4637"
    
js.setInterval(create_proxy(track_timestamp), 500)