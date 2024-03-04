import tkinter as tk
from functools import partial
from tkinter import ttk, scrolledtext, messagebox
import requests
import os
import json
import random
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

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

def create_distractors(correct_answer):
    # Generate plausible distractor options based on the correct answer
    distractors = []

    # Example: Replace each word in the correct answer with a synonym
    synonyms = {
        "HTML": ["Hypertext Markup Language", "HyperText", "Markup", "Language"],
        "CSS": ["Cascading Style Sheets", "Style Sheets", "Styling", "Cascading"],
        # Add more synonyms as needed
    }

    for word in correct_answer.split():
        if word in synonyms:
            distractors.extend(synonyms[word])
        else:
            distractors.append(word)

    # Remove the correct answer from distractors
    distractors = [d for d in distractors if d.lower() != correct_answer.lower()]

    # Take 3 random distractors
    return random.sample(distractors, 3)

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
        self.skill_level_entry = ttk.Entry(main_frame)
        self.search_button = ttk.Button(main_frame, text="Generate Content", command=self.generate_content)
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR, bg=ENTRY_BG)

        # Layout widgets
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.skill_label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.skill_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.skill_level_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.skill_level_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.search_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.results_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.user_answers = {}
        self.structured_quiz = []

        self.quiz_frame = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR, bg=ENTRY_BG)
        self.quiz_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    def generate_content_with_mistral(self, topic, specific_skill, skill_level):
        # Prompt Mistral to generate both course content and quiz questions
        prompt = f"Create an online course titled 'The Ultimate {topic} Journey' for {specific_skill} at {skill_level} skill level., I need content as if I asked you to teach me about this topic, NOT as if im the teacher teaching, I need all of the content so give me a large result"
        data = {"model": "mistral", "prompt": prompt}
        return self.post_request_to_mistral(data)

    def generate_text_with_mistral(self, topic, specific_skill, skill_level):
        # Prompt Mistral to generate quiz questions based on the provided parameters
        prompt = f"Generate quiz questions for the topic '{topic}' related to {specific_skill} at {skill_level} level. I would Also like the correct answers at the bottom, underneith all of the answers"
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
        generated_course_content = self.generate_content_with_mistral(topic, specific_skill, skill_level)
        if generated_course_content:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Generated Course Content:\n" + generated_course_content)
            generated_quiz = self.generate_text_with_mistral(topic, specific_skill, skill_level)
            if generated_quiz:
                self.generate_quiz_based_on_content(generated_quiz)  # Call this to generate the quiz
            else:
                messagebox.showwarning("No Results", "No quiz questions generated for the given parameters.")
        else:
            messagebox.showwarning("No Results", "No course content generated for the given parameters.")

    def generate_quiz_based_on_content(self, content):
        # Clear previous quiz
        self.quiz_frame.delete("1.0", tk.END)

        # Display the generated quiz in the quiz frame
        self.quiz_frame.insert(tk.END, "Generated Quiz Questions:\n")
        self.quiz_frame.insert(tk.END, content)

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
