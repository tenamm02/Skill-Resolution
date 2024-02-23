import json
import requests

url = 'http://localhost:11434/api/generate'
data = {
    "model": "mistral",
    "prompt": "Here is a story about llamas eating grass"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("Generated Story:")
    # Split the response by newline character and iterate over each line
    for line in response.content.decode('utf-8').split('\n'):
        # Skip empty lines
        if line.strip():
            try:
                # Parse the JSON from the line
                response_json = json.loads(line)
                # Extract and print the generated story
                story = response_json.get('response')
                if story:
                    print(story)
            except json.JSONDecodeError as e:
                print("Unable to parse JSON:", e)
else:
    print("Error:", response.status_code)
