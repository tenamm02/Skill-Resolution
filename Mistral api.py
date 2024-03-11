import tkinter as tk
from functools import partial
from tkinter import ttk, scrolledtext, messagebox
import requests
import json

import re
# Define a color scheme and styles
BACKGROUND_COLOR = "#333333"  # Dark gray
TEXT_COLOR = "#FFFFFF"  # White
BUTTON_COLOR = "#1E90FF"  # Dodger blue
ENTRY_BG = "#555555"  # Darker gray
FONT = ("Arial", 12)  # Define a font

# Configure style
style = ttk.Style()
style.theme_use('default')
style.configure('TEntry', foreground=TEXT_COLOR, fieldbackground=ENTRY_BG, font=FONT)
style.configure('TButton', background=BUTTON_COLOR, font=FONT)
style.configure('TLabel', background=BACKGROUND_COLOR, foreground=TEXT_COLOR, font=FONT)
style.configure('TFrame', background=BACKGROUND_COLOR)
MISTRAL_API_URL = 'http://localhost:11434/api/generate'
class ARSketchfabApp:
    def __init__(self, master):
        self.master = master
        master.title("AR Learning Content Generator & Sketchfab Model Viewer")
        master.state('zoomed')  # Maximize the window
        master.configure(bg=BACKGROUND_COLOR)

        # Create main frame
        main_frame = ttk.Frame(master)
        main_frame.grid(sticky='nsew', padx=10, pady=10)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Configure the grid to expand and fill the space
        for i in range(2):
            main_frame.grid_columnconfigure(i, weight=1)
            main_frame.grid_rowconfigure(i, weight=1)

        # Widgets for Search and Learning Content
        self.search_label = ttk.Label(main_frame, text="Enter a topic:")
        self.search_entry = ttk.Entry(main_frame)
        self.search_button = ttk.Button(main_frame, text="Generate Quiz", command=self.generate_and_display_quiz)
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR, bg=ENTRY_BG)

        # Layout widgets
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.search_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.results_text.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.user_answers = {}

        self.quiz_frame = ttk.Frame(master)  # Create a frame for quiz elements
        self.quiz_frame.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=10,
                             pady=5)  # Adjust grid positioning as needed

    def generate_and_display_quiz(self):
        generated_quiz = self.generate_quiz_with_mistral()
        if generated_quiz:
            self.structured_quiz = self.process_quiz_text_to_structure(generated_quiz)
            self.display_quiz()
        else:
            messagebox.showerror("Quiz Generation Failed", "Failed to generate quiz.")

    def display_quiz(self):
        # Clear any existing content from the quiz area
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        # Assuming self.structured_quiz is filled with quiz data
        for question_index, question in enumerate(self.structured_quiz):
            question_label = ttk.Label(self.quiz_frame, text=question["question"], font=FONT)
            question_label.pack(anchor="w")

            # Create a StringVar for each set of radio buttons
            answer_var = tk.StringVar(value="none")  # Default value to avoid unselected state
            self.user_answers[question_index] = answer_var  # Store the StringVar

            for option in question["options"]:
                option_button = ttk.Radiobutton(
                    self.quiz_frame, text=option, variable=answer_var, value=option,
                    command=partial(self.check_answer, question_index, option)
                )
                option_button.pack(anchor="w")

        submit_button = ttk.Button(self.quiz_frame, text="Submit Quiz", command=self.submit_quiz)
        submit_button.pack(pady=10)

    def check_answer(self, question_index, selected_option):
        # This method now simply updates the associated StringVar
        self.user_answers[question_index].set(selected_option)

    def submit_quiz(self):
        correct_answers = 0
        for question_index, answer_var in self.user_answers.items():
            if answer_var.get() == self.structured_quiz[question_index]['correct_answer']:
                correct_answers += 1

        total_questions = len(self.structured_quiz)
        messagebox.showinfo("Quiz Results", f"You got {correct_answers} out of {total_questions} correct.")
        # Clear the user's answers for a new quiz attempt
        for answer_var in self.user_answers.values():
            answer_var.set("none")

    def generate_quiz_with_mistral(self):
        topic = self.search_entry.get()
        prompt = f"Generate a quiz for {topic} with 5 multiple-choice questions, each having 4 options."
        data = {"model": "mistral", "prompt": prompt}
        response = requests.post(MISTRAL_API_URL, json=data)
        if response.status_code == 200:
            try:
                response_lines = response.content.decode('utf-8').strip().split('\n')
                generated_text = ' '.join(
                    item.get('response', '') for item in (json.loads(line) for line in response_lines))
                return generated_text


            except Exception as e:
                return None
        else:
            return None

    def process_quiz_text_to_structure(self, generated_text):
        # Initialize an empty list to store structured quiz data
        structured_quiz = []

        # Split the raw text into individual questions
        questions = re.split(r'\d+\.', generated_text)[1:]

        for question in questions:
            # Extract the question text
            question_text = question.split('?')[0].strip() + '?'

            # Extract options
            options_start_index = question.index('A.')
            options_end_index = question.index('ANSWER:')
            options_text = question[options_start_index:options_end_index].strip()
            options = [option.strip() for option in options_text.split('\n')]

            # Extract correct answer
            correct_answer_start_index = question.index('ANSWER:') + len('ANSWER:')
            correct_answer = question[correct_answer_start_index:].strip()

            # Append the question data to the structured quiz list
            structured_quiz.append({
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer
            })
        print(structured_quiz)
        return structured_quiz

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
