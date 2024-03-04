import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from fake_course_generator import generate_fake_course

class AugmentedRealityApp:
    def __init__(self, master):
        self.master = master
        master.title("AR Learning Content Generator")
        master.state('zoomed')  # Maximize the window
        
        # Configure the grid to expand and fill the space
        master.grid_columnconfigure(0, weight=1)
        for i in range(8):  # Adjust the range as needed
            master.grid_rowconfigure(i, weight=1)

        self.chat_text = scrolledtext.ScrolledText(master, width=60, height=10, wrap=tk.WORD)
        self.level_label = tk.Label(master, text="Enter your current level of knowledge:")
        self.knowledge_level = tk.Scale(master, from_=0, to=2, orient=tk.HORIZONTAL, showvalue=0, tickinterval=1, resolution=1)
        self.label_var = tk.StringVar()
        self.label_display = tk.Label(master, textvariable=self.label_var)
        self.generate_button = tk.Button(master, text="Generate Learning Content", command=self.generate_ar_content)
        self.ar_content_label = tk.Label(master, text="Learning Content:")
        self.ar_output = tk.Label(master, text="", wraplength=400, justify="left")
        self.link_to_ar_button = tk.Button(master, text="Link to AR", command=self.open_ar_link)

        # Layout widgets
        self.chat_text.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")
        self.level_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.knowledge_level.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.label_display.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.generate_button.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.ar_content_label.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        self.ar_output.grid(row=6, column=0, padx=10, pady=5, columnspan=2, sticky="nsew")
        self.link_to_ar_button.grid(row=7, column=0, padx=10, pady=10, sticky="nsew")

        # Initialize label display and course data
        self.update_label(self.knowledge_level.get())
        self.fake_course_data = None

        # Call the update_label method when the knowledge level changes
        self.knowledge_level.config(command=self.update_label)

        # Initialize label display and course data
        self.update_label(self.knowledge_level.get())
        self.fake_course_data = None
        
    def open_ar_link(self):
        # Add functionality to open the AR link here
        # For now, just showing a messagebox as a placeholder
        messagebox.showinfo("Link to AR", "This will link to the AR content.")

    def update_label(self, value):
        labels = ["New", "Moderate", "Strong"]
        self.label_var.set(f"Selected Level: {labels[int(value)]}")

    def generate_ar_content(self):
        chat_input = self.chat_text.get("1.0", tk.END).strip()
        knowledge_level = self.knowledge_level.get()
        self.generate_ar_content_backend(chat_input, knowledge_level)
        self.display_course_content()

    def generate_ar_content_backend(self, chat_input, knowledge_level):
        fake_course_json = generate_fake_course()
        self.fake_course_data = json.loads(fake_course_json)
        # You may update the UI with the course title or other details here if needed

    def display_course_content(self):
        self.course_window = tk.Toplevel(self.master)
        self.course_window.title("Course Content")

        # Make the course window full screen
        self.course_window.state('zoomed')

        # Display course title and description from fake_course_data
        course_title = self.fake_course_data["course_title"]
        course_description = self.fake_course_data["course_description"]
        self.course_title_label = tk.Label(self.course_window, text=course_title)
        self.course_title_label.pack()
        self.course_description_label = tk.Label(self.course_window, text=course_description)
        self.course_description_label.pack()

        # Treeview for modules and lessons
        self.course_tree = ttk.Treeview(self.course_window)
        self.course_tree.pack(expand=True, fill='both')

        # Populate Treeview with modules and lessons
        for module in self.fake_course_data['modules']:
            module_id = self.course_tree.insert('', 'end', text=module['module_title'])
            for lesson in module['lessons']:
                self.course_tree.insert(module_id, 'end', text=lesson['lesson_title'])

        # Text area for displaying selected lesson content
        self.lesson_content_text = tk.Text(self.course_window, wrap='word')
        self.lesson_content_text.pack(expand=True, fill='both')

        # Bind the Treeview select event
        self.course_tree.bind('<<TreeviewSelect>>', self.on_lesson_select)

    def on_lesson_select(self, event):
        selected_item = self.course_tree.selection()[0]
        lesson_title = self.course_tree.item(selected_item, 'text')

        # Clear previous content
        self.lesson_content_text.delete('1.0', tk.END)

        # Display content for selected lesson
        for module in self.fake_course_data['modules']:
            for lesson in module['lessons']:
                if lesson['lesson_title'] == lesson_title:
                    self.lesson_content_text.insert(tk.END, lesson['lesson_content'])

def main():
    root = tk.Tk()  # Create the root window first
    app = ARSketchfabApp(root)  # Pass the root window to your application
    root.mainloop()

if __name__ == "__main__":
    main()