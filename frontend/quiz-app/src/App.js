import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('beginner');
  const [quiz, setQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [courseContent, setCourseContent] = useState(null);


  const handleQuizGeneration = async () => {
    try {
      const response = await axios.post('http://localhost:5000/generate-quiz', {
        subject: subject,
        topics: topic,
        difficulty: difficulty
      });

      setQuiz(formatQuiz(response.data.quiz));
      setCurrentQuestionIndex(0);
      setSelectedAnswers({});
    } catch (error) {
      console.error('Error generating quiz:', error);
    }
  };

  const handleOptionChange = (questionIndex, option) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: option,
    });
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < quiz.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = () => {
    console.log('Selected answers:', selectedAnswers);
    // Logic to handle quiz submission, e.g., validate answers, calculate score
  };

 const formatQuiz = (quizData) => {
    if (!Array.isArray(quizData)) {
      console.error('Quiz data is not in the expected array format.', quizData);
      return [];
    }

    return quizData.map(questionObj => ({
      question: questionObj.question,
      options: questionObj.options.filter(option => option.trim() !== ""), // Filters out any empty string options
      answer: questionObj.answer,
    }));
  };

  function formatCourseContent(rawContent) {
    if (!Array.isArray(rawContent)) {
      console.error('No content to format or content is not in the expected array format');
      return 'No content available or incorrect content format.';
    }

    // Concatenate the 'response' property from each object in the array
    const contentString = rawContent.map(obj => obj.response.trim()).join(' ');

    // Split the content into sections based on the pattern observed in the titles
    const sections = contentString.split(/(?=\*\*[0-9]+\.\s)/).filter(Boolean);

    const formattedSections = sections.map(section => {
      // Find the index where the actual content starts, ignoring the section number
      const startIndex = section.indexOf('**', 2);
      const title = section.substring(0, startIndex).trim();
      const content = section.substring(startIndex).trim();

      // Clean up the content by removing unnecessary spaces
      const cleanedContent = content.replace(/\s+/g, ' ');

      return `${title}\n${cleanedContent}`;
    });

    return formattedSections.join('\n\n');
  }

const handleCourseGeneration = async () => {
    try {
        const response = await axios.post('http://localhost:5000/generate-course', {
            subject,
            topics: topic,
            difficulty
        });

        if (response.data && Array.isArray(response.data.courseContent)) {
            const formattedContent = formatCourseContent(response.data.courseContent);
            setCourseContent(formattedContent);
        } else {
            console.error('No course content received or content is not an array');
            setCourseContent(null);
        }
    } catch (error) {
        console.error('Error generating course:', error);
        setCourseContent(null);
    }
};

  return (
    <div>
      <h1>Mistral Course and Quiz Generator</h1>
      <div>
        <input type="text" placeholder="Subject" value={subject} onChange={e => setSubject(e.target.value)} />
        <input type="text" placeholder="Topic" value={topic} onChange={e => setTopic(e.target.value)} />
        <select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="expert">Expert</option>
        </select>
        <button onClick={handleCourseGeneration}>Generate Course</button>
        <button onClick={handleQuizGeneration}>Generate Quiz</button>
      </div>
      {/* Input fields and buttons */}
      {quiz && quiz.length > 0 && currentQuestionIndex < quiz.length ? (
  <div>
    <h2>Generated Quiz</h2>
    <div key={currentQuestionIndex}>
      {/* Display the question text */}
      <p>{`Question ${currentQuestionIndex + 1}: ${quiz[currentQuestionIndex].question}`}</p>
      {/* Render options in a vertical list */}
      {quiz[currentQuestionIndex].options.map((option, optionIndex) => (
        <div key={optionIndex}>
          <input
            type="radio"
            id={`question_${currentQuestionIndex}_option_${optionIndex}`}
            name={`question_${currentQuestionIndex}`}
            value={option}
            onChange={() => handleOptionChange(currentQuestionIndex, option)}
            checked={selectedAnswers[currentQuestionIndex] === option}
          />
          <label htmlFor={`question_${currentQuestionIndex}_option_${optionIndex}`}>{option}</label>
        </div>
      ))}
      <button disabled={currentQuestionIndex <= 0} onClick={previousQuestion}>Previous</button>
      <button disabled={currentQuestionIndex >= quiz.length - 1} onClick={nextQuestion}>Next</button>
      {currentQuestionIndex === quiz.length - 1 && (
        <button onClick={handleSubmitQuiz}>Submit Quiz</button>
      )}
    </div>
  </div>
) : (
        <div>
          {/* No quiz content message */}
          {/* ... */}
        </div>
      )}
      {courseContent && (
        <div>
          <h2>Generated Course</h2>
          <div dangerouslySetInnerHTML={{ __html: courseContent }} />
        </div>
      )}
    </div>
  );
}

export default App;
