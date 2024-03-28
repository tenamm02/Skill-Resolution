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
        if line.strip().startswith('Question' or '*Question'):
            if current_question:
                Toppic = ''
                current_question['options'] = options.copy()
                current_question['topic'] = Toppic
                questions.append(current_question)
            
            current_question = {'question': line.split(':', 1)[1].strip()}
            options = []
        elif line.strip().startswith(('A ) ' or 'A) ', 'B ) ' or 'B) ', 'C ) ' or 'C) ', 'D ) ' or 'D) ')):
            option_letter = line.strip()
            options.append(option_letter)
        elif line.strip().startswith('An swer'):
            answer_letter = line.split(':', 1)[1].strip()[0] 
            current_question['answer'] = answer_letter
        elif line.strip().startswith('Topic'):
            Topic = line.strip()
            Toppic = Topic.strip("Topic")
            current_question['topic'] = Toppic


if current_question:
    if 'options' not in current_question:
        current_question['options'] = options
    questions.append(current_question)


for index, question in enumerate(questions, start=1):
    #print(f"Question {index}: {question['question']}")
    print("Options:")
    for option in question['options']:
        print(option)
    print("Answer:", question.get('answer', 'No answer provided'))
    print()  # Add a blank line for clarity
def save_questions(questions):
    conn = sqlite3.connect('quiz_database.db')
    c = conn.cursor()
    to = current_question.pop('topic')
    for questionz in questions:
        q_text = questionz.pop('question')
        a = questionz.pop('answer')



        o = questionz.pop('options')

        t = ''.join(str(x) for x in o)
        print(o)

        question_data = (q_text, t, a,to)

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
            btn = tk.Radiobutton(self.options_frame, text="", variable=self.selected_option_var, value="", wraplength=250)
            btn.pack(anchor="w")
            self.option_buttons.append(btn)

        self.next_button = tk.Button(self.master, text="Next", command=self.next_question)
        self.next_button.pack()

        self.update_question()

    def update_question(self):
        question = self.questions[self.current_question_index]
        self.question_label.config(text=question['question'])
        options = question.get('options', [])  # Retrieve options for the current question
        for btn, option in zip(self.option_buttons, options):
            btn.config(text=option, value=option)  # Update text for each option
        self.selected_option_var.set("")  # Reset selected option

    def next_question(self):
        selected_option = self.selected_option_var.get()  # Get the selected option's value
        correct_answer = self.questions[self.current_question_index]['answer']
        
        # Extract the answer letter from the selected option
        if selected_option:
            selected_answer = selected_option.strip()[0]
        else:
            selected_answer = None

        if selected_answer == correct_answer:
            self.correct_answers += 1

        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.update_question()
        else:
            messagebox.showinfo("Quiz Complete", f"You answered {self.correct_answers} out of {len(self.questions)} questions correctly.")
            self.master.quit()
    

if __name__ == "__main__":
    # Assuming 'questions' is your list of question dictionaries
    root = tk.Tk()
    root.title("Quiz Application")
    app = QuizApplication(root, questions)
    root.mainloop()
save_questions(questions)