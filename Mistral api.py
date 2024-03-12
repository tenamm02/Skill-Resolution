import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import os
import json
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')
def list_strip(lst):
    return [item.strip() for item in lst]

def list_rstrip(lst, char="-"):
    return [item.rstrip(char) for item in lst]

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

# Set the Mistral API endpoint
MISTRAL_API_URL = 'http://localhost:11434/api/generate'
# Set the Sketchfab API token as an environment variable
os.environ['SKETCHFAB_API_TOKEN'] = '0e57c8a592a44347b8c9cf9cbee7bc5a'


def extract_key_sentences(content, num_questions=5):
    # Tokenize the content into sentences
    sentences = sent_tokenize(content)
    # Filter sentences that contain a question mark, which are likely questions
    question_sentences = [sentence for sentence in sentences if '?' in sentence]
    # If there aren't enough questions, fill in the remaining slots with the last sentences
    if len(question_sentences) < num_questions:
        question_sentences += sentences[-(num_questions - len(question_sentences)):]
    # Select the first 'num_questions' questions
    key_sentences = question_sentences[:num_questions]
    return key_sentences


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
        self.skill_label = ttk.Label(main_frame, text="Specific Skill:")
        self.skill_entry = ttk.Entry(main_frame)
        self.skill_level_label = ttk.Label(main_frame, text="Skill Level:")

        # Define skill levels and create a Combobox for skill level selection
        self.skill_levels = ["Beginning", "Intermediate", "Expert"]
        self.skill_level_combobox = ttk.Combobox(main_frame, values=self.skill_levels, state="readonly")
        self.skill_level_combobox.current(0)  # Default to the first entry
        self.skill_level_entry = ttk.Entry(main_frame)

        self.search_button = ttk.Button(main_frame, text="Generate Content", command=self.generate_content)
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR,
                                                      bg=ENTRY_BG)

        # Layout widgets
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.skill_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.skill_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.skill_level_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.skill_level_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.search_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.results_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Button to generate quiz
        self.quiz_button = ttk.Button(main_frame, text="Generate Quiz", command=self.generate_quiz_window)
        self.quiz_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # Remember to update methods that use the skill level to retrieve the value from the Combobox
    def generate_content(self):
        topic = self.search_entry.get()
        specific_skill = self.skill_entry.get()
        skill_level = self.skill_level_combobox.get()  # Update this line to use the Combobox's value
    def generate_article_with_mistral(self, topic):
        prompt = f"Generate an in-depth article about {topic}."
        data = {"model": "mistral", "prompt": prompt}
        return self.post_request_to_mistral(data)

    def generate_text_with_mistral(self, topic, specific_skill, skill_level):
        # Prompt for module-based content
        prompt = f"""Create a self-paced online course titled "Introduction to {topic}" structured into multiple modules, each focusing on a key aspect of {specific_skill}. 
    \
        """
        data = {"model": "mistral", "prompt": prompt}
        response = requests.post(MISTRAL_API_URL, json=data)
        if response.status_code == 200:
            try:
                response_lines = response.content.decode('utf-8').strip().split('\n')
                generated_text = ' '.join(
                    item.get('response', '') for item in (json.loads(line) for line in response_lines))
                return generated_text
            except Exception as e:
                return f"Error parsing Mistral API response: {str(e)}"
        else:
            return f"Error generating text with Mistral API. Status code: {response.status_code}"

    def generate_quiz(self, topic, specific_skill):
        prompt = f"make me a quiz about {topic} focusing on {specific_skill} with 5 multiple-choice questions, each having 4 options., put the answers at the buttom of all 5 questions"
        data = {"model": "mistral", "prompt": prompt}
        return self.post_request_to_mistral(data)

    def post_request_to_mistral(self, data):
        response = requests.post(MISTRAL_API_URL, json=data)
        if response.status_code == 200:
            try:
                response_lines = response.content.decode('utf-8').strip().split('\n')
                generated_text = ' '.join(
                    item.get('response', '') for item in (json.loads(line) for line in response_lines))
                return generated_text
            except Exception as e:
                return f"Error parsing Mistral API response: {str(e)}"
        else:
            return f"Error with Mistral API. Status code: {response.status_code}"

    def generate_content(self):
        topic = self.search_entry.get()
        specific_skill = self.skill_entry.get()
        skill_level = self.skill_level_entry.get()

        generated_content = self.generate_text_with_mistral(topic, specific_skill, skill_level)
        if generated_content:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Generated Content:\n" + generated_content)
        else:
            messagebox.showwarning("No Results", "No content generated for the given query.")
        return specific_skill

    def generate_quiz_window(self):
        topic = self.search_entry.get()
        specific_skill = self.skill_entry.get()
        quiz_text = self.generate_quiz(topic, specific_skill)

        if quiz_text:
            quiz_window = tk.Toplevel(self.master)
            quiz_window.title("Generated Quiz")
            quiz_window.configure(bg=BACKGROUND_COLOR)

            # Set up scrolling
            canvas = tk.Canvas(quiz_window, bg=BACKGROUND_COLOR)
            scrollbar = tk.Scrollbar(quiz_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            # Configure canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            # Pack scrollbar and canvas, then create a window for the scrollable frame
            scrollbar.pack(side="right", fill="y")
            canvas.pack(fill="both", expand=True)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            self.var_list = []  # To keep track of variables for radio buttons
            self.correct_answers = []  # To store correct answers

            questions = quiz_text.strip().split("\n\n")

            for question_block in questions:
                lines = question_block.split('\n')
                question = lines[0]
                options = lines[1:-2]

                ttk.Label(scrollable_frame, text=question, background=BACKGROUND_COLOR, foreground=TEXT_COLOR,
                          font=FONT).pack(padx=10, pady=5)

                var = tk.StringVar()
                self.var_list.append(var)

                for option in options:
                    ttk.Radiobutton(scrollable_frame, text=option.strip(), variable=var, value=option.strip(),
                                    style="TRadiobutton").pack(anchor='w')

                answer_line = lines[-2]
                correct_answer = answer_line.split('** Answer:**')[-1].strip()
                self.correct_answers.append(correct_answer)

            ttk.Button(scrollable_frame, text="Submit Answers", command=lambda: self.check_answers(quiz_window)).pack(
                pady=20)

    def check_answers(self, quiz_window):
        score = 0
        for var, correct_answer in zip(self.var_list, self.correct_answers):
            if var.get() == correct_answer:
                score += 1

        result_message = f"Your score: {score}/{len(self.correct_answers)}"
        messagebox.showinfo("Quiz Results", result_message, parent=quiz_window)

        # Optionally, display which questions were answered correctly/incorrectly
        for i, (var, correct_answer) in enumerate(zip(self.var_list, self.correct_answers), start=1):
            if var.get() == correct_answer:
                print(f"Question {i}: Correct")
            else:
                print(f"Question {i}: Incorrect")

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

