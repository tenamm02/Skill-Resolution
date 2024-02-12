# -*- coding: utf-8 -*-
"""GPT2WIKIPULL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZzJUNNivdrIOysP-uF59-cgrkNbEhlXf
"""



import requests

def fetch_wikipedia_content(query):
    """
    Fetches the summary of a Wikipedia page for a given query.

    Parameters:
    - query: The search term to query Wikipedia for.

    Returns:
    A string containing the summary of the Wikipedia page.
    """
    URL = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        print(data)
        return data['extract']
    else:
        return "Could not fetch data from Wikipedia."

from transformers import pipeline, set_seed


def analyze_with_gpt2(content):
    """
    Uses GPT-2 to generate a course plan with structured content and questions.

    Parameters:
    - content: The content fetched from Wikipedia.

    Returns:
    A string containing a structured course plan generated by GPT-2.
    """
    generator = pipeline('text-generation', model='gpt2')
    set_seed(42)

    # Split content into sections
    sections = content.split('\n\n')

    # Initialize the course plan
    course_plan = ""

    # Iterate over sections and add structured content
    for section in sections:
        # Generate a heading for the section
        course_plan += f"\n\n## {section[:50]}"  # Limit heading length to 50 characters

        # Generate questions related to the section
        questions = generator(f"What are some questions related to {section[:50]}?", max_length=100,
                              num_return_sequences=3)
        course_plan += "\n\n### Questions:"
        for q in questions:
            course_plan += f"\n- {q['generated_text'].strip()}"

        # Generate a brief summary of the section
        summary = generator(f"Summarize the section: {section[:50]}", max_length=200, num_return_sequences=1)
        course_plan += f"\n\n### Summary:\n{summary[0]['generated_text']}"

    return course_plan

def main():
    query = input("Enter a topic to generate a course plan: ")
    wiki_content = fetch_wikipedia_content(query)
    print("\nFetching Wikipedia content... Done.\n")

    print("Generating course plan using GPT-2...\n")
    course_plan = analyze_with_gpt2(wiki_content[:1000])  # We limit the content to avoid overwhelming GPT-2
    print(course_plan)

if __name__ == "__main__":
    main()
