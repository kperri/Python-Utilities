import os
import sys
import requests
import random
import json
import tkinter as tk
from PIL import Image, ImageTk


def close(event):
    stretch["complete"] = True
    with open(r"resources\stretches.json", "w") as f:
        json.dump(stretches, f)
    sys.exit()


def skip(event):
    sys.exit()


with open(r"resources\stretches.json", "r") as f:
    stretches = json.load(f)
    valid_stretches = [
        stretch for stretch in stretches if not stretches[stretch]["complete"]
    ]
    if not valid_stretches:
        for stretch in stretches:
            stretches[stretch]["complete"] = False

        valid_stretches = list(stretches.keys())
    stretch = random.choice(valid_stretches)
    stretch = stretches[stretch]

if not os.path.exists(stretch["file"]):
    img_data = requests.get(stretch["url"]).content
    with open(stretch["file"], "wb") as handler:
        handler.write(img_data)

window = tk.Tk()
label = tk.Label(text=f"Break Time: {stretch['name']}")
label.pack()

image = Image.open(stretch["file"])
frames_total = image.n_frames

animation = []


def loag_gif():
    for x in range(frames_total):
        frame = ImageTk.PhotoImage(image.copy())
        animation.append(frame)
        image.seek(x)


playback_delay = 500


def update(ind):
    frame = animation[ind]
    ind += 1
    if ind == frames_total:
        ind = 0
    image_label.configure(image=frame)
    window.after(playback_delay, update, ind)


image_label = tk.Label(window)
image_label.pack()
loag_gif()

label = tk.Label(text=stretch["description"], wraplength=250, justify="center")
label.pack()

button = tk.Button(text="Done", width=10, height=2, bg="gray")
button.bind("<Button-1>", close)
button.pack()

button = tk.Button(text="Skip", width=10, height=2, bg="gray")
button.bind("<Button-1>", skip)
button.pack()

window.after(0, update, 0)
window.mainloop()
