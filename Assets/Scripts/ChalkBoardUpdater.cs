using System.Collections;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class ChalkboardUpdater : MonoBehaviour
{
    public Renderer chalkboardRenderer; // Assign the Mesh Renderer of the chalkboard in the Inspector

    private Texture2D texture;

    void Start()
    {
        texture = new Texture2D(256, 256);
        chalkboardRenderer.material.mainTexture = texture;
        StartCoroutine(FetchAndUpdateChalkboard());
    }

    IEnumerator FetchAndUpdateChalkboard()
    {
        string url = "http://localhost:5000/generate-course";
        var courseParams = new
        {
            subject = "Math",
            topics = "Algebra",
            difficulty = "beginner"
        };
        string jsonData = JsonUtility.ToJson(courseParams);

        using (UnityWebRequest www = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
        {
            byte[] jsonToSend = new UTF8Encoding().GetBytes(jsonData);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(jsonToSend);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                string data = www.downloadHandler.text;
                Debug.Log("Received: " + data);
                // Update the chalkboard texture or handle the data as needed
            }
            else
            {
                Debug.LogError("Error fetching data: " + www.error);
            }
        }
    }




    void UpdateChalkboardTexture(string text)
    {
        FillTextureWithText(texture, text);

        // Apply the updated texture to the chalkboard material
        chalkboardRenderer.material.mainTexture = texture;
    }

    void FillTextureWithText(Texture2D texture, string text)
    {
        // Clear the texture to a solid color, here assuming a blackboard
        Color bgColor = Color.black;
        Color textColor = Color.white; // Text color, white like chalk
        texture.SetPixels(Enumerable.Repeat(bgColor, texture.width * texture.height).ToArray());
        
        // Simulating text drawing (very basic)
        int startX = 10; // Start position of the text on the texture
        int startY = texture.height - 20; // Adjust as needed
        int pixelPerChar = 6; // Width of each character in pixels

        for (int i = 0; i < text.Length && startX + i * pixelPerChar < texture.width; i++)
        {
            // This is a very simplistic way to represent text drawing
            // You would replace this with actual text rendering logic
            for (int x = 0; x < pixelPerChar; x++)
            {
                texture.SetPixel(startX + i * pixelPerChar + x, startY, textColor);
            }
        }

        texture.Apply();
    }
}
