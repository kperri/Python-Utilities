import os
import sys
import requests
import random
import json
import tkinter as tk


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

frameCnt = stretch["frames"]
frames = [
    tk.PhotoImage(file=stretch["file"], format="gif -index %i" % (i))
    for i in range(frameCnt)
]


def update(ind):

    frame = frames[ind]
    ind += 1
    if ind == frameCnt:
        ind = 0
    image.configure(image=frame)
    window.after(750, update, ind)


image = tk.Label(window)
image.pack()

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
