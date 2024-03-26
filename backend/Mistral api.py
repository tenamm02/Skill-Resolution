import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import os
import json
import nltk
from nltk.tokenize import sent_tokenize
import subprocess
import webbrowser
import sqlite3
# Define the path to the script you want to run
script_path = 'Quiz parser (1).py'

# Run the script
os.environ['SKETCHFAB_API_TOKEN'] = '0e57c8a592a44347b8c9cf9cbee7bc5a'
nltk.download('punkt')

def list_strip(lst):
    return [item.strip() for item in lst]

def setup_database():
    conn = sqlite3.connect('generated_content.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            specific_skill TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()
setup_database()
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


def post_request_to_mistral(data):
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


def generate_quiz(topic, specific_skill):
    prompt = f"make me a quiz about {topic} focusing on {specific_skill} with 5 multiple-choice questions, each having 4 options., put the answers at the buttom of all 5 questions"
    data = {"model": "mistral", "prompt": prompt}
    return post_request_to_mistral(data)


def generate_text_with_mistral(topic, specific_skill, skill_level):
    # Prompt for module-based content
    prompt = prompt = f"""
As a virtual mentor, I'm here to guide you through the fascinating world of {topic}. Today, we'll dive into the essentials of {specific_skill}, a crucial aspect of {topic} that offers a range of possibilities and applications. 

1. **Introduction to {specific_skill}**: Let's start with a broad overview. What is {specific_skill}, and why is it important in the context of {topic}? We'll explore its significance and the fundamental concepts that underpin {specific_skill}.

2. **Key Concepts and Principles**: Understanding the building blocks of {specific_skill} is essential. I'll break down the core concepts for you, using clear explanations and relatable examples to make sure you grasp the basics.

3. **Practical Applications**: Knowing how to apply {specific_skill} in real-world scenarios is where things get exciting. I'll introduce you to some common applications of {specific_skill} within {topic}, showing you how it's used to solve problems, enhance projects, or create new opportunities.

4. **Interactive Exercise**: Let's put theory into practice. I'll guide you through a simple exercise designed to give you hands-on experience with {specific_skill}. This activity will help solidify your understanding and give you a taste of what you can achieve.

5. **Further Exploration**: Now that you've got the basics down, where can you go from here? I'll point you towards additional resources and advanced topics in {specific_skill} for those eager to learn more and take their skills to the next level.

Ready to get started? Let's embark on this educational journey together and unlock the potential of {specific_skill} in the vast landscape of {topic}.
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


def generate_article_with_mistral(topic):
    prompt = f"Generate an in-depth article about {topic}."
    data = {"model": "mistral", "prompt": prompt}
    return post_request_to_mistral(data)

class MistralAPI:

    # ...

    @staticmethod
    def get_from_database(topic, specific_skill):
        conn = sqlite3.connect('generated_content.db')
        cursor = conn.cursor()
        query = '''
            SELECT * FROM generated_content
            WHERE topic = ? AND specific_skill = ?
        '''
        cursor.execute(query, (topic, specific_skill))
        content = cursor.fetchone()
        conn.close()
        if content:
            return content[3]
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
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=FONT, fg=TEXT_COLOR,
                                                      bg=ENTRY_BG)
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
        self.AR_Button_button = ttk.Button(main_frame, text="Generate AR", command=self.search_free_models)

        self.skill_levels = ["Beginning", "Intermediate", "Expert"]
        self.skill_level_combobox = ttk.Combobox(main_frame, values=self.skill_levels, state="readonly")
        self.skill_level_combobox.current(0)  # Default to the first entry

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
        self.AR_Button_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        # Button to generate quiz
        self.quiz_button = ttk.Button(main_frame, text="Generate Quiz", command=self.generate_quiz_window)
        self.quiz_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # Remember to update methods that use the skill level to retrieve the value from the Combobox
    def generate_content(self):
        topic = self.search_entry.get()
        specific_skill = self.skill_entry.get()
        skill_level = self.skill_level_combobox.get()  # Update this line to use the Combobox's value

        generated_content = MistralAPI.get_from_database(topic, specific_skill)
        if generated_content:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Generated Content:\n" + generated_content)
        else:
            generated_content = generate_text_with_mistral(topic,specific_skill,skill_level)
            if generated_content:

                content = generated_content
                self.results_text.delete("1.0",tk.END)
                self.results_text.insert(tk.END,"Generated Content:\n" + generated_content)
                self.save_to_database(topic,specific_skill,content)
            
            messagebox.showwarning("No Results", "No content generated for the given query.")

    def save_to_database(self, topic, specific_skill,content):
        conn = sqlite3.connect('generated_content.db')
        cursor = conn.cursor()

        query = '''
            INSERT INTO generated_content (topic, specific_skill, content)
            VALUES (?, ?, ?)
        '''
        cursor.execute(query, (topic, specific_skill, content))
        conn.commit()
        conn.close()
    def generate_quiz_window(self):
        topic = self.search_entry.get()
        specific_skill = self.skill_entry.get()
        quiz_text = generate_quiz(topic, specific_skill)
        print(quiz_text)
        with open("Testdoc.txt", "w") as file:
            file.write(quiz_text)
        file.close()
        subprocess.run(['python', script_path])
    def submit_quiz(self, quiz_text):
        # Implement submission of the quiz
        pass

    def search_free_models(self):
        query = self.search_entry.get()

        # Define Sketchfab API endpoint
        api_endpoint = 'https://api.sketchfab.com/v3/search'

        # Set up request parameters
        params = {
            'type': 'models',
            'q': query,
            'price': 'free',
            'token': os.environ['SKETCHFAB_API_TOKEN']
        }

        # Send GET request to Sketchfab API
        response = requests.get(api_endpoint, params=params)

        # Check if request was successful
        if response.status_code == 200:
            # Clear previous search results
            self.results_text.delete("1.0", tk.END)

            self.results_text.insert(tk.END, "\n\nFree 3D Models from Sketchfab:\n")
            for result in response.json()['results']:
                # Insert model information
                self.results_text.insert(tk.END, f"Name: {result['name']}\n")
                self.results_text.insert(tk.END, f"URL: {result['viewerUrl']}\n")
                self.results_text.insert(tk.END, f"Description: {result['description']}\n\n")

                # Add a button to view the model
                # It's tricky to manage lambda functions in loops due to variable scoping issues.
                # Make sure the lambda captures the current URL value correctly.
                view_button = tk.Button(self.results_text, text="View Model",
                                        command=lambda url=result['viewerUrl']: self.view_model(url))
                self.results_text.window_create(tk.END, window=view_button)
                self.results_text.insert(tk.END, "\n")
        else:
            # Display error message if request was unsuccessful
            self.results_text.insert(tk.END,
                                     f"\n\nError: Unable to fetch search results from Sketchfab. Status code: {response.status_code}")

    def view_model(self, url):
        webbrowser.open_new(url)
def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()


