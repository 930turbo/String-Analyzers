"""Tk desktop interface. All processing stays on this computer."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .core import analyze, transform, export_report
from .cli import read_text

BG, PANEL, FIELD, TEXT, MUTED, ACCENT = "#10131b", "#191e2b", "#121722", "#edf1fa", "#97a4bd", "#a995ff"
SAMPLE = """Good tools make room for good ideas.

String Analyzer turns a wall of text into a clear picture. Explore words, discover repeated phrases, and clean up a draft without sending anything to the cloud.

Fast. Focused. Offline. A small workspace for your next great idea."""
OPERATIONS = ["Lowercase", "Uppercase", "Title case", "Trim lines", "Collapse spaces", "Remove blank lines", "Deduplicate lines", "Sort lines", "Normalize Unicode"]


class App:
    def __init__(self, root):
        self.root = root
        root.title("String Analyzer")
        root.geometry("1180x800")
        root.minsize(980, 700)
        root.configure(bg=BG)
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.generation = 0
        self.pending = None
        self.result = analyze("")
        self.closed = False
        self.style()
        self.build()
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Control-o>", lambda e: self.open_file())
        root.bind("<Control-s>", lambda e: self.export())
        root.bind("<Control-Return>", lambda e: self.schedule(0))
        self.schedule(0)

    def style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(".", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("TFrame", background=BG)
        s.configure("TButton", background=PANEL, foreground=TEXT, padding=(12, 8), borderwidth=0)
        s.map("TButton", background=[("active", "#30394f")])
        s.configure("Accent.TButton", background=ACCENT, foreground=BG)
        s.map("Accent.TButton", background=[("active", "#c5b8ff")])
        s.configure("TCheckbutton", background=BG, foreground=MUTED)
        s.map("TCheckbutton", background=[("active", BG)])
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(16, 10))
        s.map("TNotebook.Tab", background=[("selected", "#30304b")], foreground=[("selected", TEXT)])
        s.configure("Treeview", background=FIELD, fieldbackground=FIELD, foreground=TEXT, rowheight=29, borderwidth=0)
        s.configure("Treeview.Heading", background=PANEL, foreground=MUTED, padding=8)
        s.map("Treeview", background=[("selected", "#49406b")])
        s.configure("TCombobox", fieldbackground=FIELD, foreground=TEXT, arrowcolor=TEXT)
        s.map("TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", TEXT)], selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", TEXT)])

    def label(self, parent, text, size=10, color=TEXT, bg=BG, **kw):
        return tk.Label(parent, text=text, bg=bg, fg=color, font=("Segoe UI", size), **kw)

    def build(self):
        shell = tk.Frame(self.root, bg=BG, padx=26, pady=22)
        shell.pack(fill="both", expand=True)
        header = tk.Frame(shell, bg=BG)
        header.pack(fill="x")
        self.label(header, "Aa", 27, ACCENT).pack(side="left", padx=(0, 16))
        title = tk.Frame(header, bg=BG)
        title.pack(side="left")
        self.label(title, "String Analyzer", 23).pack(anchor="w")
        self.label(title, "A little clarity for every character.", 10, MUTED).pack(anchor="w")
        ttk.Button(header, text="Export report", style="Accent.TButton", command=self.export).pack(side="right")
        self.label(header, "LOCAL / OFFLINE", 9, "#8bd8ba").pack(side="right", padx=20)
        cards = tk.Frame(shell, bg=BG)
        cards.pack(fill="x", pady=(24, 20))
        self.metrics = {}
        for i, (key, name) in enumerate([("words", "WORDS"), ("characters", "CHARACTERS"), ("unique_words", "UNIQUE WORDS"), ("reading_seconds", "READ TIME")]):
            cards.columnconfigure(i, weight=1)
            card = tk.Frame(cards, bg=PANEL, padx=18, pady=12)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))
            self.label(card, name, 9, MUTED, PANEL).pack(anchor="w")
            value = self.label(card, "0", 25, TEXT, PANEL)
            value.pack(anchor="w")
            self.metrics[key] = value
        self.status = self.label(shell, "Ready · paste text or open a UTF-8 file", 9, MUTED)
        self.status.pack(side="bottom", anchor="w", pady=(16, 0))
        panes = tk.PanedWindow(shell, bg=BG, sashwidth=14, bd=0, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left, right = tk.Frame(panes, bg=BG), tk.Frame(panes, bg=BG)
        panes.add(left, minsize=370, stretch="always")
        panes.add(right, minsize=480, stretch="always")
        bar = tk.Frame(left, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.label(bar, "YOUR TEXT", 10, MUTED).pack(side="left")
        ttk.Button(bar, text="Open file", command=self.open_file).pack(side="right")
        ttk.Button(bar, text="Sample", command=lambda: self.set_text(SAMPLE)).pack(side="right", padx=6)
        editor_frame = tk.Frame(left, bg=FIELD)
        self.editor = tk.Text(editor_frame, bg=FIELD, fg=TEXT, insertbackground=ACCENT, selectbackground="#49406b", relief="flat", wrap="word", undo=True, padx=18, pady=18, font=("Segoe UI", 12), spacing1=2, spacing3=5, width=40, height=10)
        scroll = ttk.Scrollbar(editor_frame, command=self.editor.yview)
        scroll.pack(side="right", fill="y")
        self.editor.configure(yscrollcommand=scroll.set)
        self.editor.pack(fill="both", expand=True)
        self.editor.bind("<<Modified>>", self.modified)
        self.editor.tag_configure("match", background="#574679", foreground="white")
        options = tk.Frame(left, bg=BG)
        options.pack(side="bottom", fill="x", pady=12)
        self.stopwords, self.case = tk.BooleanVar(), tk.BooleanVar()
        ttk.Checkbutton(options, text="Hide English stop words", variable=self.stopwords, command=self.schedule).pack(side="left")
        ttk.Checkbutton(options, text="Match case", variable=self.case, command=self.schedule).pack(side="right")
        tools = tk.Frame(left, bg=BG)
        tools.pack(side="bottom", fill="x", before=options)
        self.operation = ttk.Combobox(tools, values=OPERATIONS, state="readonly", width=21)
        self.operation.current(0)
        self.operation.pack(side="left", fill="x", expand=True)
        ttk.Button(tools, text="Apply", command=self.apply).pack(side="left", padx=6)
        ttk.Button(tools, text="Undo", command=self.undo).pack(side="left")
        editor_frame.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)
        overview, frequency, cloud, search = [tk.Frame(self.notebook, bg=BG, padx=14, pady=14) for _ in range(4)]
        for frame, name in zip([overview, frequency, cloud, search], ["Overview", "Frequencies", "Word cloud", "Find"]): self.notebook.add(frame, text=name)
        self.overview = tk.Text(overview, bg=FIELD, fg=TEXT, relief="flat", padx=18, pady=16, font=("Segoe UI", 11), spacing3=9, wrap="word", width=40, height=10, state="disabled")
        overview_scroll = ttk.Scrollbar(overview, command=self.overview.yview)
        overview_scroll.pack(side="right", fill="y")
        self.overview.configure(yscrollcommand=overview_scroll.set)
        self.overview.pack(fill="both", expand=True)
        self.kind = ttk.Combobox(frequency, values=["Words", "Letters", "Punctuation", "Bigrams", "Trigrams"], state="readonly")
        self.kind.current(0)
        self.kind.pack(fill="x", pady=(0, 10))
        self.kind.bind("<<ComboboxSelected>>", lambda e: self.fill_table())
        self.table = ttk.Treeview(frequency, columns=("term", "count", "share"), show="headings", selectmode="browse", height=8)
        for col, title, width in [("term", "Term", 250), ("count", "Count", 75), ("share", "Share", 75)]:
            self.table.heading(col, text=title)
            self.table.column(col, width=width, minwidth=50, anchor="w" if col == "term" else "e")
        table_scroll = ttk.Scrollbar(frequency, command=self.table.yview)
        table_scroll.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=table_scroll.set)
        self.table.pack(fill="both", expand=True)
        self.label(frequency, "Top 500 terms shown · exports include every term", 9, MUTED).pack(anchor="w", pady=(8, 0))
        self.cloud = tk.Canvas(cloud, bg=FIELD, highlightthickness=0)
        self.cloud.pack(fill="both", expand=True)
        self.cloud.bind("<Configure>", lambda e: self.draw_cloud())
        self.label(cloud, "Top 40 words · sized by relative frequency", 9, MUTED).pack(anchor="w", pady=(8, 0))
        self.label(search, "Find literal text", 12).pack(anchor="w")
        self.query = tk.Entry(search, bg=FIELD, fg=TEXT, insertbackground=ACCENT, relief="flat", font=("Segoe UI", 12))
        self.query.pack(fill="x", ipady=10, pady=12)
        self.query.bind("<Return>", lambda e: self.find())
        ttk.Button(search, text="Highlight matches", command=self.find).pack(anchor="w")
        self.found = self.label(search, "Search is case-insensitive. Up to 5,000 matches highlighted.", 10, MUTED, wraplength=400, justify="left")
        self.found.pack(anchor="w", pady=18)


    def text(self): return self.editor.get("1.0", "end-1c")

    def set_text(self, text):
        self.editor.edit_separator()
        self.editor.configure(autoseparators=False)
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        self.editor.configure(autoseparators=True)
        self.editor.edit_separator()
        self.schedule()

    def modified(self, event=None):
        if self.editor.edit_modified():
            self.editor.edit_modified(False)
            self.editor.tag_remove("match", "1.0", "end")
            self.schedule()

    def schedule(self, delay=400):
        self.generation += 1
        if self.pending: self.root.after_cancel(self.pending)
        self.pending = self.root.after(delay, self.submit)

    def submit(self):
        self.pending = None
        if self.future and not self.future.done():
            self.pending = self.root.after(100, self.submit)
            return
        generation = self.generation
        self.status.configure(text="Analyzing locally…")
        self.future = self.pool.submit(analyze, self.text(), exclude_stopwords=self.stopwords.get(), case_sensitive=self.case.get())
        future = self.future
        self.root.after(50, lambda: self.poll(generation, future))

    def poll(self, generation, future):
        if not future.done():
            self.root.after(50, lambda: self.poll(generation, future))
            return
        if generation != self.generation: return
        try:
            self.result = future.result()
            self.render()
            self.status.configure(text="Up to date · offline analysis · Ctrl+O open / Ctrl+S export")
        except Exception as error:
            self.status.configure(text=str(error))

    def render(self):
        r = self.result
        for key, label in self.metrics.items(): label.configure(text=f"{r[key]:,}" + (" sec" if key == "reading_seconds" else ""))
        sentiment = r["sentiment"]
        lines = ["THE BIG PICTURE", f"{r['sentences']:,} sentences    ·    {r['paragraphs']:,} paragraphs    ·    {r['lines']:,} lines", f"{r['characters_no_whitespace']:,} characters without whitespace", f"{r['utf8_bytes']:,} UTF-8 bytes    ·    {r['digits']:,} digits", "", "VOCABULARY", f"{r['lexical_diversity']}% unique / analyzed words", f"{r['average_word_length']} characters per word on average", f"{r['analyzed_words']:,} words after frequency filters", f"{r['entropy_bits']} bits / character (Shannon entropy)", "", "TONE SNAPSHOT", f"{sentiment['label']} · {sentiment['positive_hits']} positive / {sentiment['negative_hits']} negative hits", "Simple English word-list heuristic. Does not interpret negation, sarcasm, or context."]
        self.overview.configure(state="normal")
        self.overview.delete("1.0", "end")
        self.overview.insert("1.0", "\n".join(lines))
        self.overview.configure(state="disabled")
        self.fill_table()
        self.draw_cloud()

    def fill_table(self):
        key = {"Words": "word_frequency", "Letters": "letter_frequency", "Punctuation": "punctuation_frequency", "Bigrams": "bigrams", "Trigrams": "trigrams"}[self.kind.get()]
        self.table.delete(*self.table.get_children())
        entries = self.result[key]
        total = sum(entries.values())
        for term, count in list(entries.items())[:500]: self.table.insert("", "end", values=(term, count, f"{count / max(1, total):.1%}"))

    def draw_cloud(self):
        self.cloud.delete("all")
        entries = list(self.result["word_frequency"].items())[:40]
        width, height = self.cloud.winfo_width(), self.cloud.winfo_height()
        if not entries:
            self.cloud.create_text(width/2, height/2, text="Your words will take shape here.", fill=MUTED, font=("Segoe UI", 12))
            return
        x, y, row_height = 16, 18, 0
        for i, (word, count) in enumerate(entries):
            size = 11 + int(20 * count / entries[0][1])
            display = word if len(word) <= 24 else word[:21] + "…"
            item = self.cloud.create_text(x, y, text=display, anchor="nw", fill=[ACCENT, "#8bd8ba", "#eac495", "#b7c6e6"][i % 4], font=("Segoe UI", size, "bold"))
            box = self.cloud.bbox(item)
            w, h = box[2]-box[0], box[3]-box[1]
            if x + w > width-16 and x > 16:
                x, y, row_height = 16, y + row_height + 12, 0
                self.cloud.coords(item, x, y)
            if y + h > height-12:
                self.cloud.delete(item)
                break
            x += w + 18
            row_height = max(row_height, h)

    def find(self):
        query = self.query.get()
        self.editor.tag_remove("match", "1.0", "end")
        if not query:
            self.found.configure(text="Enter text to search.")
            return
        start, count, first = "1.0", 0, None
        length = tk.IntVar()
        while count < 5000:
            index = self.editor.search(query, start, stopindex="end", nocase=True, count=length)
            if not index: break
            end = f"{index}+{length.get()}c"
            self.editor.tag_add("match", index, end)
            first = first or index
            start, count = end, count + 1
        if first: self.editor.see(first)
        self.found.configure(text=f"{count:,}{'+' if count == 5000 else ''} matches highlighted.")

    def apply(self):
        self.editor.edit_separator()
        self.set_text(transform(self.text(), self.operation.get()))

    def undo(self):
        try: self.editor.edit_undo()
        except tk.TclError: pass

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.md *.csv *.json *.log"), ("All files", "*.*")])
        if path:
            try: self.set_text(read_text(path))
            except (OSError, UnicodeError, ValueError) as error: messagebox.showerror("Cannot open file", str(error))

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="analysis.json", filetypes=[("JSON report", "*.json"), ("CSV report", "*.csv"), ("Text report", "*.txt")])
        if not path: return
        try:
            # Snapshot the editor so exports never silently use stale results.
            result = analyze(self.text(), exclude_stopwords=self.stopwords.get(), case_sensitive=self.case.get())
            kind = Path(path).suffix.lower().lstrip(".")
            Path(path).write_text(export_report(result, kind), encoding="utf-8")
            self.status.configure(text=f"Saved {Path(path).name}")
        except (OSError, UnicodeError, ValueError) as error: messagebox.showerror("Cannot export", str(error))

    def close(self):
        self.closed = True
        for callback in self.root.tk.call("after", "info"):
            self.root.after_cancel(callback)
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def launch():
    root = tk.Tk()
    App(root)
    root.mainloop()
