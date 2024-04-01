import tkinter as tk
from tkinter import messagebox
import sqlite3

# Define a structure to hold the parsed data
questions = []

# Temporary variables to hold information while parsing
current_question = {}
options = []

# Add your file path here
file_path = "Testdoc.txt"

# Open the file and read line by line
with open(file_path, "r") as file:
    for line in file:
        line = line.strip()
        if line.startswith('Question'):
            # Save the previous question if there is one
            if current_question:
                current_question['options'] = options
                questions.append(current_question)
                options = []  # Reset options list for the next question
            # Start a new question
            current_question = {'question': line.split(':', 1)[1].strip(), 'options': []}
        elif line.startswith(('A ','B ','C ','D ')):
            # Normalize spacing within options and add them to the options list
            option_text = ' '.join(line.split())
            options.append(option_text)

        elif line.startswith('An swer'):
            # The answer is appended as is; normalization of spaces is optional
            answer_text = ' '.join(line.split(':', 1)[1].strip().split())
            current_question['answer'] = answer_text
            print(answer_text)

    # Don't forget to add the last question if it has options
    if current_question and options:
        current_question['options'] = options
        questions.append(current_question)

def save_questions(questions):
    conn = sqlite3.connect('quiz_database.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        question TEXT,
        options TEXT,
        answer TEXT,
        topic TEXT
    )
    ''')
    for question in questions:
        question_data = (
            question['question'],
            ' ,'.join(question['options']),
            question['answer'],
            question.get('topic', 'No topic')
        )
        c.execute('''
        INSERT INTO questions (question, options, answer, topic)
        VALUES (?, ?, ?, ?)
        ''', question_data)
    conn.commit()
    conn.close()

class QuizApplication:
    def __init__(self, master, questions):
        self.master = master
        self.questions = questions
        self.current_question_index = 0
        self.correct_answers = 0
        self.create_widgets()

    def create_widgets(self):
        self.question_label = tk.Label(self.master, text="", wraplength=300)
        self.question_label.pack(pady=(20, 10))

        self.options_frame = tk.Frame(self.master)
        self.options_frame.pack(pady=(5, 20))

        self.selected_option_var = tk.StringVar(value="")  # This tracks the selected option
        self.option_buttons = []  # Keep track of the radiobuttons to update their text
        for _ in range(4):  # Assuming there are always 4 options
            btn = tk.Radiobutton(self.options_frame, text="", variable=self.selected_option_var, value="",
                                 wraplength=250)
            btn.pack(anchor="w")
            self.option_buttons.append(btn)

        self.next_button = tk.Button(self.master, text="Next", command=self.next_question)
        self.next_button.pack()

        self.update_question()

    def update_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.config(text=question['question'])
            options = question.get('options', [])  # Retrieve options for the current question
            for btn, option_text in zip(self.option_buttons, options):
                btn.config(text=option_text, value=option_text)  # Update text for each option
            self.selected_option_var.set("")  # Reset selected option

    def next_question(self):
        selected_option = self.selected_option_var.get()  # Get the selected option's value
        correct_answer = self.questions[self.current_question_index].get('answer', '')
        # Compare the selected option's first character to the correct answer
        if selected_option[0] == correct_answer[0]:
            self.correct_answers += 1

        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.update_question()
        else:
            messagebox.showinfo("Quiz Complete",
                                f"You answered {self.correct_answers} out of {len(self.questions)} questions correctly.")
            self.master.quit()

if __name__ == "__main__":
    save_questions(questions)  # Save questions to the database before starting the app
    root = tk.Tk()
    root.title("Quiz Application")
    app = QuizApplication(root, questions)
    root.mainloop()
