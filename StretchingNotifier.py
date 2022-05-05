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
main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=1)
canvas = tk.Canvas(main_frame)
canvas.pack(side="left", fill="both", expand=1)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * int((event.delta / 120)), "units")


canvas.bind_all("<MouseWheel>", on_mouse_wheel)

second_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=second_frame, anchor="nw")

label = tk.Label(second_frame, text=f"Break Time: {stretch['name']}")
label.pack()


image = Image.open(stretch["file"])
frames_total = image.n_frames

window_size = f"{image.width}x{int(image.height*.75)}"
window.geometry(window_size)

animation = []


def loag_gif():
    for x in range(frames_total):
        image.seek(x)
        frame = ImageTk.PhotoImage(image.copy())
        animation.append(frame)


playback_delay = int(3000 / frames_total)


def update(ind):
    frame = animation[ind]
    ind += 1
    if ind == frames_total:
        ind = 0
    image_label.configure(image=frame)
    window.after(playback_delay, update, ind)


image_label = tk.Label(second_frame)
image_label.pack()
loag_gif()

label = tk.Label(
    second_frame, text=stretch["description"], wraplength=250, justify="center"
)
label.pack()

button = tk.Button(second_frame, text="Done", width=10, height=2, bg="gray")
button.bind("<Button-1>", close)
button.pack()

button = tk.Button(second_frame, text="Skip", width=10, height=2, bg="gray")
button.bind("<Button-1>", lambda e: sys.exit())
button.pack()

window.after(0, update, 0)
window.mainloop()
