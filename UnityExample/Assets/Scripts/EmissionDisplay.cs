using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Text))]
public class EmissionDisplay : MonoBehaviour
{
    Text text;

    void Start()
    {
        text = GetComponent<Text>();
    }

    public void OnIntensityChanged(float value)
    {
        text.text = String.Format("Emission: {0}0%", value);
    }
}
