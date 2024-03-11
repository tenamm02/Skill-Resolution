import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import os
import json
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

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
        self.skill_level_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.search_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.results_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        # Button to generate quiz
        self.quiz_button = ttk.Button(main_frame, text="Generate Quiz", command=self.generate_quiz_window)
        self.quiz_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def generate_article_with_mistral(self, topic):
        prompt = f"Generate an in-depth article about {topic}."
        data = {"model": "mistral", "prompt": prompt}
        return self.post_request_to_mistral(data)

    def generate_text_with_mistral(self, topic, specific_skill, skill_level):
        # Updated prompt to include detailed course structure and elements
        prompt = f"""Create a comprehensive, self-paced online course titled "The Ultimate {topic} Journey". This course should be structured into multiple modules, each focusing on a key aspect of {topic}. Begin with a captivating introduction that outlines the course objectives and how users will benefit from it. Each module should include:

    - A clear explanation of the module's topic, with text and multimedia content such as images, infographics, and videos.
    - Interactive elements like quizzes at the end of each section to reinforce learning.
    - Practical exercises and hands-on projects that users can complete to apply what they've learned.
    - Gamification features, such as awarding stars for module completion and points for exercise submissions.
    - A progress tracker that visually displays the user's progress through the course and the stars earned.
    - A conclusion that summarizes the key takeaways and encourages further exploration.

    Ensure the content is adaptive, providing simpler explanations and foundational tasks for beginners, and more complex challenges and in-depth discussions for advanced users. Incorporate real-world examples and case studies to illustrate practical applications of {topic}. The course should engage users, keeping them motivated with a mix of challenging, informative, and entertaining content tailored for {skill_level} skill level."""

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

    def generate_quiz(self, topic):
        prompt = f"Generate a quiz for {topic} with 5 multiple-choice questions, each having 4 options."
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

    def generate_quiz_window(self):
        topic = self.search_entry.get()
        quiz_text = self.generate_quiz(topic)

        if quiz_text:
            quiz_window = tk.Toplevel(self.master)
            quiz_window.title("Generated Quiz")
            quiz_window.geometry("600x400")
            quiz_window.configure(bg=BACKGROUND_COLOR)

            quiz_textbox = scrolledtext.ScrolledText(quiz_window, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR, bg=ENTRY_BG)
            quiz_textbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            quiz_textbox.insert(tk.END, "Generated Quiz:\n\n")

            # Split quiz text into individual questions
            questions = quiz_text.strip().split("\n\n")
            for i, question in enumerate(questions, start=1):
                quiz_textbox.insert(tk.END, f"Question {i}:\n")
                quiz_textbox.insert(tk.END, question + "\n\n")
        else:
            messagebox.showwarning("No Results", "No quiz generated for the given topic.")


def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

