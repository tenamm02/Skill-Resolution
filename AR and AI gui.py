import tkinter as tk
from tkinter import scrolledtext, messagebox
import webbrowser
import requests
import os
import wikipedia
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
        self.search_label = tk.Label(master, text="Enter a topic to search and generate learning content:")
        self.search_entry = tk.Entry(master)
        self.search_button = tk.Button(master, text="Search & Generate", command=self.search_and_generate)
        self.results_text = scrolledtext.ScrolledText(master, width=60, height=20, wrap=tk.WORD)

        # Layout widgets for Search and Learning Content
        self.search_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.search_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.results_text.grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky="nsew")

    def fetch_wikipedia_content(self, query):
        try:
            wikipedia.set_lang("en")  # Set Wikipedia language to English
            content = wikipedia.summary(query, sentences=5)  # Get summary of the topic
            return content
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation error
            return "Wikipedia disambiguation error: " + str(e)
        except wikipedia.exceptions.PageError as e:
            # Handle page not found error
            return "Wikipedia page not found error: " + str(e)
        except Exception as e:
            # Handle other errors
            return "Error fetching Wikipedia content: " + str(e)

    def generate_text_with_mistral(self, prompt):
        data = {
            "model": "mistral",
            "prompt": prompt
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

    def search_and_generate(self):
        query = self.search_entry.get()

        # Fetch content from Wikipedia
        wikipedia_content = self.fetch_wikipedia_content(query)

        if wikipedia_content:
            self.results_text.delete("1.0", tk.END)
            learning_content = self.generate_text_with_mistral(wikipedia_content[:1000])
            self.results_text.insert(tk.END, "Learning Content from Wikipedia:\n" + learning_content + "\n\n")
        else:
            messagebox.showwarning("No Results", "No Wikipedia content found for the given query.")

        # Fetch free 3D models from Sketchfab
        self.search_free_models()

    def search_free_models(self):
        query = self.search_entry.get()

        # Define Sketchfab API endpoint
        api_endpoint = 'https://api.sketchfab.com/v3/search'

        # Set up request parameters
        params = {
            'type': 'models',
            'q': query,
            'price': 'free',  # Filter for free models only
            'token': os.environ['SKETCHFAB_API_TOKEN']
        }

        # Send GET request to Sketchfab API
        response = requests.get(api_endpoint, params=params)

        # Check if request was successful
        if response.status_code == 200:
            # Display search results
            self.results_text.insert(tk.END, "\n\nFree 3D Models from Sketchfab:\n")
            for result in response.json()['results']:
                self.results_text.insert(tk.END, f"Name: {result['name']}\n")
                self.results_text.insert(tk.END, f"URL: {result['viewerUrl']}\n")
                self.results_text.insert(tk.END, f"Description: {result['description']}\n\n")

                # Add a button to view the model
                view_button = tk.Button(self.results_text, text="View Model", command=lambda url=result['viewerUrl']: self.view_model(url))
                self.results_text.window_create(tk.END, window=view_button)
                self.results_text.insert(tk.END, "\n")
        else:
            # Display error message if request was unsuccessful
            self.results_text.insert(tk.END, f"\n\nError: Unable to fetch search results from Sketchfab. Status code: {response.status_code}")

    def view_model(self, url):
        webbrowser.open_new(url)

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
