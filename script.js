document.addEventListener('DOMContentLoaded', () => {
    let mediaRecorder;
    let audioChunks = [];

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstart = () => {
                console.log("Recording started...");
                document.getElementById("status").innerText = "Recording...";
            };

            mediaRecorder.onstop = async () => {
                console.log("Recording stopped.");
                document.getElementById("status").innerText = "Processing...";
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];

                const formData = new FormData();
                formData.append('file', audioBlob, 'audio.wav');

                try {
                    const response = await fetch('http://127.0.0.1:5000/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    document.getElementById("transcript").innerText = result.transcript;
                    if (result.parsed_time) {
                        document.getElementById("parsedTime").innerText = `Parsed Time: ${result.parsed_time}`;
                    } else {
                        document.getElementById("parsedTime").innerText = "No valid time found.";
                    }
                    document.getElementById("status").innerText = "Transcription complete";
                } catch (error) {
                    console.error("Error during transcription:", error);
                    document.getElementById("status").innerText = "Error during transcription";
                }
            };

            mediaRecorder.start();
        } catch (error) {
            console.error("Error accessing microphone:", error);
            document.getElementById("status").innerText = "Error accessing microphone";
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        } else {
            console.error("MediaRecorder is not initialized or already stopped.");
        }
    }

    document.getElementById("recordButton").addEventListener("mousedown", startRecording);
    document.getElementById("recordButton").addEventListener("mouseup", stopRecording);
});