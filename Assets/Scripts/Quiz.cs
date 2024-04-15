using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class Quiz : MonoBehaviour
{
    public GameObject canvas;
    public TextMeshProUGUI quizBoardText;
    public InputField subjectInputField; // Assign this in the Inspector
    public InputField topicsInputField; // Assign this in the Inspector
    public Button nextButton; // Assign in Inspector
    public Button previousButton; // Assign in Inspector
    public Button submitButton; // Assign in Inspector
    public Transform optionsContainer; // Parent GameObject where option buttons/toggles will be instantiated
    public GameObject prefabOptionButton; // Assign this in the Unity Inspector
    
    
    [System.Serializable]
    public class QuestionItem
    {
        public string question;
        public List<string> options;
        public int correctAnswerIndex; // Assuming answer is an index
        public int selectedAnswerIndex = -1; // Default to -1, meaning no selection
    }

    [System.Serializable]
    public class QuizContent
    {
        public List<QuestionItem> questions;
    }

    public QuizContent quizContent;
    public int currentQuestionIndex = 0;

    public class CertificateBypass : CertificateHandler
    {
        protected override bool ValidateCertificate(byte[] certificateData)
        {
            // Always accept
            return true;
        }
    }

    void Awake()
    {
        // Set the security protocol
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12; // Default to TLS 1.2
#if NETCOREAPP3_0_OR_GREATER || NET5_0_OR_GREATER
        ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls13; // Add TLS 1.3 if available
#endif

        // Certificate validation bypass
        ServicePointManager.ServerCertificateValidationCallback += (sender, cert, chain, error) =>
        {
            Debug.Log($"ServerCertificateValidationCallback: {error}");
            return true; // Forcefully accept all certificates
        };

        // Add listeners to buttons
        nextButton.onClick.AddListener(GoToNextQuestion);
        previousButton.onClick.AddListener(GoToPreviousQuestion);
        submitButton.onClick.AddListener(SubmitQuiz);
    }

    public void StartFetchingQuizContent()
    {
        StartCoroutine(FetchAndUpdateQuizBoard());
        Debug.Log("Starting to fetch and update quiz data...");
        canvas.SetActive(true); // Make sure the canvas is visible when updating
    }

    IEnumerator FetchAndUpdateQuizBoard()
{
    string subject = subjectInputField.text;
    string[] topicsArray = topicsInputField.text.Split(',').Select(t => t.Trim()).Where(t => !string.IsNullOrEmpty(t)).ToArray();
    string jsonData = $"{{\"subject\":\"{subject}\", \"topics\":\"{string.Join(",", topicsArray)}\"}}";

    string url = "https://192.168.1.186:8000/generate-quiz";
    Debug.Log($"Sending request to {url} with data: {jsonData}");

    using (UnityWebRequest www = UnityWebRequest.PostWwwForm(url, UnityWebRequest.kHttpVerbPOST))
    {
        byte[] jsonToSend = Encoding.UTF8.GetBytes(jsonData);
        www.uploadHandler = new UploadHandlerRaw(jsonToSend);
        www.downloadHandler = new DownloadHandlerBuffer();
        www.SetRequestHeader("Content-Type", "application/json");
        www.certificateHandler = new CertificateBypass();

        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            string receivedData = www.downloadHandler.text;
            Debug.Log("Received quiz data: " + receivedData);
            ParseAndDisplayQuiz(receivedData);
        }
        else
        {
            Debug.LogError("Error fetching quiz data: " + www.error);
        }
    }
}

void ParseAndDisplayQuiz(string text)
{
    string[] questionBlocks = text.Split(new string[] { "Question:" }, StringSplitOptions.RemoveEmptyEntries);
    List<QuestionItem> questions = new List<QuestionItem>();

    foreach (string block in questionBlocks)
    {
        if (string.IsNullOrWhiteSpace(block))
            continue;

        string[] parts = block.Split(new string[] { "An swer:" }, StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length < 2)
            continue;

        string questionPart = parts[0].Trim();
        string answerPart = parts[1].Trim();

        // Split the question part further to extract options
        string questionText = questionPart.Split(new[] { 'A' })[0].Trim();
        List<string> options = new List<string>
        {
            questionPart.Split(new[] { 'A' })[1].Split('B')[0].Trim(),
            questionPart.Split(new[] { 'B' })[1].Split('C')[0].Trim(),
            questionPart.Split(new[] { 'C' })[1].Split('D')[0].Trim(),
            questionPart.Split(new[] { 'D' })[1].Trim()
        };

        int correctAnswerIndex = answerPart[0] - 'A';

        questions.Add(new QuestionItem
        {
            question = questionText,
            options = options,
            correctAnswerIndex = correctAnswerIndex,
            selectedAnswerIndex = -1  // Default to -1, indicating no selection
        });
    }

    quizContent = new QuizContent { questions = questions };
    DisplayCurrentQuestion();
}

void DisplayCurrentQuestion()
{
    if (currentQuestionIndex >= quizContent.questions.Count)
        return; // Add a safety check

    QuestionItem currentQuestion = quizContent.questions[currentQuestionIndex];
    quizBoardText.text = currentQuestion.question;

    // Clear previous options
    foreach (Transform child in optionsContainer)
    {
        Destroy(child.gameObject);
    }

    // Display new options
    for (int i = 0; i < currentQuestion.options.Count; i++)
    {
        GameObject optionButton = Instantiate(prefabOptionButton, optionsContainer) as GameObject; // Ensure you cast to GameObject
        if (optionButton != null)
        {
            optionButton.GetComponentInChildren<TextMeshProUGUI>().text = currentQuestion.options[i];
            int index = i; // Local copy for use in the lambda capture
            optionButton.GetComponent<Button>().onClick.AddListener(() => SelectAnswer(index));
        }
    }
}


    void SelectAnswer(int optionIndex)
    {
        quizContent.questions[currentQuestionIndex].selectedAnswerIndex = optionIndex;
    }

    void GoToNextQuestion()
    {
        if (currentQuestionIndex < quizContent.questions.Count - 1)
        {
            currentQuestionIndex++;
            DisplayCurrentQuestion();
        }
    }

    void GoToPreviousQuestion()
    {
        if (currentQuestionIndex > 0)
        {
            currentQuestionIndex--;
            DisplayCurrentQuestion();
        }
    }

    void SubmitQuiz()
    {
        int score = 0;
        foreach (var question in quizContent.questions)
        {
            if (question.selectedAnswerIndex == question.correctAnswerIndex)
            {
                score++;
            }
        }
        Debug.Log($"Quiz Completed. Score: {score} out of {quizContent.questions.Count}");
        // Optionally display the score in the UI or handle it according to your game design
    }
}
