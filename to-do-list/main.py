# TaskFlow – Python To-Do List Application
#Below is the complete, ready-to-run project.
## Project Structure
"""
TaskFlow
├── main.py
├── tasks.json

TaskFlow - A modern desktop To-Do List application.
Built with:
- Python 3
- Tkinter / ttk
- JSON for persistent storage
"""

import json
import tkinter as tk
import uuid
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_FILE = Path(__file__).resolve().parent / "tasks.json"

FONT_FAMILY = "Segoe UI"

COLORS = {
    "bg": "#171721",
    "surface": "#23232F",
    "card": "#262635",
    "input": "#1B1B26",
    "border": "#343445",
    "accent": "#7C6FF0",
    "accent_hover": "#9588FF",
    "success": "#3DD68C",
    "danger": "#FF6B6B",
    "warning": "#FFB84D",
    "text": "#F5F5FA",
    "text_secondary": "#A2A2B5",
    "text_muted": "#77778C",
}

PRIORITY_COLORS = {
    "Low": "#4DA3FF",
    "Medium": "#FFB84D",
    "High": "#FF6B6B",
}


# ---------------------------------------------------------------------------
# Data Layer
# ---------------------------------------------------------------------------

class TaskManager:
    """Handles loading, saving and modifying tasks stored in a JSON file."""

    def __init__(self, filepath=DATA_FILE):
        self.filepath = Path(filepath)
        self.tasks = []
        self.load_had_error = False
        self.load_tasks()

    # -- Persistence -------------------------------------------------------

    def load_tasks(self):
        """Load tasks from JSON, creating / repairing the file if needed."""
        if not self.filepath.exists():
            self.tasks = []
            self.save_tasks()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("tasks.json must contain a list of tasks.")

            cleaned_tasks = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                title = str(item.get("title", "")).strip()
                if not title:
                    continue

                priority = item.get("priority", "Medium")
                if priority not in PRIORITY_COLORS:
                    priority = "Medium"

                cleaned_tasks.append({
                    "id": str(item.get("id") or uuid.uuid4().hex),
                    "title": title,
                    "description": str(item.get("description", "")).strip(),
                    "priority": priority,
                    "completed": bool(item.get("completed", False)),
                    "created_at": str(item.get("created_at", "")),
                })

            self.tasks = cleaned_tasks

        except (json.JSONDecodeError, ValueError, OSError, UnicodeDecodeError):
            # Corrupted / unreadable file: back it up and start fresh.
            self.load_had_error = True
            self.tasks = []
            try:
                backup_path = self.filepath.parent / (self.filepath.name + ".bak")
                if self.filepath.exists():
                    self.filepath.replace(backup_path)
            except OSError:
                pass
            self.save_tasks()

    def save_tasks(self):
        """Save tasks atomically. Returns True on success, False on failure."""
        try:
            temp_path = self.filepath.with_name(self.filepath.name + ".tmp")
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=2, ensure_ascii=False)
            temp_path.replace(self.filepath)
            return True
        except OSError:
            return False

    # -- CRUD --------------------------------------------------------------

    def add_task(self, title, description, priority):
        task = {
            "id": uuid.uuid4().hex,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().strftime("%b %d, %Y"),
        }
        self.tasks.insert(0, task)  # Newest tasks first
        return task

    def get_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def update_task(self, task_id, title, description, priority, completed):
        task = self.get_task(task_id)
        if task is None:
            return False
        task["title"] = title
        task["description"] = description
        task["priority"] = priority
        task["completed"] = completed
        return True

    def delete_task(self, task_id):
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        return len(self.tasks) != original_count

    def toggle_task(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False
        task["completed"] = not task["completed"]
        return True

    def clear_completed(self):
        completed_count = sum(1 for t in self.tasks if t["completed"])
        self.tasks = [t for t in self.tasks if not t["completed"]]
        return completed_count


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class TaskFlowApp(tk.Tk):
    """Main TaskFlow window."""

    def __init__(self):
        super().__init__()

        self.title("TaskFlow — To-Do List")
        self.geometry("920x680")
        self.minsize(760, 560)
        self.configure(bg=COLORS["bg"])

        self.task_manager = TaskManager(DATA_FILE)
        self.current_filter = "All"

        # Form variables
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Medium")
        self.search_var = tk.StringVar()

        self._setup_styles()
        self._create_widgets()
        self.refresh_task_list()

        if self.task_manager.load_had_error:
            self.after(300, self._show_corrupted_file_warning)

        self.title_entry.focus_set()
        self.bind("<Control-f>", lambda _e: self.search_entry.focus_set())

    # -- Setup -------------------------------------------------------------

    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Dark.TCombobox",
            fieldbackground=COLORS["input"],
            background=COLORS["surface"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            arrowcolor=COLORS["text"],
            padding=6,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", COLORS["input"])],
            foreground=[("readonly", COLORS["text"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["surface"],
            troughcolor=COLORS["bg"],
            bordercolor=COLORS["bg"],
            arrowcolor=COLORS["text_secondary"],
        )

        # Dark dropdown list for comboboxes
        self.option_add("*TCombobox*Listbox.background", COLORS["input"])
        self.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

    def _show_corrupted_file_warning(self):
        messagebox.showwarning(
            "Data File Repaired",
            "Your saved tasks file was corrupted or unreadable, so "
            "TaskFlow started with an empty list.\n\n"
            "The original file was backed up as 'tasks.json.bak'.",
            parent=self,
        )

    def _create_widgets(self):
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=24, pady=20)

        self._create_header(main)
        self._create_stats(main)
        self._create_progress(main)
        self._create_input_card(main)
        self._create_toolbar(main)
        self._create_task_list(main)
        self._create_footer(main)

        # Refresh list automatically while typing in the search box
        self.search_var.trace_add("write", lambda *_args: self.refresh_task_list())

        # Mouse-wheel scrolling (Windows / macOS / Linux)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel_up)
        self.bind_all("<Button-5>", self._on_mousewheel_down)

    # -- Widget sections ---------------------------------------------------

    def _create_header(self, parent):
        header = tk.Frame(parent, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 16))

        left = tk.Frame(header, bg=COLORS["bg"])
        left.pack(side="left")

        tk.Label(
            left, text="✓  TaskFlow",
            font=(FONT_FAMILY, 26, "bold"),
            fg=COLORS["text"], bg=COLORS["bg"],
        ).pack(anchor="w")

        tk.Label(
            left, text="Stay organized, stay productive.",
            font=(FONT_FAMILY, 10),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            header, text=datetime.now().strftime("%A, %B %d, %Y"),
            font=(FONT_FAMILY, 10),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(side="right", anchor="n", pady=8)

    def _create_stat_card(self, parent, column, label_text, accent_color):
        card = tk.Frame(
            parent, bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="nsew",
                  padx=(0, 10) if column < 2 else (0, 0))

        value_label = tk.Label(
            card, text="0",
            font=(FONT_FAMILY, 20, "bold"),
            fg=accent_color, bg=COLORS["surface"],
        )
        value_label.pack(pady=(10, 0))

        tk.Label(
            card, text=label_text,
            font=(FONT_FAMILY, 9, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["surface"],
        ).pack(pady=(0, 10))

        return value_label

    def _create_stats(self, parent):
        stats_frame = tk.Frame(parent, bg=COLORS["bg"])
        stats_frame.pack(fill="x", pady=(0, 12))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        self.total_value_label = self._create_stat_card(
            stats_frame, 0, "TOTAL TASKS", COLORS["accent"])
        self.active_value_label = self._create_stat_card(
            stats_frame, 1, "ACTIVE", COLORS["warning"])
        self.completed_value_label = self._create_stat_card(
            stats_frame, 2, "COMPLETED", COLORS["success"])

    def _create_progress(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(0, 16))

        row = tk.Frame(frame, bg=COLORS["bg"])
        row.pack(fill="x", pady=(0, 6))

        tk.Label(
            row, text="Progress",
            font=(FONT_FAMILY, 9, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(side="left")

        self.progress_label = tk.Label(
            row, text="0% completed",
            font=(FONT_FAMILY, 9),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        )
        self.progress_label.pack(side="right")

        bar_bg = tk.Frame(frame, bg=COLORS["border"], height=10)
        bar_bg.pack(fill="x")
        bar_bg.pack_propagate(False)

        self.progress_fill = tk.Frame(bar_bg, bg=COLORS["accent"])
        self.progress_fill.place(x=0, y=0, relheight=1.0, relwidth=0)

    def _make_entry(self, parent, textvariable):
        return tk.Entry(
            parent, textvariable=textvariable,
            font=(FONT_FAMILY, 11),
            bg=COLORS["input"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )

    def _create_input_card(self, parent):
        card = tk.Frame(
            parent, bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border"],
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card, text="Add a new task",
            font=(FONT_FAMILY, 11, "bold"),
            fg=COLORS["text"], bg=COLORS["surface"],
        ).pack(anchor="w", padx=16, pady=(14, 8))

        row = tk.Frame(card, bg=COLORS["surface"])
        row.pack(fill="x", padx=16)

        self.title_entry = self._make_entry(row, self.title_var)
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=7)
        self.title_entry.bind("<Return>", lambda _e: self.add_task())

        self.priority_combo = ttk.Combobox(
            row, textvariable=self.priority_var,
            values=list(PRIORITY_COLORS.keys()),
            state="readonly", width=11,
            style="Dark.TCombobox", font=(FONT_FAMILY, 10),
        )
        self.priority_combo.pack(side="left", padx=(0, 10))

        add_button = tk.Button(
            row, text="+  Add Task", command=self.add_task,
            font=(FONT_FAMILY, 10, "bold"),
            bg=COLORS["accent"], fg="#FFFFFF",
            activebackground=COLORS["accent_hover"], activeforeground="#FFFFFF",
            relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
        )
        add_button.pack(side="left")

        self.description_entry = self._make_entry(card, self.description_var)
        self.description_entry.pack(fill="x", padx=16, pady=(10, 4), ipady=6)
        self.description_entry.bind("<Return>", lambda _e: self.add_task())

        tk.Label(
            card, text="Title is required. Description is optional — press Enter to add quickly.",
            font=(FONT_FAMILY, 8),
            fg=COLORS["text_muted"], bg=COLORS["surface"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def _create_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=COLORS["bg"])
        toolbar.pack(fill="x", pady=(0, 10))

        # Search
        search_frame = tk.Frame(toolbar, bg=COLORS["bg"])
        search_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            search_frame, text="🔍",
            font=(FONT_FAMILY, 11),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(side="left", padx=(0, 6))

        self.search_entry = self._make_entry(search_frame, self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=5)

        tk.Button(
            search_frame, text="✕", command=self.clear_search,
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["surface"], fg=COLORS["text_secondary"],
            activebackground=COLORS["border"], activeforeground=COLORS["text"],
            relief="flat", bd=0, padx=10, pady=5, cursor="hand2",
        ).pack(side="left", padx=(8, 16))

        # Filters
        filter_frame = tk.Frame(toolbar, bg=COLORS["bg"])
        filter_frame.pack(side="right")

        self.filter_buttons = {}
        for key, label in (("All", "All Tasks"),
                           ("Active", "Active"),
                           ("Completed", "Completed")):
            button = tk.Button(
                filter_frame, text=label,
                command=lambda f=key: self.set_filter(f),
                font=(FONT_FAMILY, 9, "bold"),
                relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
            )
            button.pack(side="left", padx=2)
            self.filter_buttons[key] = button

    def _create_task_list(self, parent):
        list_header = tk.Frame(parent, bg=COLORS["bg"])
        list_header.pack(fill="x", pady=(2, 8))

        tk.Label(
            list_header, text="Your Tasks",
            font=(FONT_FAMILY, 13, "bold"),
            fg=COLORS["text"], bg=COLORS["bg"],
        ).pack(side="left")

        self.task_count_label = tk.Label(
            list_header, text="",
            font=(FONT_FAMILY, 9),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        )
        self.task_count_label.pack(side="right")

        canvas_frame = tk.Frame(parent, bg=COLORS["bg"])
        canvas_frame.pack(fill="both", expand=True)

        self.task_canvas = tk.Canvas(
            canvas_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            canvas_frame, orient="vertical",
            command=self.task_canvas.yview, style="Vertical.TScrollbar")
        self.task_canvas.configure(yscrollcommand=scrollbar.set)

        self.task_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.task_frame = tk.Frame(self.task_canvas, bg=COLORS["bg"])
        self.task_window = self.task_canvas.create_window(
            (0, 0), window=self.task_frame, anchor="nw")

        self.task_frame.bind("<Configure>", self._on_task_frame_configure)
        self.task_canvas.bind("<Configure>", self._on_canvas_configure)

    def _create_footer(self, parent):
        footer = tk.Frame(parent, bg=COLORS["bg"])
        footer.pack(fill="x", pady=(12, 0))

        self.status_label = tk.Label(
            footer, text="",
            font=(FONT_FAMILY, 9),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        )
        self.status_label.pack(side="left")

        tk.Button(
            footer, text="Clear Completed", command=self.clear_completed,
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["surface"], fg=COLORS["danger"],
            activebackground=COLORS["border"], activeforeground=COLORS["danger"],
            relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
        ).pack(side="right")

    # -- Scrolling ---------------------------------------------------------

    def _on_task_frame_configure(self, _event):
        self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.task_canvas.itemconfig(self.task_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.grab_current() is not None:  # A modal dialog is open
            return
        if event.delta:
            self.task_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_up(self, _event):
        if self.grab_current() is None:
            self.task_canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, _event):
        if self.grab_current() is None:
            self.task_canvas.yview_scroll(1, "units")

    # -- Filtering / rendering ---------------------------------------------

    def get_filtered_tasks(self):
        search_text = self.search_var.get().strip().lower()
        tasks = self.task_manager.tasks

        if self.current_filter == "Active":
            tasks = [t for t in tasks if not t["completed"]]
        elif self.current_filter == "Completed":
            tasks = [t for t in tasks if t["completed"]]

        if search_text:
            tasks = [t for t in tasks if search_text in t["title"].lower()]

        return tasks

    def refresh_task_list(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        filtered_tasks = self.get_filtered_tasks()

        if not filtered_tasks:
            self._show_empty_state()
        else:
            for task in filtered_tasks:
                self._create_task_card(task)

        total = len(self.task_manager.tasks)
        self.task_count_label.configure(
            text=f"Showing {len(filtered_tasks)} of {total} tasks")
        self._update_filter_buttons()
        self._update_stats()

    def _show_empty_state(self):
        frame = tk.Frame(self.task_frame, bg=COLORS["bg"])
        frame.pack(fill="x", pady=50)

        if self.search_var.get().strip():
            message = "No tasks match your search."
            hint = "Try a different search term."
        elif self.current_filter != "All":
            message = f"No {self.current_filter.lower()} tasks."
            hint = "Tasks matching this filter will appear here."
        else:
            message = "No tasks yet."
            hint = "Add your first task above to get started."

        tk.Label(
            frame, text=message,
            font=(FONT_FAMILY, 14, "bold"),
            fg=COLORS["text"], bg=COLORS["bg"],
        ).pack()
        tk.Label(
            frame, text=hint,
            font=(FONT_FAMILY, 10),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(pady=(6, 0))

    def _create_task_card(self, task):
        completed = task["completed"]
        priority_color = PRIORITY_COLORS.get(task["priority"], COLORS["accent"])

        card = tk.Frame(
            self.task_frame, bg=COLORS["card"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["border"],
        )
        card.pack(fill="x", padx=2, pady=5)

        # Left accent bar (green when completed, priority colour otherwise)
        tk.Frame(
            card, width=5,
            bg=COLORS["success"] if completed else priority_color,
        ).pack(side="left", fill="y")

        # Checkbox toggle
        tk.Button(
            card, text="☑" if completed else "☐",
            command=lambda tid=task["id"]: self.toggle_task(tid),
            font=(FONT_FAMILY, 18),
            fg=COLORS["success"] if completed else COLORS["text_secondary"],
            bg=COLORS["card"], activebackground=COLORS["card"],
            relief="flat", bd=0, cursor="hand2",
        ).pack(side="left", padx=(10, 4))

        # Text content
        content = tk.Frame(card, bg=COLORS["card"])
        content.pack(side="left", fill="both", expand=True, padx=8, pady=10)

        title_font = (FONT_FAMILY, 12, "bold overstrike") if completed \
            else (FONT_FAMILY, 12, "bold")
        title_label = tk.Label(
            content, text=task["title"], font=title_font,
            fg=COLORS["text_muted"] if completed else COLORS["text"],
            bg=COLORS["card"], anchor="w", justify="left", wraplength=480,
        )
        title_label.pack(anchor="w", fill="x")

        if task["description"]:
            tk.Label(
                content, text=task["description"],
                font=(FONT_FAMILY, 9),
                fg=COLORS["text_muted"] if completed else COLORS["text_secondary"],
                bg=COLORS["card"], anchor="w", justify="left", wraplength=480,
            ).pack(anchor="w", fill="x", pady=(3, 0))

        meta = tk.Frame(content, bg=COLORS["card"])
        meta.pack(anchor="w", pady=(7, 0))

        tk.Label(
            meta, text=f"  {task['priority']}  ",
            font=(FONT_FAMILY, 8, "bold"),
            fg="#FFFFFF", bg=priority_color,
        ).pack(side="left")

        if task["created_at"]:
            tk.Label(
                meta, text=task["created_at"],
                font=(FONT_FAMILY, 8),
                fg=COLORS["text_muted"], bg=COLORS["card"],
            ).pack(side="left", padx=(10, 0))

        # Action buttons
        actions = tk.Frame(card, bg=COLORS["card"])
        actions.pack(side="right", padx=12)

        tk.Button(
            actions, text="Edit",
            command=lambda t=task: self.open_edit_dialog(t),
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["surface"], fg=COLORS["text"],
            activebackground=COLORS["border"], activeforeground=COLORS["text"],
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            actions, text="Delete",
            command=lambda tid=task["id"]: self.delete_task(tid),
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["surface"], fg=COLORS["danger"],
            activebackground=COLORS["border"], activeforeground=COLORS["danger"],
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2",
        ).pack(side="left")

        # Double-click a task to edit it
        for widget in (card, content, title_label):
            widget.bind(
                "<Double-Button-1>",
                lambda _e, t=task: self.open_edit_dialog(t))

    def _update_filter_buttons(self):
        for key, button in self.filter_buttons.items():
            if key == self.current_filter:
                button.configure(
                    bg=COLORS["accent"], fg="#FFFFFF",
                    activebackground=COLORS["accent_hover"],
                    activeforeground="#FFFFFF")
            else:
                button.configure(
                    bg=COLORS["surface"], fg=COLORS["text_secondary"],
                    activebackground=COLORS["border"],
                    activeforeground=COLORS["text"])

    def _update_stats(self):
        total = len(self.task_manager.tasks)
        completed = sum(1 for t in self.task_manager.tasks if t["completed"])
        active = total - completed
        percent = int((completed / total) * 100) if total else 0

        self.total_value_label.configure(text=str(total))
        self.active_value_label.configure(text=str(active))
        self.completed_value_label.configure(text=str(completed))

        self.progress_label.configure(
            text=f"{percent}% completed  •  {completed} of {total} done")
        self.progress_fill.place(
            x=0, y=0, relheight=1.0, relwidth=percent / 100 if total else 0)

        self.status_label.configure(
            text=f"{total} total tasks  •  {completed} completed  •  {active} remaining")

    # -- Actions -----------------------------------------------------------

    def save_data(self):
        if not self.task_manager.save_tasks():
            messagebox.showerror(
                "Save Error",
                "TaskFlow could not save your tasks to tasks.json.\n"
                "Please check that the folder is writable.",
                parent=self,
            )

    def add_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning(
                "Empty Task",
                "Please enter a task title before adding it.",
                parent=self,
            )
            self.title_entry.focus_set()
            return

        self.task_manager.add_task(
            title=title,
            description=self.description_var.get().strip(),
            priority=self.priority_var.get(),
        )
        self.save_data()

        self.title_var.set("")
        self.description_var.set("")
        self.priority_var.set("Medium")
        self.refresh_task_list()
        self.title_entry.focus_set()

    def toggle_task(self, task_id):
        if self.task_manager.toggle_task(task_id):
            self.save_data()
            self.refresh_task_list()

    def delete_task(self, task_id):
        task = self.task_manager.get_task(task_id)
        if task is None:
            return

        confirmed = messagebox.askyesno(
            "Delete Task",
            f"Delete \"{task['title']}\"?\n\nThis action cannot be undone.",
            parent=self,
        )
        if confirmed:
            self.task_manager.delete_task(task_id)
            self.save_data()
            self.refresh_task_list()

    def clear_completed(self):
        completed = sum(1 for t in self.task_manager.tasks if t["completed"])
        if completed == 0:
            messagebox.showinfo(
                "No Completed Tasks",
                "There are no completed tasks to clear.",
                parent=self,
            )
            return

        confirmed = messagebox.askyesno(
            "Clear Completed Tasks",
            f"Delete all {completed} completed task(s)?\n\n"
            "This action cannot be undone.",
            parent=self,
        )
        if confirmed:
            self.task_manager.clear_completed()
            self.save_data()
            self.refresh_task_list()

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus_set()

    def set_filter(self, filter_name):
        self.current_filter = filter_name
        self.refresh_task_list()

    # -- Edit dialog -------------------------------------------------------

    def open_edit_dialog(self, task):
        dialog = tk.Toplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("480x360")
        dialog.resizable(False, False)
        dialog.configure(bg=COLORS["bg"])
        dialog.transient(self)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        title_var = tk.StringVar(value=task["title"])
        description_var = tk.StringVar(value=task["description"])
        priority_var = tk.StringVar(value=task["priority"])
        completed_var = tk.BooleanVar(value=task["completed"])

        container = tk.Frame(dialog, bg=COLORS["bg"])
        container.pack(fill="both", expand=True, padx=22, pady=20)

        tk.Label(
            container, text="Edit Task",
            font=(FONT_FAMILY, 15, "bold"),
            fg=COLORS["text"], bg=COLORS["bg"],
        ).pack(anchor="w", pady=(0, 14))

        tk.Label(
            container, text="Title *",
            font=(FONT_FAMILY, 9, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(anchor="w")
        title_entry = self._make_entry(container, title_var)
        title_entry.pack(fill="x", pady=(4, 12), ipady=6)

        tk.Label(
            container, text="Description (optional)",
            font=(FONT_FAMILY, 9, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(anchor="w")
        self._make_entry(container, description_var).pack(
            fill="x", pady=(4, 12), ipady=6)

        tk.Label(
            container, text="Priority",
            font=(FONT_FAMILY, 9, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["bg"],
        ).pack(anchor="w")
        ttk.Combobox(
            container, textvariable=priority_var,
            values=list(PRIORITY_COLORS.keys()),
            state="readonly", style="Dark.TCombobox",
            font=(FONT_FAMILY, 10),
        ).pack(fill="x", pady=(4, 12))

        tk.Checkbutton(
            container, text="Mark as completed", variable=completed_var,
            font=(FONT_FAMILY, 10),
            bg=COLORS["bg"], fg=COLORS["text"],
            activebackground=COLORS["bg"], activeforeground=COLORS["text"],
            selectcolor=COLORS["surface"], cursor="hand2",
        ).pack(anchor="w", pady=(0, 18))

        buttons = tk.Frame(container, bg=COLORS["bg"])
        buttons.pack(fill="x")

        def save_edit():
            new_title = title_var.get().strip()
            if not new_title:
                messagebox.showwarning(
                    "Empty Task",
                    "The task title cannot be empty.",
                    parent=dialog,
                )
                title_entry.focus_set()
                return

            self.task_manager.update_task(
                task_id=task["id"],
                title=new_title,
                description=description_var.get().strip(),
                priority=priority_var.get(),
                completed=completed_var.get(),
            )
            self.save_data()
            self.refresh_task_list()
            dialog.destroy()

        tk.Button(
            buttons, text="Cancel", command=dialog.destroy,
            font=(FONT_FAMILY, 10, "bold"),
            bg=COLORS["surface"], fg=COLORS["text"],
            activebackground=COLORS["border"], activeforeground=COLORS["text"],
            relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
        ).pack(side="right")

        tk.Button(
            buttons, text="Save Changes", command=save_edit,
            font=(FONT_FAMILY, 10, "bold"),
            bg=COLORS["accent"], fg="#FFFFFF",
            activebackground=COLORS["accent_hover"], activeforeground="#FFFFFF",
            relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
        ).pack(side="right", padx=(0, 8))

        dialog.bind("<Return>", lambda _e: save_edit())
        dialog.bind("<Escape>", lambda _e: dialog.destroy())

        # Centre the dialog over the main window
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        title_entry.focus_set()
        title_entry.select_range(0, tk.END)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = TaskFlowApp()
    app.mainloop()





## 2. `tasks.json`

# > This file is created automatically if missing. 
# The sample below gives you a few demo tasks on first launch — replace it with `[]` if you prefer to start empty.

json
[
  {
    "id": "sample-1",
    "title": "Welcome to TaskFlow",
    "description": "Click the checkbox to complete a task, or use Edit / Delete on the right.",
    "priority": "Medium",
    "completed": False,
    "created_at": "Jan 01, 2026"
  },
  {
    "id": "sample-2",
    "title": "Try editing this task",
    "description": "Double-click any task (or press Edit) to change its title, description, priority or status.",
    "priority": "High",
    "completed": False,
    "created_at": "Jan 01, 2026"
  },
  {
    "id": "sample-3",
    "title": "Use search and filters",
    "description": "Search by title, then switch between All, Active and Completed above.",
    "priority": "Low",
    "completed": True,
    "created_at": "Jan 01, 2026"
  }
]

"""
A beautiful, reliable, beginner-friendly desktop To-Do List app built
with **Python 3**, **Tkinter/ttk**, and **JSON** storage.
No external packages required — only Python's standard library.

## Features
- ✅ Add, edit, and delete tasks (double-click a task to edit it)
- ☑️ Mark tasks as completed with a checkbox toggle
- 🔍 Search tasks by title (live, as you type)
- 🗂️ Filter by **All Tasks / Active / Completed**
- 📊 Live statistics: total, active, completed + progress bar
- 🏷️ Optional description and priority (Low / Medium / High) per task
- 💾 Automatic saving to `tasks.json` after every change
- 🛡️ Graceful handling of missing or corrupted data files
  (a corrupt file is backed up as `tasks.json.bak`)
- 🌙 Modern dark theme with a clean, responsive layout

## Usage
| Action            | How                                              |
|-------------------|--------------------------------------------------|
| Add a task        | Type a title, press **Enter** or **Add Task**    |
| Complete a task   | Click the checkbox on the left of the task       |
| Edit a task       | Click **Edit**, or double-click the task         |
| Delete a task     | Click **Delete** and confirm                     |
| Search            | Type in the search box (or press `Ctrl+F`)       |
| Filter            | Click **All Tasks / Active / Completed**         |
| Clear finished    | Click **Clear Completed** in the bottom-right    |

## Data Storage
Tasks are stored in `tasks.json` next to `main.py`. Every add, edit,
completion, and deletion is saved immediately, so your tasks are still
there when you restart the app.

"""