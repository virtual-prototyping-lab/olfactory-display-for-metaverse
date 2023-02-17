using System;
using System.Collections;
using System.Collections.Generic;
using System.IO.Ports;
using System.Text;
using Unity.Collections;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

// To fix the error with `Ports` missing in `System.IO`, set the following:
// Edit -> Project Settings -> Player -> Other Settings -> Api Compatibility Level -> .NET 4.x

public class OlfactoryControl : MonoBehaviour
{
    public string portName;
    int baudRate = 115200;

    static SerialPort serialPort;

    int intensity1 = 10;
    int intensity2 = 10;

    // Start is called before the first frame update
    void Start()
    {
        OpenPort();
    }

    void OnApplicationQuit()
    {
        serialPort.Close();
    }

    public void SetOlfactory(bool channel1, bool channel2)
    {
        if (serialPort != null && serialPort.IsOpen)
        {
            serialPort.Write("0"); // Reset all channels
            if (channel1)
            {
                char intensityChar = (char)(intensity1 - 1 + 'A');
                serialPort.Write(String.Format("{0}1", intensityChar)); // Enable channel 1
            }
            if (channel2)
            {
                char intensityChar = (char)(intensity2 - 1 + 'A');
                serialPort.Write(String.Format("{0}2", intensityChar)); // Enable channel 2
            }
        }
        else
        {
            Debug.LogWarning("Olfactory port not ready");
        }
    }

    void OpenPort()
    {
        serialPort = new SerialPort(portName, baudRate);
        // serialPort.DtrEnable = false;  // This can be used to prevent the Arduino from resetting on connection, add 10uF capacitor between RST and GND
        serialPort.ReadTimeout = 15;
        serialPort.WriteTimeout = 1;

        if (serialPort != null && !serialPort.IsOpen)
        {
            serialPort.Open();
            print("Port opened");
        }
    }

    public void OnIntensity1Changed(float value)
    {
        intensity1 = Mathf.RoundToInt(Mathf.Clamp(value, 1, 10));
    }

    public void OnIntensity2Changed(float value)
    {
        intensity2 = Mathf.RoundToInt(Mathf.Clamp(value, 1, 10));
    }

    // The following methods are just overloads to SetOlfactory so they can be called with buttons

    public void SetChannel1()
    {
        SetOlfactory(true, false);
    }
    public void SetChannel2()
    {
        SetOlfactory(false, true);
    }
    public void SetBoth()
    {
        SetOlfactory(true, true);
    }
    public void SetNone()
    {
        SetOlfactory(false, false);
    }
}

#if UNITY_EDITOR
[CustomEditor(typeof(OlfactoryControl))]
class OlfactoryControlEditor : Editor
{
    public override void OnInspectorGUI()
    {
        var myTarget = (OlfactoryControl)target;
        StringBuilder sb = new StringBuilder("", 50);
        foreach (string s in SerialPort.GetPortNames())
        {
            sb.AppendFormat("{0}\n", s);
        }

        GUIStyle textStyle = EditorStyles.label;
        textStyle.wordWrap = true;
        EditorGUILayout.LabelField("Available ports", sb.ToString(), textStyle);

        DrawDefaultInspector();
    }
}
#endif // UNITY_EDITOR
