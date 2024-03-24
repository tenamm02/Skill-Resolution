from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MISTRAL_API_URL = 'https://api.mistral.com/generate'

def post_request_to_mistral(data):
    try:
        response = requests.post(MISTRAL_API_URL, json=data)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        print(response.text)  # Print the full response text
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Mistral API: {str(e)}")
        return f"Error connecting to Mistral API: {str(e)}"

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    mistral_response = post_request_to_mistral(data)
    if isinstance(mistral_response, dict) and 'Error' in mistral_response:
        return jsonify({"error": mistral_response}), 500
    return jsonify({"quiz": mistral_response})

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    quiz_data = request.json
    # Add logic to process and store quiz data
    return jsonify({"status": "success", "message": "Quiz submitted successfully"})

@app.route('/generate-course', methods=['POST'])
def generate_course():
    course_params = request.json
    if not all(key in course_params for key in ['subject', 'topics', 'difficulty']):
        return jsonify({"error": "Missing required parameters"}), 400

    data = {
        "model": "course-generation-model",
        "prompt": f"Generate a course outline for {course_params['subject']} covering {course_params['topics']} at {course_params['difficulty']} level"
    }
    mistral_response = post_request_to_mistral(data)
    if isinstance(mistral_response, dict) and 'Error' in mistral_response:
        return jsonify({"error": mistral_response}), 500
    return jsonify({"courseContent": mistral_response})

if __name__ == '__main__':
    app.run(debug=True)
