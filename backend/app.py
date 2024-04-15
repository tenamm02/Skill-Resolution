from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json
import logging
import sqlite3
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.logger.setLevel('DEBUG')
app.logger.debug("Debug message")

@app.before_request
def log_request():
    data = request.get_data(as_text=True) if request.method != 'GET' else 'No body'
    app.logger.debug(f"Received {request.method} request for {request.url} with body: {data} and headers: {request.headers}")


MISTRAL_API_URL = 'http://localhost:11434/api/generate'

def post_request_to_mistral(data):
    headers = {'Content-Type': 'application/json'}
    url = MISTRAL_API_URL
    try:
        app.logger.debug(f"Sending request to Mistral API with data: {data}")
        response = requests.post(url, json=data, headers=headers)
        app.logger.debug("Response received")
        response.raise_for_status()

        response_parts = []
        for line in response.iter_lines():
            if line:
                json_line = json.loads(line.decode('utf-8'))
                response_parts.append(json_line)
                if json_line.get('done', False):
                    break

        return response_parts

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error connecting to Mistral API: {str(e)}")
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
    import sqlite3
    course_params = request.json

    # Connecting to the database using a context manager
    with sqlite3.connect('quiz_database.db') as conn:
        cursor = conn.cursor()

        # Assuming the database schema supports filtering by specific_skill
        query = '''
                    SELECT question, options, answer FROM questions 
                    WHERE topic = ?
                    LIMIT 5
                '''

        cursor.execute(query, (course_params['subject'],))
        content = cursor.fetchall()

    # Check if content was fetched successfully
    if content:
        formatted_content = []
        for question, options, answer in content:
            print(options)
            formatted_question = f"Question: {question}"
            formatted_options = "\n".join(
                f"{option}" for option in options.split(','))
            # Assuming answer is stored as a number (0, 1, 2, 3) corresponding to the option index
            formatted_answer = f"An swer: {answer}"

            formatted_content.append(f"{formatted_question}\n{formatted_options}\n{formatted_answer}\n")

        return "\n".join(formatted_content)
    else:
        prompt = f"""make me a quiz about {course_params['subject']} focusing on {course_params['topics']} with 5 multiple-choice questions, each having 4 options., put the answers at the buttom of all 5 questions" 

MAKE EACH QUESTION IN THE FOLLOWING FORMAT!!!
Question: 'Which  dog  breed  is  known  for  having  a  distinctive  wr ink led  skin  and  short  legs ?')
A ) Box er

B ) fiber ian  Hus ky

C ) Do ber man  P ins cher

D ) Be agleDog

An swer: A)
"""

        data = {"model": "mistral", "prompt": prompt}
        return post_request_to_mistral(data)

@app.route('/generate-course', methods=['POST'])
def generate_course():
    import sqlite3

    course_params = request.json
    if not all(key in course_params for key in ['subject', 'topics', 'difficulty']):
        return jsonify({"error": "Missing required parameters"}), 400
    topics_json = json.dumps(course_params['topics'])
    conn = sqlite3.connect('generated_content.db')
    cursor = conn.cursor()
    query = '''
                SELECT content FROM generated_content
                WHERE topic = ? AND specific_skill = ?
            '''
    cursor.execute(query, (course_params['subject'], topics_json))
    content = cursor.fetchone()
    conn.close()
    if content:
        print(content)
        return jsonify({"courseContent":content})

    else:
        data = {
            "model": "mistral",
            "prompt": f"Generate a course outline for {course_params['subject']} covering {course_params['topics']} at {course_params['difficulty']} level"
                      f"""
        As a virtual mentor, I'm here to guide you through the fascinating world of {course_params['subject']}. Today, we'll dive into the essentials of {course_params['topics']}, a crucial aspect of {course_params['subject']} that offers a range of possibilities and applications. 

        1. **Introduction to {course_params['subject']}**: Let's start with a broad overview. What is {course_params['topics']}, and why is it important in the context of {course_params['subject']}? We'll explore its significance and the fundamental concepts that underpin {course_params['topics']}.

        2. **Key Concepts and Principles**: Understanding the building blocks of {course_params['topics']} is essential. I'll break down the core concepts for you, using clear explanations and relatable examples to make sure you grasp the basics.

        3. **Practical Applications**: Knowing how to apply {course_params['topics']} in real-world scenarios is where things get exciting. I'll introduce you to some common applications of {course_params['topics']} within {course_params['subject']} showing you how it's used to solve problems, enhance projects, or create new opportunities.

        4. **Interactive Exercise**: Let's put theory into practice. I'll guide you through a simple exercise designed to give you hands-on experience with {course_params['topics']}. This activity will help solidify your understanding and give you a taste of what you can achieve.

        5. **Further Exploration**: Now that you've got the basics down, where can you go from here? I'll point you towards additional resources and advanced topics in  {course_params['topics']} for those eager to learn more and take their skills to the next level.

        Ready to get started? Let's embark on this educational journey together and unlock the potential of {course_params['topics']} in the vast landscape of {course_params['subject']}.
        """
    }

        mistral_response = post_request_to_mistral(data)
        if 'error' in mistral_response:
            return jsonify({"error": mistral_response['error']}), 500

        return jsonify({"courseContent": mistral_response})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Flask is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, ssl_context=('cert.pem', 'key.pem'))

