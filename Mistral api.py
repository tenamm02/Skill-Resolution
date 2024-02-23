import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import os
import json

# Set the Mistral API endpoint
MISTRAL_API_URL = 'http://localhost:11434/api/generate'

# Set the Sketchfab API token as an environment variable
os.environ['SKETCHFAB_API_TOKEN'] = '0e57c8a592a44347b8c9cf9cbee7bc5a'

class ARSketchfabApp:
    def __init__(self, master):
        self.master = master
        master.title("AR Learning Content Generator & Sketchfab Model Viewer")
        master.state('zoomed')  # Maximize the window

        # Configure the grid to expand and fill the space
        master.grid_columnconfigure(0, weight=1)
        for i in range(8):  # Adjust the range as needed
            master.grid_rowconfigure(i, weight=1)

        # Widgets for Search and Learning Content
        self.search_label = tk.Label(master, text="Enter a topic to generate learning content:")
        self.search_entry = tk.Entry(master)
        self.search_button = tk.Button(master, text="Generate Content", command=self.generate_content)
        self.results_text = scrolledtext.ScrolledText(master, width=60, height=20, wrap=tk.WORD)

        # Layout widgets for Search and Learning Content
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.search_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.results_text.grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky="nsew")

    def generate_text_with_mistral(self, prompt):
        data = {
            "model": "mistral",
            "prompt": "generate me a 15 week course plan" + prompt
        }

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

    def generate_content(self):
        query = self.search_entry.get()
        generated_content = self.generate_text_with_mistral(query)

        if generated_content:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Generated Content:\n" + generated_content)
        else:
            messagebox.showwarning("No Results", "No content generated for the given query.")

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
