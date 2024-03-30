using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class ChalkboardUpdater : MonoBehaviour
{
    public Renderer chalkboardRenderer; // Assign the Mesh Renderer of the chalkboard in the Inspector

    void Start()
    {
        StartCoroutine(FetchAndUpdateChalkboard());
    }

    IEnumerator FetchAndUpdateChalkboard()
    {
        while (true)
        {
            UnityWebRequest www = UnityWebRequest.Get("http://yourflaskbackend.com/api/data");
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                string data = www.downloadHandler.text;
                UpdateChalkboardTexture(data);
            }
            else
            {
                Debug.LogError("Error fetching data: " + www.error);
            }

            yield return new WaitForSeconds(5); // Fetch and update every 5 seconds
        }
    }

    void UpdateChalkboardTexture(string text)
    {
        // Create a new Texture2D and fill it with the text data
        Texture2D texture = new Texture2D(256, 256);
        FillTextureWithText(texture, text);
        
        // Apply the texture to the chalkboard material
        chalkboardRenderer.material.mainTexture = texture;
    }

    void FillTextureWithText(Texture2D texture, string text)
    {
        // Here you would use text rendering methods to draw the text onto the texture
        // For simplicity, we'll just clear the texture to a solid color
        Color fillColor = Color.black; // Black background for chalkboard
        Color[] fillPixels = new Color[texture.width * texture.height];

        for (int i = 0; i < fillPixels.Length; i++)
        {
            fillPixels[i] = fillColor;
        }

        texture.SetPixels(fillPixels);
        texture.Apply();

        // Text rendering logic should go here, using Graphics.DrawTexture or similar
        // For now, we just have a solid color
    }
}
