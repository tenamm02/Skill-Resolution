using UnityEngine;
using UnityEngine.UI;

public class VirtualKeyboardInput : MonoBehaviour
{
    public OVRVirtualKeyboardInputFieldTextHandler textHandler;

    public void OnInputFieldSelected(InputField selectedInputField)
    {
        textHandler.InputField = selectedInputField;
    }
}