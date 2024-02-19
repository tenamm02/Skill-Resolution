import tkinter as tk
from tkinter import scrolledtext, messagebox
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import wikipedia

class ARSketchfabApp:
    def __init__(self, master):
        self.master = master
        master.title("AR Learning Content Generator & Sketchfab Model Viewer")
        master.state('zoomed')  # Maximize the window

        # Configure the grid to expand and fill the space
        master.grid_columnconfigure(0, weight=1)
        for i in range(8):  # Adjust the range as needed
            master.grid_rowconfigure(i, weight=1)

        self.query_label = tk.Label(master, text="Enter a topic or model name:")
        self.query_entry = tk.Entry(master)
        self.search_button = tk.Button(master, text="Search", command=self.generate_learning_content)
        self.results_text = scrolledtext.ScrolledText(master, width=60, height=10, wrap=tk.WORD)

        self.query_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.query_entry.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
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

    def generate_learning_content(self):
        query = self.query_entry.get()

        # Fetch content from Wikipedia
        wikipedia_content = self.fetch_wikipedia_content(query)

        if wikipedia_content:
            # Define the structure of the learning content
            content_structure = f"""
            How a Course Functions for {query}:
            1. User Onboarding:
                • Users begin by taking the skill assessment and choosing their preferred topics.
            2. Initial Course Delivery:
                • The AI presents the first set of personalized content and AR experiences to the user through the platform interface.
            3. User Interaction:
                • As users interact with the course materials and AR simulations, the system captures their responses and engagement levels.
            4. Adaptive Learning:
                • The AI analyzes the captured data to continuously adjust the difficulty and type of content presented, ensuring the course remains challenging yet achievable.
            5. Continuous Assessment:
                • Throughout the course, users are assessed through quizzes and interactive prompts to measure progress.
            6. Feedback Loop:
                • Users can provide feedback on content and prompts, which the AI uses to refine the course further.
            7. Course Completion:
                Upon finishing the course, users receive a summary of their performance, along with any applicable certifications or badges.
            """

            # Use GPT-2 to generate the learning content based on the structure and Wikipedia content
            generated_content = self.generate_text_with_gpt2(wikipedia_content)

            # Split the generated content into sections based on the headings in the structure
            sections = []
            for heading in content_structure.split("\n\n"):
                if heading.strip():  # Skip empty lines
                    heading_text = heading.split("\n")[0].strip()  # Extract the heading text
                    section_start = generated_content.find(heading_text)
                    if section_start != -1:
                        section_end = generated_content.find("\n\n", section_start + len(heading_text))
                        if section_end != -1:
                            sections.append(generated_content[section_start:section_end].strip())

            # Reorganize the sections according to the structure
            structured_content = "\n\n".join(sections)

            # Display the structured content
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, structured_content)
        else:
            messagebox.showwarning("No Results", "No Wikipedia content found for the given query.")

    def generate_text_with_gpt2(self, prompt):
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model = GPT2LMHeadModel.from_pretrained("gpt2")

        input_ids = tokenizer.encode(prompt, return_tensors="pt")

        output = model.generate(
            input_ids=input_ids,
            max_length=1000,  # Adjust max_length to 1000
            pad_token_id=tokenizer.eos_token_id,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            top_k=50,
            top_p=0.95,
            temperature=1.0,
            do_sample=True,
            num_beams=5,
            early_stopping=True
        )

        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

        return generated_text

def main():
    root = tk.Tk()
    app = ARSketchfabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
