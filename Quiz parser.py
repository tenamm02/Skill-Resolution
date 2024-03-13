# Define a structure to hold the parsed data
questions = []

# Temporary variables to hold information while parsing
current_question = {}
options = []

# Open the file and read line by line
with open("/home/christopherseccafico/Downloads/Testdoc.txt", "r") as file:
    for line in file:
        # Check for the start of a new question
        if line.strip().startswith('Question'):
            # If there's an existing question being processed, save it before starting a new one
            if current_question:
                current_question['options'] = options.copy()
                questions.append(current_question)
            
            # Reset the temporary variables for the new question
            current_question = {'question': line.split(':', 1)[1].strip()}
            options.clear()
        elif line.strip().startswith(('A )', 'B )', 'C )', 'D )')):
            # If the line is an option, add it to the options list
            options.append(line.strip())
        elif line.strip().startswith('An'):
            # If the line indicates an answer, save it to the current question
            current_question['answer'] = line.split(':', 1)[1].strip()

# Don't forget to add the last question to the list
if current_question:
    if 'options' not in current_question:
        current_question['options'] = options.copy()
    questions.append(current_question)

# Display the structured data
for question in questions:
    print(f"Question: {question['question']}")
    for option in question['options']:
        print(option)
    if 'answer' in question:
        print(f"Answer: {question['answer']}\n")
    else:
        print("Answer: N/A\n")

