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


public class ChalkboardUpdater : MonoBehaviour
{
    public InputField subjectInputField; // Assign this in the Inspector
    public InputField topicsInputField; // Assign this in the Inspector
    public TMP_Dropdown difficultyDropdown; // Assign this in the Inspector
    public TextMeshProUGUI chalkboardText; // Assign this in the Inspector
    public GameObject canvas;
    
    [System.Serializable]
    public class CourseContentItem
    {
        public string created_at;
        public bool done;
        public string model;
        public string response;
    }

    [System.Serializable]
    public class CourseContent
    {
        public List<CourseContentItem> courseContent;
    }
    
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
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;  // Default to TLS 1.2
#if NETCOREAPP3_0_OR_GREATER || NET5_0_OR_GREATER
    ServicePointManager.SecurityProtocol |= SecurityProtocolType.Tls13;  // Add TLS 1.3 if available
#endif

        // Certificate validation bypass
        ServicePointManager.ServerCertificateValidationCallback += (sender, cert, chain, error) => {
            Debug.Log($"ServerCertificateValidationCallback: {error}");
            return true;  // Forcefully accept all certificates
        };
    }

    
    private string BuildJsonDataFromInput()
    {
        string subject = subjectInputField.text;
        string[] topicsArray = topicsInputField.text.Split(',').Select(t => t.Trim()).Where(t => !string.IsNullOrEmpty(t)).ToArray();
        string difficulty = difficultyDropdown.options[difficultyDropdown.value].text;

        // Convert topics array to JSON array format
        string topicsJsonArray = "[\"" + string.Join("\", \"", topicsArray) + "\"]";

        // Manually construct the JSON data with user inputs
        return "{\"subject\":\"" + subject + "\", \"topics\":" + topicsJsonArray + ", \"difficulty\":\"" + difficulty + "\"}";

    }
    
    public void StartFetchingCourseContent()
    {
        StartCoroutine(FetchAndUpdateChalkboard(BuildJsonDataFromInput()));
        Debug.Log("Starting to fetch and update chalkboard...");
        canvas.SetActive(false);
    }

    IEnumerator FetchAndUpdateChalkboard(string jsonData)
    {
        string url = "https://192.168.1.186:8000/generate-course";
        Debug.Log($"Sending request to {url} with data: {jsonData}");

        using (UnityWebRequest www = new UnityWebRequest(url, "POST"))
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
                Debug.Log("Received data: " + receivedData);
                string parsedContent = ParseCourseContent(receivedData);
                Debug.Log("Parsed content: " + parsedContent);
                UpdateChalkboardText(parsedContent);
            }
            else
            {
                Debug.LogError("Error fetching data: " + www.error);
            }
        }
    }


[System.Serializable]
private struct CourseRequestData
{
    public string subject;
    public List<string> topics;
    public string difficulty;
}



    private string ParseCourseContent(string json)
    {
        Debug.Log("Parsing course content...");
        CourseContent content = JsonUtility.FromJson<CourseContent>(json);
        StringBuilder fullText = new StringBuilder();

        foreach (var item in content.courseContent)
        {
            if (!string.IsNullOrEmpty(item.response.Trim()))
            {
                if (fullText.Length > 0 && !fullText.ToString().EndsWith(" ") && !item.response.StartsWith(" ") && !item.response.StartsWith("\n"))
                {
                    fullText.Append(" ");
                }
                fullText.Append(item.response.Trim());
            }
        }

        return fullText.ToString();
    }
    
    void UpdateChalkboardText(string text)
    {
        Debug.Log($"Updating chalkboard text: {text.Substring(0, Mathf.Min(text.Length, 200))}..."); // Show only first 200 characters to avoid flooding the log
        if (chalkboardText != null)
        {
            chalkboardText.text = text;
        }
        else
        {
            Debug.LogError("ChalkboardText is not assigned in the inspector.");
        }
    }
    
}
