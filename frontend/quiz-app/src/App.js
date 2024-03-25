import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [courseContent, setCourseContent] = useState(null);

  const handleQuizGeneration = async () => {
    try {
      const response = await axios.post('http://localhost:5000/generate-quiz', {
        topic: topic
      });
      setQuiz(response.data.quiz);
    } catch (error) {
      console.error('Error generating quiz:', error);
    }
  };

  const handleCourseGeneration = async () => {
    try {
      const response = await axios.post('http://localhost:5000/generate-course', {
        subject: subject,
        topics: topic,
        difficulty: difficulty
      });
      setCourseContent(response.data.courseContent);
    } catch (error) {
      console.error('Error generating course:', error);
    }
  };

  return (
    <div>
      <h1>Mistral Course and Quiz Generator</h1>
      <div>
        <input type="text" placeholder="Subject" value={subject} onChange={e => setSubject(e.target.value)} />
        <input type="text" placeholder="Topic" value={topic} onChange={e => setTopic(e.target.value)} />
        <input type="text" placeholder="Difficulty" value={difficulty} onChange={e => setDifficulty(e.target.value)} />
        <button onClick={handleCourseGeneration}>Generate Course</button>
        <button onClick={handleQuizGeneration}>Generate Quiz</button>
      </div>
      {quiz && (
        <div>
          <h2>Generated Quiz</h2>
          <p>{JSON.stringify(quiz)}</p>
        </div>
      )}
      {courseContent && (
        <div>
          <h2>Generated Course</h2>
          <p>{JSON.stringify(courseContent)}</p>
        </div>
      )}
    </div>
  );
}

export default App;
