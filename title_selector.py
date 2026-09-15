import tkinter as tk
from tkinter import scrolledtext, messagebox

INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
RESULT_FILE = "selected_titles.txt"
MAX_INPUT_CHARS = 1200

def read_segments(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    raw_segments = content.split("\n\n")
    segments = [seg.strip("\n") for seg in raw_segments if seg.strip() != ""]
    return segments

def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def load_data():
    input_segments = read_segments(INPUT_FILE)
    output_segments = read_segments(OUTPUT_FILE)
    if len(input_segments) != len(output_segments):
        raise ValueError(
            "Segment count mismatch: input has %d, output has %d"
            % (len(input_segments), len(output_segments))
        )
    candidates_per_segment = []
    for seg in output_segments:
        lines = [line.strip() for line in seg.split("\n") if line.strip() != ""]
        lines = dedupe_preserve_order(lines)
        candidates_per_segment.append(lines)
    return input_segments, candidates_per_segment

def truncate_for_display(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " […]"

class TitleSelectorApp:
    def __init__(self, root, input_segments, candidates_per_segment):
        self.root = root
        self.input_segments = input_segments
        self.candidates_per_segment = candidates_per_segment
        self.total = len(input_segments)
        self.current_index = 0
        self.selections = [None] * self.total
        self.build_layout()
        self.reset_result_file()
        self.show_segment(0)

    def build_layout(self):
        self.root.title("Title Selector")
        self.root.geometry("1100x700")
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        self.progress_label = tk.Label(top_frame, text="", font=("TkDefaultFont", 11, "bold"))
        self.progress_label.pack(side=tk.LEFT)
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = tk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)
        left_label = tk.Label(left_frame, text="Input segment", font=("TkDefaultFont", 10, "bold"))
        left_label.pack(anchor="w")
        self.input_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=("TkDefaultFont", 11))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.configure(state=tk.DISABLED)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_label = tk.Label(right_frame, text="Candidate titles", font=("TkDefaultFont", 10, "bold"))
        right_label.pack(anchor="w")
        self.options_frame = tk.Frame(right_frame)
        self.options_frame.pack(fill=tk.BOTH, expand=True, anchor="n")
        custom_frame = tk.Frame(right_frame)
        custom_frame.pack(fill=tk.X, pady=(10, 0))
        custom_label = tk.Label(custom_frame, text="Manual entry (Enter confirms):")
        custom_label.pack(anchor="w")
        entry_row = tk.Frame(custom_frame)
        entry_row.pack(fill=tk.X, pady=(2, 0))
        self.custom_entry = tk.Entry(entry_row, font=("TkDefaultFont", 11))
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.custom_entry.bind("<Return>", self.on_custom_entry_confirm)
        self.custom_ok_button = tk.Button(entry_row, text="OK", width=6, command=self.on_custom_entry_confirm)
        self.custom_ok_button.pack(side=tk.LEFT, padx=(6, 0))
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        self.status_label = tk.Label(bottom_frame, text="", fg="gray")
        self.status_label.pack(side=tk.RIGHT, padx=(0, 20))

    def reset_result_file(self):
        open(RESULT_FILE, "w", encoding="utf-8").close()

    def clear_option_widgets(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def show_segment(self, index):
        self.current_index = index
        input_text_full = self.input_segments[index]
        display_text = truncate_for_display(input_text_full, MAX_INPUT_CHARS)
        self.input_text.configure(state=tk.NORMAL)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, display_text)
        self.input_text.configure(state=tk.DISABLED)
        self.clear_option_widgets()
        self.custom_entry.delete(0, tk.END)
        candidates = self.candidates_per_segment[index]
        for candidate in candidates:
            row = tk.Button(
                self.options_frame,
                text=candidate,
                wraplength=650,
                justify=tk.LEFT,
                anchor="w",
                font=("TkDefaultFont", 11),
                relief=tk.FLAT,
                command=lambda c=candidate: self.select_candidate(c),
            )
            row.pack(fill=tk.X, anchor="w", pady=3)
        self.progress_label.config(text="Segment %d of %d" % (index + 1, self.total))
        self.update_status()

    def update_status(self):
        done_count = sum(1 for s in self.selections if s is not None)
        self.status_label.config(text="Selected: %d / %d" % (done_count, self.total))

    def on_custom_entry_confirm(self, event=None):
        value = self.custom_entry.get().strip()
        if value == "":
            return
        self.select_candidate(value)

    def select_candidate(self, value):
        self.selections[self.current_index] = value
        append_result_line(value)
        self.update_status()
        self.advance()

    def advance(self):
        if self.current_index + 1 < self.total:
            self.show_segment(self.current_index + 1)
        else:
            messagebox.showinfo("Done", "All segments done. Results saved to %s" % RESULT_FILE)

def append_result_line(text):
    with open(RESULT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def main():
    input_segments, candidates_per_segment = load_data()
    root = tk.Tk()
    TitleSelectorApp(root, input_segments, candidates_per_segment)
    root.mainloop()

if __name__ == "__main__":
    main()
