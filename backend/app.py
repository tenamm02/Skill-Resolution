from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

MISTRAL_API_URL = 'http://localhost:11434/api/generate'

def post_request_to_mistral(data):
    headers = {'Content-Type': 'application/json'}
    url = MISTRAL_API_URL
    try:
        print(f"Sending request to Mistral API with data: {data}")
        response = requests.post(url, json=data, headers=headers)
        print("Response received")
        response.raise_for_status()  # This will throw an exception for HTTP errors

        # Process each line as a separate JSON object
        response_parts = []
        for line in response.iter_lines():
            if line:
                json_line = json.loads(line.decode('utf-8'))
                response_parts.append(json_line)
                if json_line.get('done', False):
                    break

        # Now response_parts contains all the separate JSON objects
        return response_parts

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Mistral API: {str(e)}")
        return {"error": f"Error connecting to Mistral API: {str(e)}"}


def parse_mistral_response(response_parts):
    full_response_text = ''

    for part in response_parts:
        if 'response' in part:
            full_response_text += part['response']

    lines = full_response_text.split('\n')

    questions = []
    current_question = {}
    reading_answers = False

    for line in lines:
        if line.startswith("**Question"):
            if current_question:
                questions.append(current_question)
            # Initialize current_question with 'options' as an empty list
            current_question = {"question": line, "options": [], "answer": ""}
            reading_answers = False
        elif line.startswith("Answer:"):
            current_question["answer"] = line.replace("Answer:", "").strip()
        elif reading_answers or line.startswith("A)") or line.startswith("B)") or line.startswith(
                "C)") or line.startswith("D)"):
            # Ensure 'options' exists before appending to it
            if 'options' not in current_question:
                current_question['options'] = []
            current_question["options"].append(line.strip())
            reading_answers = True
        elif reading_answers and not line.strip():
            reading_answers = False

    if current_question:
        questions.append(current_question)

    return questions


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    if not all(key in data for key in ['subject', 'topics', 'difficulty']):
        return jsonify({"error": "Missing required parameters"}), 400

    prompt = f"make me a quiz about {data['subject']} focusing on {data['topics']} with 5 multiple-choice questions, each having 4 options., put the answers at the bottom of all 5 questions"
    data_payload = {
        "model": "mistral",
        "prompt": prompt
    }

    mistral_response = post_request_to_mistral(data_payload)
    structured_quiz = parse_mistral_response(mistral_response)
    return jsonify({"quiz": structured_quiz})

@app.route('/generate-course', methods=['POST'])
def generate_course():
    course_params = request.json
    if not all(key in course_params for key in ['subject', 'topics', 'difficulty']):
        return jsonify({"error": "Missing required parameters"}), 400

    data = {
        "model": "mistral",
        "prompt": f"Generate a course outline for {course_params['subject']} covering {course_params['topics']} at {course_params['difficulty']} level"
    }

    mistral_response = post_request_to_mistral(data)
    if 'error' in mistral_response:
        return jsonify({"error": mistral_response['error']}), 500

    return jsonify({"courseContent": mistral_response})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Flask is running"})

if __name__ == '__main__':
    app.run(debug=True)
