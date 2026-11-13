# TaskFlow – Python To-Do List Application

A modern and user-friendly desktop task management application built with **Python** and **Tkinter**. TaskFlow helps you organize daily tasks, track progress, and manage priorities through a clean dark-themed interface.

## ✨ Features

- **Task Management:** Create, edit, and delete tasks.
- **Priority Levels:** Assign Low, Medium, or High priority to each task.
- **Task Tracking:** Mark tasks as completed or active.
- **Live Search:** Instantly find tasks by title.
- **Smart Filtering:** Filter tasks by All, Active, or Completed.
- **Progress Tracking:** Monitor completion statistics with a dynamic progress bar.
- **Task Descriptions:** Add optional descriptions to your tasks.
- **Persistent Storage:** Automatically save tasks using JSON.
- **Data Recovery:** Handle corrupted data files with automatic backup.
- **Dark UI:** Enjoy a clean and modern desktop interface.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core application logic |
| Tkinter / ttk | Desktop graphical interface |
| JSON | Persistent data storage |
| UUID | Unique task identification |
| pathlib | File and path management |

## 🚀 Getting Started

### Prerequisites

- Python 3 installed on your system.
- Tkinter support available in your Python installation.

No external Python packages are required.

### Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/taskflow-python-todo.git
```

2. Navigate to the project directory:

```bash
cd taskflow-python-todo
```

3. Run the application:

```bash
python main.py
```

The application automatically creates `tasks.json` if it does not already exist.

## 📖 How to Use

| Action | Instruction |
|---|---|
| Add a task | Enter a title and click Add Task |
| Complete a task | Click the checkbox |
| Edit a task | Click Edit or double-click a task |
| Delete a task | Click Delete and confirm |
| Search tasks | Use the search bar or press `Ctrl + F` |
| Filter tasks | Select All Tasks, Active, or Completed |
| Clear completed | Click Clear Completed |

## 💾 Data Storage

TaskFlow uses a local JSON file to store task information.

- Tasks are saved automatically after every modification.
- Your data remains available after restarting the application.
- If the data file becomes corrupted or unreadable, the application attempts to back it up as `tasks.json.bak`.

All task data is stored locally on your computer.

## 🎨 Interface

TaskFlow features a modern dark-themed interface with:

- A clean and organized layout.
- Priority-based color indicators.
- Task statistics and progress tracking.
- Scrollable task cards.
- Interactive controls and confirmation dialogs.

## 🔮 Future Improvements

Potential features for future versions:

- Task deadlines and reminders.
- Task categories and tags.
- Sorting tasks by priority or creation date.
- Export and import functionality.
- Improved customization options.

## 📄 License

This project is open-source. You are free to explore, modify, and build upon it.

---

**Built with Python ❤️**

*Stay organized, stay productive.*
