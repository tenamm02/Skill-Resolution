import requests
from transformers import pipeline, set_seed

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
        return data['extract']
    else:
        return "Could not fetch data from Wikipedia."

def generate_questions(content):
    """
    Generates questions based on the given content.

    Parameters:
    - content: The content fetched from Wikipedia.

    Returns:
    A list of questions generated from the content.
    """
    question_generator = pipeline('question-generation')
    questions = question_generator(content)
    return [q['question'] for q in questions]

def main():
    query = input("Enter a topic to generate questions: ")
    wiki_content = fetch_wikipedia_content(query)
    print("\nFetching Wikipedia content... Done.\n")

    print("Generating questions...\n")
    questions = generate_questions(wiki_content)
    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")

if __name__ == "__main__":
    main()
