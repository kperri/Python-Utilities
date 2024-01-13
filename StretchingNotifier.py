import os
import sys
import requests
import random
import json
import time
import playsound
import threading
import tkinter as tk
from PIL import Image, ImageTk

TASKBAR_SIZE = 72
GIF_SPEED_DIVIDEND = 2000
RESOURCE_FOLDER = "resources"
ALARM_SOUND = f"{RESOURCE_FOLDER}\\alarm.mp3"
JSON_FILE = f"{RESOURCE_FOLDER}\\exercises.json"


def countdown(timers):
    global countdown_labels, stop_thread
    stop_thread = False
    i = 0
    for timer in timers:
        total_seconds = timer
        while total_seconds > 0:
            time.sleep(1)
            total_seconds -= 1
            countdown_labels[i]["text"] = f"Timer: {total_seconds}"
            if stop_thread:
                break

        if stop_thread:
            break
        threading.Thread(
            target=playsound.playsound, args=(ALARM_SOUND,), daemon=True
        ).start()
        i += 1


def close():
    global stretch, stretches
    stretches[stretch]["complete"] = True
    with open(JSON_FILE, "w") as f:
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
    with open(JSON_FILE, "r") as f:
        return json.load(f)


def reset_stretches():
    global stretches
    for stretch in stretches:
        stretches[stretch]["complete"] = False
    with open(JSON_FILE, "w") as f:
        json.dump(stretches, f)


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
        if stretch["url"]:
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


def build_ui(stretch_data):
    global stretch, stretches, playback_delay, frames_total, animations, countdown_labels, start_button
    countdown_labels = []
    start_button = None

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
    window_size = f"{image.width}x{window.winfo_screenheight() - TASKBAR_SIZE}+0+0"
    window.geometry(window_size)

    playback_delay = int(GIF_SPEED_DIVIDEND / frames_total)

    def update_ui(new_stretch=None):
        global stretch, stretches, playback_delay, frames_total, animations, countdown_labels, stop_thread
        if new_stretch:
            stretch = new_stretch
        else:
            stretch = pick_new_stretch(stretches, stretch)
        stretch_data = stretches[stretch]
        set_mutable_properties(stretch_data)
        image, frames_total, animations = load_gif(stretch_data["file"])
        timer_thread = set_timers(timer_frame, stretch_data, button_frame)
        playback_delay = int(GIF_SPEED_DIVIDEND / frames_total)
        current_stretch.set(stretch_data["name"])
        window_size = f"{image.width}x{window.winfo_screenheight() - TASKBAR_SIZE}+0+0"
        window.geometry(window_size)
        if timer_thread and timer_thread.is_alive():
            stop_thread = True

    timer_frame = tk.Frame(second_frame)
    timer_frame.pack()

    def set_timers(timer_frame, stretch_data, button_frame):
        global countdown_labels, start_button
        if countdown_labels:
            for countdown_label in countdown_labels:
                countdown_label.destroy()

        if "timer" in stretch_data and stretch_data["timer"]:
            countdown_labels = []
            for timer in stretch_data["timer"]:
                countdown_label = tk.Label(
                    timer_frame, text=f"Timer: {timer}", justify="center"
                )
                countdown_label.pack()
                countdown_labels.append(countdown_label)

            timer_thread = threading.Thread(
                target=countdown, args=(stretch_data["timer"],), daemon=True,
            )

            if start_button:
                start_button.destroy()

            start_button = tk.Button(
                button_frame, text="Start", width=10, height=2, bg="gray"
            )
            start_button.bind(
                "<Button-1>", lambda e: timer_thread.start(),
            )
            start_button.pack(
                in_=button_frame, side="left", padx=(0, 5), before=done_button
            )

            return timer_thread
        elif start_button:
            start_button.destroy()
            start_button = None

    current_stretch = tk.StringVar(second_frame)
    current_stretch.set(stretches[stretch]["name"])
    stretch_name_dict = {}
    for s in stretches:
        stretch_name_dict[stretches[s]["name"]] = s
    stretch_dropdown = tk.OptionMenu(
        second_frame, current_stretch, *list(stretch_name_dict.keys())
    )
    current_stretch.trace_add(
        "write",
        lambda var, index, mode: update_ui(stretch_name_dict[current_stretch.get()]),
    )
    stretch_dropdown.pack()

    button_frame = tk.Frame(second_frame)
    button_frame.pack(side="bottom", fill="both", expand=True)

    done_button = tk.Button(button_frame, text="Done", width=10, height=2, bg="gray")
    done_button.bind(
        "<Button-1>", lambda e: close(),
    )
    done_button.pack(in_=button_frame, side="left", padx=(0, 5))

    skip_button = tk.Button(button_frame, text="Skip", width=10, height=2, bg="gray")
    skip_button.bind(
        "<Button-1>", lambda e: update_ui(),
    )
    skip_button.pack(in_=button_frame, side="left", padx=(0, 5))

    reset_button = tk.Button(button_frame, text="Reset", width=10, height=2, bg="gray")
    reset_button.bind(
        "<Button-1>", lambda e: reset_stretches(),
    )
    reset_button.pack(in_=button_frame, side="left", padx=(0, 5))

    cancel_button = tk.Button(
        button_frame, text="Cancel", width=10, height=2, bg="gray"
    )
    cancel_button.bind("<Button-1>", lambda e: sys.exit(0))
    cancel_button.pack(in_=button_frame, side="left")

    timer_thread = set_timers(timer_frame, stretch_data, button_frame)

    window.bind(
        "<Key>",
        lambda e: update_ui()
        if e.char == "s"
        else (
            close()
            if e.char == "d"
            else (
                sys.exit(0)
                if e.char == "c"
                else (timer_thread.start() if timer_thread and e.char == "w" else None)
            )
        ),
    )
    window.after(0, update, 0, image_label, window)
    window.mainloop()


global stretch, stretches, stop_thread

stretches = get_stretches()
stretch = pick_stretch(stretches)
stretch_data = stretches[stretch]
download_stretch_data(stretch_data)
build_ui(stretch_data)
