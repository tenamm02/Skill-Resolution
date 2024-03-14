import tkinter as tk
from tkinter import messagebox

# Define a structure to hold the parsed data
questions = []

# Create the Tkinter window
root = tk.Tk()
root.title("Quiz")


# Open the file and read line by line

questions = []

with open("Testdoc.txt", "r") as file:
    current_question = {}
    for line in file:
        # Check for the start of a new question
        if line.strip().startswith('Question'):
            current_question = {'question': line.split(':', 1)[1].strip(), 'options': [], 'answer': ''}
        elif line.strip().startswith(('A )', 'B )', 'C )', 'D )')):
            # If the line is an option, add it to the options list
            current_question['options'].append(line.strip())
        elif line.strip().startswith('An'):
            # If the line indicates an answer, save only the letter to the current question
            current_question['answer'] = line.split(':', 1)[1].strip().split()[0]
            questions.append(current_question)

# Print the entire list of answers
for question in questions:
    print(question['answer'])


# Define a function to move to the next question
# Define a function to move to the next question
# Define a function to move to the next question
def next_question():
    current_question_index = current_question_index_var.get()
    if current_question_index < len(questions) - 1:
        current_question_index += 1
        current_question_index_var.set(current_question_index)
        display_question()
    else:
        check_answers()

# Create widgets
question_label = tk.Label(root, text="", wraplength=400, justify="left", font=("Arial", 12))
question_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

option_buttons = []
selected_options = []
current_question_index_var = tk.IntVar(value=0)
for _ in range(4):
    selected_options.append(tk.IntVar(value=-1))  # Initialize IntVar for each question
for _ in range(4):
    option_button = tk.Radiobutton(root, text="", variable=selected_options[-1], value=len(option_buttons))
    option_button.grid(row=len(option_buttons)+1, column=0, columnspan=2, padx=10, sticky="w")
    option_buttons.append(option_button)

next_button = tk.Button(root, text="Next", command=next_question)
next_button.grid(row=len(option_buttons)+1, column=0, columnspan=2, pady=10)


# Define a function to display the current question
def display_question():
    index = current_question_index_var.get()
    if index < len(selected_options):
        question_label.config(text=questions[index]['question'])
        for i, option in enumerate(questions[index]['options']):
            option_buttons[i].config(text=option)
        selected_option = selected_options[index].get()
        if selected_option != -1:
            selected_options[index].set(-1)
    else:
        messagebox.showerror("Error", "Index out of range!")


# Define a function to check the answers and calculate the score
def check_answers():
    score = 0
    unanswered = False
    for i, question in enumerate(questions):
        selected_option_index = selected_options[i].get()
        if selected_option_index == -1:
            unanswered = True
            break
        selected_option = question['options'][selected_option_index]
        correct_answer = question['answer']

        # Debugging: Print selected option and correct answer
        print(f"Question {i + 1}: Selected Option - {selected_option}, Correct Answer - {correct_answer}")

        if selected_option == correct_answer:
            score += 1

    print(f"Score: {score}")  # Debugging: Print the score

    if unanswered:
        messagebox.showwarning("Warning", "Please answer all questions!")
    else:
        messagebox.showinfo("Score", f"Your score is: {score}/{len(questions)}")


# Display the first question
display_question()

# Start the Tkinter event loop
root.mainloop()

