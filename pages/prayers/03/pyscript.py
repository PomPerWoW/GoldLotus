
import js
from pyodide.ffi import create_proxy

document = js.document

TIMESTAMP = [0.01, 4.4, 10.7, 16.8, 35.8, 44.6, 51.5, 66.6, 77]

def play_audio_at_time(time):
    audio = document.getElementById("myAudio")
    audio.currentTime = time
    audio.play()

def play1(_):
    play_audio_at_time(TIMESTAMP[0])

def play2(_):
    play_audio_at_time(TIMESTAMP[1])

def play3(_):
    play_audio_at_time(TIMESTAMP[2])
    
def play4(_):
    play_audio_at_time(TIMESTAMP[3])
    
def play5(_):
    play_audio_at_time(TIMESTAMP[4])
    
def play6(_):
    play_audio_at_time(TIMESTAMP[5])
    
def play7(_):
    play_audio_at_time(TIMESTAMP[6])
    
def play8(_):
    play_audio_at_time(TIMESTAMP[7])
    
def play9(_):
    play_audio_at_time(TIMESTAMP[8])
    
line1 = document.getElementById("line1")
line1.addEventListener("click", create_proxy(play1))

line2 = document.getElementById("line2")
line2.addEventListener("click", create_proxy(play2))

line3 = document.getElementById("line3")
line3.addEventListener("click", create_proxy(play3))

line4 = document.getElementById("line4")
line4.addEventListener("click", create_proxy(play4))

line5 = document.getElementById("line5")
line5.addEventListener("click", create_proxy(play5))

line6 = document.getElementById("line6")
line6.addEventListener("click", create_proxy(play6))

line7 = document.getElementById("line7")
line7.addEventListener("click", create_proxy(play7))

line8 = document.getElementById("line8")
line8.addEventListener("click", create_proxy(play8))

line9 = document.getElementById("line9")
line9.addEventListener("click", create_proxy(play9))

def track_timestamp():
    audio_position = document.getElementById("myAudio").currentTime
    text_elements = {
        "line1": TIMESTAMP[0], 
        "line2": TIMESTAMP[1], 
        "line3": TIMESTAMP[2],
        "line4": TIMESTAMP[3],  
        "line5": TIMESTAMP[4],
        "line6": TIMESTAMP[5], 
        "line7": TIMESTAMP[6],
        "line8": TIMESTAMP[7],  
        "line9": TIMESTAMP[8],
    }

    for element_id, end_time in text_elements.items():
        if audio_position > end_time:
            element = document.getElementById(element_id)
            element.style.color = "red"
        else:
            element = document.getElementById(element_id)
            element.style.color = "black"
    
js.setInterval(create_proxy(track_timestamp), 500)