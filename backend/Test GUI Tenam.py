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
import sqlite3

def setup_database():
    conn = sqlite3.connect('learning_content.db')
    cursor = conn.cursor()
    # Create tables for topics, course contents, and quizzes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY,
        topic TEXT NOT NULL,
        skill TEXT,
        skill_level TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS course_contents (
        id INTEGER PRIMARY KEY,
        topic_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY(topic_id) REFERENCES topics(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY,
        content_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        distractors TEXT NOT NULL,
        FOREIGN KEY(content_id) REFERENCES course_contents(id)
    )
    ''')
    conn.commit()
    conn.close()

def insert_topic(topic, skill, skill_level):
    conn = sqlite3.connect('learning_content.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO topics (topic, skill, skill_level) VALUES (?, ?, ?)', (topic, skill, skill_level))
    topic_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return topic_id

def insert_content(topic_id, content):
    conn = sqlite3.connect('learning_content.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO course_contents (topic_id, content) VALUES (?, ?)', (topic_id, content))
    content_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return content_id

def insert_quiz(content_id, question, correct_answer, distractors):
    conn = sqlite3.connect('learning_content.db')
    cursor = conn.cursor()
    distractors_text = json.dumps(distractors)  # Convert list to JSON string for storage
    cursor.execute('INSERT INTO quizzes (content_id, question, correct_answer, distractors) VALUES (?, ?, ?, ?)',
                   (content_id, question, correct_answer, distractors_text))
    conn.commit()
    conn.close()

def fetch_quizzes(content_id):
    conn = sqlite3.connect('learning_content.db')
    cursor = conn.cursor()
    cursor.execute('SELECT question, correct_answer, distractors FROM quizzes WHERE content_id = ?', (content_id,))
    quizzes = [{'question': row[0], 'correct_answer': row[1], 'distractors': json.loads(row[2])} for row in cursor.fetchall()]
    conn.close()
    return quizzes

def search_similar_topics(topic, skill, skill_level):
    conn = sqlite3.connect('learning_content.db')
    cursor = conn.cursor()
    # Using simple LIKE query for demonstration; adapt as needed for more sophistication
    query = """
    SELECT id, topic, skill, skill_level FROM topics
    WHERE topic LIKE ? OR skill LIKE ? OR skill_level LIKE ?
    """
    cursor.execute(query, (f'%{topic}%', f'%{skill}%', f'%{skill_level}%'))
    results = cursor.fetchall()
    conn.close()
    return results


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

def create_distractor(correct_answer):
    # This is a placeholder. Implement your logic to create a plausible distractor.
    return "Distractor"

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
        self.structured_quiz = [
            {"question": "What is the primary purpose of HTML?",
             "options": ["Structure web content", "Style web pages", "Interactivity", "Data storage"],
             "correct_answer": "Structure web content"},
            # Additional questions...
        ]

        self.quiz_frame = ttk.Frame(master)  # Create a frame for quiz elements
        self.quiz_frame.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=10,
                             pady=5)  # Adjust grid positioning as needed

    def generate_article_with_mistral(self, topic):
        prompt = f"Generate an in-depth article about {topic}."
        data = {"model": "mistral", "prompt": prompt}
        return self.post_request_to_mistral(data)

    def generate_quiz_with_mistral(self, topic):
        prompt = f"Generate a quiz for {topic} with 5 multiple-choice questions, each having 4 options."
        data = {"model": "mistral", "prompt": prompt}
        return self.post_request_to_mistral(data)
        pass

    def process_quiz_text_to_structure(self, raw_text):
        """
        Processes raw quiz text from Mistral to a structured format.
        """
        # Implementation as previously discussed
        quizzes = [

        ]
        return quizzes

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

    def display_quiz_button(self):
        self.quiz_button = ttk.Button(self.master, text="Generate Quiz", command=self.generate_and_display_quiz)
        self.quiz_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def generate_and_display_quiz(self):
        self.display_quiz()

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

    def display_article(self):
        topic = self.search_entry.get()
        article_content = self.generate_article_with_mistral(topic)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "Generated Article:\n" + article_content)

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

    def generate_quiz_based_on_content(self, content):
        key_sentences = extract_key_sentences(content)
        self.structured_quiz = []
        for sentence in key_sentences:
            question = f"What is described by: '{sentence}'?"
            correct_answer = sentence
            distractors = [create_distractor(correct_answer) for _ in range(3)]
            options = distractors + [correct_answer]
            random.shuffle(options)
            self.structured_quiz.append({
                "question": question,
                "options": options,
                "correct_answer": correct_answer
            })

    def generate_content(self):
        topic = self.search_entry.get()
        specific_skill = self.skill_entry.get()
        skill_level = self.skill_level_entry.get()
        generated_content = self.generate_text_with_mistral(topic, specific_skill, skill_level)
        generated_content = self.generate_text_with_mistral(self.search_entry.get(), self.skill_entry.get(),
                                                            self.skill_level_entry.get())
        if generated_content:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Generated Content:\n" + generated_content)
            self.display_quiz_button()
            self.generate_quiz_based_on_content(generated_content)  # Call this to generate the quiz

        # Search for similar topics
        similar_topics = search_similar_topics(topic, specific_skill, skill_level)

        if similar_topics:
            # If similar topics exist, choose how to use them. This is a simplified example.
            # You could fetch the content associated with these topics and display it,
            # or compare the content's similarity more thoroughly before deciding.
            messagebox.showinfo("Similar Content Found", "Similar content already exists in the database.")
            # Fetch and display the first similar topic's content for demonstration
            content_id = similar_topics[0][0]  # Assuming the first column is the ID
            quizzes = fetch_quizzes(content_id)  # Assuming quizzes are related to content
            # Display quizzes or content as needed
        else:
            messagebox.showwarning("No Results", "No content generated for the given query.")
            # No similar content found, proceed to generate new content
            topic_id = insert_topic(topic, specific_skill, skill_level)
            generated_content = self.generate_text_with_mistral(topic, specific_skill, skill_level)
            if generated_content:
                content_id = insert_content(topic_id, generated_content)
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, "Generated Content:\n" + generated_content)
                self.display_quiz_button()
                self.generate_quiz_based_on_content(generated_content, content_id)  # Pass content_id to link quizzes
            else:
                messagebox.showwarning("No Results", "No content generated for the given query.")


def main():
    setup_database()  # Ensure the database is set up
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
