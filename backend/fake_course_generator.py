import json

def generate_fake_course():
    fake_course = {
        "course_title": "Introduction to Augmented Reality",
        "course_description": "A comprehensive introduction to the fundamentals of Augmented Reality.",
        "modules": []
    }

    for module_number in range(1, 4):  # Let's assume 3 modules for this fake course
        module = {
            "module_title": f"Module {module_number}",
            "module_description": f"This is a placeholder description for Module {module_number}.",
            "lessons": []
        }

        for lesson_number in range(1, 4):  # Each module has 3 lessons
            lesson = {
                "lesson_title": f"Lesson {lesson_number}",
                "lesson_content": f"This is placeholder text for the content of Lesson {lesson_number} in Module {module_number}.",
                "multimedia": f"http://example.com/media/module{module_number}_lesson{lesson_number}.mp4",
                "ar_activity": f"http://example.com/ar/module{module_number}_lesson{lesson_number}.html"
            }
            module["lessons"].append(lesson)
        
        fake_course["modules"].append(module)

    return json.dumps(fake_course, indent=4)

fake_course_json = generate_fake_course()
print(fake_course_json)
