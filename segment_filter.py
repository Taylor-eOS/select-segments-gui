import tkinter as tk
import tkinter.font as tkfont

INPUT_FILE = "input.txt"
OUTPUT_FILE = "selected.txt"
BOX_PIXEL_WIDTH = 850
BOX_PIXEL_HEIGHT = 108

def load_segments():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    raw_segments = content.split("\n\n")
    segments = [s for s in raw_segments if s.strip() != ""]
    return segments

def save_selected(segments, selected_flags):
    chosen = [segments[i] for i in range(len(segments)) if selected_flags[i]]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(chosen))

def build_gui(segments):
    selected_flags = [False] * len(segments)
    root = tk.Tk()
    root.title("Segment Filter")
    root.geometry("900x700")
    display_font = tkfont.Font(family="Courier New", size=10)
    top_frame = tk.Frame(root)
    top_frame.pack(side="top", fill="x")
    status_label = tk.Label(top_frame, text="0 of {} selected".format(len(segments)), anchor="w")
    status_label.pack(side="left", padx=10, pady=5)
    save_button = tk.Button(top_frame, text="Save selected to selected.txt")
    save_button.pack(side="right", padx=10, pady=5)
    canvas_frame = tk.Frame(root)
    canvas_frame.pack(side="top", fill="both", expand=True)
    canvas = tk.Canvas(canvas_frame, highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner_frame = tk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def on_inner_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    inner_frame.bind("<Configure>", on_inner_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    def on_mousewheel(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind_all("<Button-4>", on_mousewheel)
    canvas.bind_all("<Button-5>", on_mousewheel)

    def update_status():
        count = sum(1 for f in selected_flags if f)
        status_label.config(text="{} of {} selected".format(count, len(segments)))

    def make_toggle(index, block_frame, clip_frame, text_label):
        def toggle(event=None):
            selected_flags[index] = not selected_flags[index]
            if selected_flags[index]:
                block_frame.config(bg="#cfe8cf")
                clip_frame.config(bg="#cfe8cf")
                text_label.config(bg="#cfe8cf")
            else:
                block_frame.config(bg="#f0f0f0")
                clip_frame.config(bg="#f0f0f0")
                text_label.config(bg="#f0f0f0")
            update_status()
        return toggle
    for index, segment in enumerate(segments):
        block_frame = tk.Frame(inner_frame, bg="#f0f0f0", bd=1, relief="solid")
        block_frame.pack(side="top", fill="x", padx=8, pady=4)
        clip_frame = tk.Frame(block_frame, bg="#f0f0f0", width=BOX_PIXEL_WIDTH, height=BOX_PIXEL_HEIGHT)
        clip_frame.pack(side="top", fill="x", padx=6, pady=6)
        clip_frame.pack_propagate(False)
        text_label = tk.Label(
            clip_frame,
            text=segment,
            bg="#f0f0f0",
            justify="left",
            anchor="nw",
            wraplength=BOX_PIXEL_WIDTH,
            font=display_font,
        )
        text_label.pack(side="top", fill="both", expand=True)
        toggle = make_toggle(index, block_frame, clip_frame, text_label)
        block_frame.bind("<Button-1>", toggle)
        clip_frame.bind("<Button-1>", toggle)
        text_label.bind("<Button-1>", toggle)


    def on_save():
        save_selected(segments, selected_flags)
        status_label.config(text="Saved {} segments to {}".format(sum(selected_flags), OUTPUT_FILE))
    save_button.config(command=on_save)
    root.mainloop()

if __name__ == "__main__":
    segments = load_segments()
    build_gui(segments)
