import tkinter as tk
from tkinter import scrolledtext, messagebox
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import arxiv
import wikipedia


class AugmentedRealityApp:
    def __init__(self, master):
        self.master = master
        master.title("AR Learning Content Generator")
        master.state('zoomed')  # Maximize the window

        # Configure the grid to expand and fill the space
        master.grid_columnconfigure(0, weight=1)
        for i in range(8):  # Adjust the range as needed
            master.grid_rowconfigure(i, weight=1)

        self.chat_text = scrolledtext.ScrolledText(master, width=60, height=10, wrap=tk.WORD)
        self.query_label = tk.Label(master, text="Enter a topic to generate a course plan:")
        self.query_entry = tk.Entry(master)
        self.generate_button = tk.Button(master, text="Generate Learning Content",
                                         command=self.generate_learning_content)
        self.course_plan_label = tk.Label(master, text="Learning Content:")
        self.course_plan_output = scrolledtext.ScrolledText(master, width=60, height=10, wrap=tk.WORD)

        # Layout widgets
        self.chat_text.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")
        self.query_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.query_entry.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.generate_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.course_plan_label.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.course_plan_output.grid(row=4, column=0, padx=10, pady=5, columnspan=2, sticky="nsew")

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


def main():
    root = tk.Tk()
    app = AugmentedRealityApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
