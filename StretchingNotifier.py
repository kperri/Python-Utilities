import os
import sys
import requests
import random
import json
import tkinter as tk
from PIL import Image, ImageTk


def close(stretches):
    global stretch
    stretches[stretch]["complete"] = True
    with open(r"resources\stretches.json", "w") as f:
        json.dump(stretches, f)
    sys.exit()


def update(ind, image_label, window):
    global playback_delay, frames_total, animations
    if ind >= len(animations):
        ind = 0
    frame = animations[ind]
    ind += 1
    if ind == frames_total:
        ind = 0
    image_label.configure(image=frame)
    window.after(playback_delay, update, ind, image_label, window)


def get_stretches():
    with open(r"resources\stretches.json", "r") as f:
        return json.load(f)


def pick_stretch(stretches, current_stretch=None):
    valid_stretches = [
        stretch for stretch in stretches if not stretches[stretch]["complete"]
    ]
    if current_stretch and current_stretch in valid_stretches:
        valid_stretches.remove(current_stretch)
    if not valid_stretches:
        for stretch in stretches:
            stretches[stretch]["complete"] = False

        valid_stretches = list(stretches.keys())
    stretch = random.choice(valid_stretches)

    return stretch


def pick_new_stretch(stretches, stretch):
    stretch = pick_stretch(stretches, stretch)
    download_stretch_data(stretches[stretch])
    return stretch


def download_stretch_data(stretch):
    if not os.path.exists(stretch["file"]):
        img_data = requests.get(stretch["url"]).content
        with open(stretch["file"], "wb") as handler:
            handler.write(img_data)


def load_gif(file):
    image = Image.open(file)
    frames_total = image.n_frames
    animations = []
    for x in range(frames_total):
        image.seek(x)
        frame = ImageTk.PhotoImage(image.copy())
        animations.append(frame)
    return image, frames_total, animations


def build_ui(stretches, stretch_data):
    global stretch, playback_delay, frames_total, animations

    window = tk.Tk()
    main_frame = tk.Frame(window)
    main_frame.pack(fill="both", expand=1)
    canvas = tk.Canvas(main_frame)
    canvas.pack(side="left", fill="both", expand=1)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.bind_all(
        "<MouseWheel>",
        lambda e: canvas.yview_scroll(-1 * int((e.delta / 120)), "units"),
    )

    second_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=second_frame, anchor="nw")

    header_label = tk.Label(second_frame, text=f"Break Time: {stretch_data['name']}")
    header_label.pack()

    image_label = tk.Label(second_frame)
    image_label.pack()

    description_label = tk.Label(
        second_frame, text=stretch_data["description"], wraplength=250, justify="center"
    )
    description_label.pack()

    def set_mutable_properties(stretch_data):
        header_label["text"] = f"Break Time: {stretch_data['name']}"
        description_label["text"] = stretch_data["description"]

    set_mutable_properties(stretch_data)
    image, frames_total, animations = load_gif(stretch_data["file"])
    window_size = f"{image.width}x{int(image.height*.9)}"
    window.geometry(window_size)

    playback_delay = int(2000 / frames_total)

    button_frame = tk.Frame(second_frame)
    button_frame.pack(side="bottom", fill="both", expand=True)
    done_button = tk.Button(button_frame, text="Done", width=10, height=2, bg="gray")
    done_button.bind(
        "<Button-1>", lambda e, stretches=stretches: close(stretches),
    )
    done_button.pack(in_=button_frame, side="left", padx=(0, 5))

    def update_ui(stretches):
        global stretch, playback_delay, frames_total, animations
        stretch = pick_new_stretch(stretches, stretch)
        stretch_data = stretches[stretch]
        set_mutable_properties(stretch_data)
        image, frames_total, animations = load_gif(stretch_data["file"])
        playback_delay = int(2000 / frames_total)
        window_size = f"{image.width}x{int(image.height*.9)}"
        window.geometry(window_size)

    skip_button = tk.Button(button_frame, text="Skip", width=10, height=2, bg="gray")
    skip_button.bind(
        "<Button-1>", lambda e, stretches=stretches: update_ui(stretches),
    )
    skip_button.pack(in_=button_frame, side="left", padx=(0, 5))

    cancel_button = tk.Button(
        button_frame, text="Cancel", width=10, height=2, bg="gray"
    )
    cancel_button.bind("<Button-1>", lambda e: sys.exit(0))
    cancel_button.pack(in_=button_frame, side="left")

    window.after(0, update, 0, image_label, window)
    window.mainloop()


global stretch

stretches = get_stretches()
stretch = pick_stretch(stretches)
stretch_data = stretches[stretch]
download_stretch_data(stretch_data)
build_ui(stretches, stretch_data)
