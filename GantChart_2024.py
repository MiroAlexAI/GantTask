import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, colorchooser
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
from datetime import datetime, timedelta
import csv

class GanttChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gantt Chart Task Manager")

        self.tasks = []
        self.selected_task = None

        # Предустановленные цвета
        self.colors = ["skyblue", "lightgreen", "lightcoral", "lightyellow", "plum", "lightsalmon"]

        # GUI элементы
        self.task_name_label = tk.Label(root, text="Task Name")
        self.task_name_label.pack()

        self.task_name_entry = tk.Entry(root)
        self.task_name_entry.pack()

        self.start_date_label = tk.Label(root, text="Start Date (YYYY-MM-DD)")
        self.start_date_label.pack()

        self.start_date_entry = tk.Entry(root)
        self.start_date_entry.pack()

        self.duration_label = tk.Label(root, text="Duration (days)")
        self.duration_label.pack()

        self.duration_entry = tk.Entry(root)
        self.duration_entry.pack()

        self.color_label = tk.Label(root, text="Task Color")
        self.color_label.pack()

        self.color_var = tk.StringVar(value=self.colors[0])
        self.color_menu = tk.OptionMenu(root, self.color_var, *self.colors)
        self.color_menu.pack()

        self.custom_color_button = tk.Button(root, text="Choose Custom Color", command=self.choose_custom_color)
        self.custom_color_button.pack()

        self.add_task_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_task_button.pack()

        self.show_chart_button = tk.Button(root, text="Show Gantt Chart", command=self.show_gantt_chart)
        self.show_chart_button.pack()

        self.save_button = tk.Button(root, text="Save to CSV", command=self.save_to_csv)
        self.save_button.pack()

        self.load_button = tk.Button(root, text="Load from CSV", command=self.load_from_csv)
        self.load_button.pack()

    def choose_custom_color(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            self.color_var.set(color_code)

    def add_task(self):
        task_name = self.task_name_entry.get()
        start_date_str = self.start_date_entry.get()
        duration = self.duration_entry.get()
        color = self.color_var.get()

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format or duration")
            return

        self.tasks.append([task_name, start_date, duration, color])
        messagebox.showinfo("Success", "Task added successfully")

        self.task_name_entry.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

    def show_gantt_chart(self):
        if not self.tasks:
            messagebox.showerror("Error", "No tasks to show")
            return

        self.fig, self.ax = plt.subplots()

        for i, (task_name, start_date, duration, color) in enumerate(self.tasks):
            self.ax.broken_barh([(date2num(start_date), duration)], (i - 0.4, 0.8), facecolors=color)
            self.ax.text(date2num(start_date), i, task_name, ha='left', va='center')

        self.ax.set_yticks(range(len(self.tasks)))
        self.ax.set_yticklabels([task[0] for task in self.tasks])
        self.ax.xaxis_date()

        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_double_click = self.fig.canvas.mpl_connect('button_press_event', self.on_double_click)

        plt.show()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        for i, (task_name, start_date, duration, color) in enumerate(self.tasks):
            task_start_num = date2num(start_date)
            if (task_start_num <= event.xdata <= task_start_num + duration) and (i - 0.4 <= event.ydata <= i + 0.4):
                self.selected_task = i
                self.offset = event.xdata - task_start_num
                break

    def on_release(self, event):
        self.selected_task = None

    def on_motion(self, event):
        if self.selected_task is None or event.inaxes != self.ax:
            return

        new_start_date = num2date(event.xdata - self.offset).date()
        self.tasks[self.selected_task][1] = datetime.combine(new_start_date, datetime.min.time())

        self.update_chart()

    def on_double_click(self, event):
        if event.dblclick and event.inaxes == self.ax:
            for i, (task_name, start_date, duration, color) in enumerate(self.tasks):
                task_start_num = date2num(start_date)
                if (task_start_num <= event.xdata <= task_start_num + duration) and (i - 0.4 <= event.ydata <= i + 0.4):
                    self.selected_task = i
                    self.edit_task(i)
                    break

    def edit_task(self, task_index):
        task_name = self.tasks[task_index][0]
        start_date = self.tasks[task_index][1].strftime("%Y-%m-%d")
        duration = self.tasks[task_index][2]
        color = self.tasks[task_index][3]

        new_task_name = simpledialog.askstring("Edit Task", "Task Name:", initialvalue=task_name)
        new_start_date = simpledialog.askstring("Edit Task", "Start Date (YYYY-MM-DD):", initialvalue=start_date)
        new_duration = simpledialog.askinteger("Edit Task", "Duration (days):", initialvalue=duration)
        new_color = simpledialog.askstring("Edit Task", "Task Color:", initialvalue=color)

        if new_task_name and new_start_date and new_duration and new_color:
            try:
                new_start_date = datetime.strptime(new_start_date, "%Y-%m-%d")
                new_duration = int(new_duration)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format or duration")
                return

            self.tasks[task_index] = [new_task_name, new_start_date, new_duration, new_color]
            self.update_chart()

    def update_chart(self):
        self.ax.clear()
        for i, (task_name, start_date, duration, color) in enumerate(self.tasks):
            self.ax.broken_barh([(date2num(start_date), duration)], (i - 0.4, 0.8), facecolors=color)
            self.ax.text(date2num(start_date), i, task_name, ha='left', va='center')

        self.ax.set_yticks(range(len(self.tasks)))
        self.ax.set_yticklabels([task[0] for task in self.tasks])
        self.ax.xaxis_date()

        self.ax.grid(True)

        self.fig.canvas.draw()

    def save_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Task Name", "Start Date", "Duration (days)", "Color"])
            for task in self.tasks:
                writer.writerow([task[0], task[1].strftime("%Y-%m-%d"), task[2], task[3]])

        messagebox.showinfo("Success", "Tasks saved successfully")

    def load_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок
            self.tasks = []
            for row in reader:
                task_name = row[0]
                start_date = datetime.strptime(row[1], "%Y-%m-%d")
                duration = int(row[2])
                color = row[3]
                self.tasks.append([task_name, start_date, duration, color])

        messagebox.showinfo("Success", "Tasks loaded successfully")
        self.update_chart()

if __name__ == "__main__":
    root = tk.Tk()
    app = GanttChartApp(root)
    root.mainloop()
