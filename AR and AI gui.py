import tkinter as tk
from tkinter import scrolledtext, messagebox
import webbrowser
import requests
import os
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import arxiv
import wikipedia

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

        # Widgets for AR Learning Content Generator
        self.query_label = tk.Label(master, text="Enter a topic to generate a course plan:")
        self.query_entry = tk.Entry(master)
        self.generate_button = tk.Button(master, text="Generate Learning Content",
                                         command=self.generate_learning_content)
        self.course_plan_label = tk.Label(master, text="Learning Content:")
        self.course_plan_output = scrolledtext.ScrolledText(master, width=60, height=10, wrap=tk.WORD)

        # Widgets for Sketchfab Model Viewer
        self.search_label = tk.Label(master, text="Search for a free 3D model:")
        self.search_entry = tk.Entry(master)
        self.search_button = tk.Button(master, text="Search", command=self.search_free_models)
        self.results_text = scrolledtext.ScrolledText(master, width=60, height=10, wrap=tk.WORD)

        # Layout widgets for AR Learning Content Generator
        self.query_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.query_entry.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.generate_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.course_plan_label.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.course_plan_output.grid(row=3, column=0, padx=10, pady=5, columnspan=2, sticky="nsew")

        # Layout widgets for Sketchfab Model Viewer
        self.search_label.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.search_entry.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        self.search_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.results_text.grid(row=6, column=0, padx=10, pady=5, columnspan=2, sticky="nsew")

    def fetch_arxiv_content(self, query):
        search = arxiv.Search(
            query=query,
            max_results=1,
            sort_by=arxiv.SortCriterion.Relevance
        )

        for result in search.results():
            return result.summary

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

    def generate_text_with_gpt2(self, prompt, max_length=200, num_return_sequences=1):
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model = GPT2LMHeadModel.from_pretrained("gpt2")

        input_ids = tokenizer.encode(prompt, return_tensors="pt")

        output = model.generate(
            input_ids=input_ids,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            pad_token_id=tokenizer.eos_token_id,
            bos_token_id=tokenizer.bos_token_id,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=1.0,
            num_beams=1,
            early_stopping=True
        )

        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

        return generated_text

    def generate_learning_content(self):
        query = self.query_entry.get()

        # Fetch content from arXiv
        arxiv_content = self.fetch_arxiv_content(query)

        # Fetch content from Wikipedia
        wikipedia_content = self.fetch_wikipedia_content(query)

        if arxiv_content:
            self.course_plan_output.delete("1.0", tk.END)
            learning_content = self.generate_text_with_gpt2(arxiv_content[:1000], max_length=500)
            self.course_plan_output.insert(tk.END, "From arXiv:\n" + learning_content + "\n\n")
        else:
            messagebox.showwarning("No Results", "No arXiv content found for the given query.")

        if wikipedia_content:
            self.course_plan_output.insert(tk.END, "From Wikipedia:\n" + wikipedia_content)
        else:
            messagebox.showwarning("No Results", "No Wikipedia content found for the given query.")

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
            self.results_text.delete('1.0', tk.END)
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
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, f"Error: Unable to fetch search results. Status code: {response.status_code}")

    def view_model(self, url):
        webbrowser.open_new(url)

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
