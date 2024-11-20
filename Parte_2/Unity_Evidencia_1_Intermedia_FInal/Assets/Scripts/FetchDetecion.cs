using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class FetchDetection : MonoBehaviour
{
    [Header("Server Configuration")]
    public string serverUrl = "http://127.0.0.1:5000"; // Replace with your Flask server URL

    [Header("Cinemachine Camera")]
    public Cinemachine.CinemachineVirtualCamera agentCamera; // Assign the Cinemachine camera in the Inspector

    // Detection data structure
    [System.Serializable]
    public class Detection
    {
        public int class_;
        public int center_x;
        public int center_y;
        public int[] bbox;
    }

    void Start()
    {
        StartCoroutine(GetDetection());
    }

    IEnumerator GetDetection()
    {
        string url = $"{serverUrl}/get_detection";

        while (true)
        {
            UnityWebRequest request = UnityWebRequest.Get(url);
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonResponse = request.downloadHandler.text;

                if (!string.IsNullOrEmpty(jsonResponse))
                {
                    try
                    {
                        Detection detection = JsonUtility.FromJson<Detection>(jsonResponse);
                        Debug.Log($"Detected object: Class {detection.class_}, Center: ({detection.center_x}, {detection.center_y})");

                        // Optional: Update Cinemachine camera to focus on detected object
                        UpdateCamera(detection);
                    }
                    catch (System.Exception ex)
                    {
                        Debug.LogError($"Error parsing detection response: {ex.Message}");
                    }
                }
            }
            else if (request.responseCode == 204)
            {
                Debug.Log("No object detected");
            }
            else
            {
                Debug.LogError($"Failed to get detection: {request.error}");
            }

            yield return new WaitForSeconds(1f); // Poll every 1 second
        }
    }

    void UpdateCamera(Detection detection)
    {
        if (agentCamera != null)
        {
            // Example logic: Move camera to center of detected object
            Vector3 newPosition = new Vector3(detection.center_x, detection.center_y, agentCamera.transform.position.z);
            agentCamera.transform.position = Vector3.Lerp(agentCamera.transform.position, newPosition, Time.deltaTime * 2f);
        }
    }
}
