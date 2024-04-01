
import js
from pyodide.ffi import create_proxy

document = js.document

def play_audio_at_time(time):
    audio = document.getElementById("myAudio")
    audio.currentTime = time
    audio.play()

def play1(_):
    play_audio_at_time(0)

def play2(_):
    play_audio_at_time(4.2)

def play3(_):
    play_audio_at_time(7.5)
    
def play4(_):
    play_audio_at_time(11.6)
    
line1 = document.getElementById("line1")
line1.addEventListener("click", create_proxy(play1))

line2 = document.getElementById("line2")
line2.addEventListener("click", create_proxy(play2))

line3 = document.getElementById("line3")
line3.addEventListener("click", create_proxy(play3))

line4 = document.getElementById("line4")
line4.addEventListener("click", create_proxy(play4))

def track_timestamp():
    audio_position = document.getElementById("myAudio").currentTime
    text_elements = {
        "line1": 0.01, 
        "line2": 4.2, 
        "line3": 7.5,
        "line4": 11.6,  
    }

    for element_id, end_time in text_elements.items():
        if audio_position > end_time:
            element = document.getElementById(element_id)
            element.style.color = "red"
        else:
            element = document.getElementById(element_id)
            element.style.color = "black"
    
js.setInterval(create_proxy(track_timestamp), 500)