using UnityEngine;
using UnityEngine.UI;

public class VirtualKeyboardInput : MonoBehaviour
{
    private InputField currentInputField;

    public void SetCurrentInputField(InputField inputField)
    {
        currentInputField = inputField;
    }

    public void AppendCharacter(string character)
    {
        if (currentInputField != null)
        {
            currentInputField.text += character;
        }
    }

    public void DeleteCharacter()
    {
        if (currentInputField != null && currentInputField.text.Length > 0)
        {
            currentInputField.text = currentInputField.text.Substring(0, currentInputField.text.Length - 1);
        }
    }

    public void ClearText()
    {
        if (currentInputField != null)
        {
            currentInputField.text = "";
        }
    }
}