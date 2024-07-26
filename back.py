from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import speechmatics
from werkzeug.utils import secure_filename
from httpx import HTTPStatusError
import re

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)

AUTH_TOKEN = "bF81X8FZphjQ2yGX0sb8INd2K2RQd91L"
LANGUAGE = "en"
CONNECTION_URL = f"wss://eu2.rt.speechmatics.com/v2/{LANGUAGE}"

def parse_time_command(transcript):
    match = re.search(r'set time to (\w+ \w+|\w+)', transcript)
    if match:
        time_text = match.group(1)
        return convert_time_to_24hr(time_text)
    return None

def convert_time_to_24hr(time_text):
    time_map = {
        "twelve": "12", "one": "1", "two": "2", "three": "3", 
        "four": "4", "five": "5", "six": "6", "seven": "7", 
        "eight": "8", "nine": "9", "ten": "10", "eleven": "11",
        "quarter": "15", "half": "30"
    }
    
    if "quarter past" in time_text:
        hour = time_map.get(time_text.split()[0].lower())
        return f"{hour}:{15:02d}" if hour else None
    elif "half past" in time_text:
        hour = time_map.get(time_text.split()[0].lower())
        return f"{hour}:{30:02d}" if hour else None
    elif "quarter to" in time_text:
        hour = time_map.get(time_text.split()[0].lower())
        return f"{str(int(hour) % 12 + 1)}:{45:02d}" if hour else None
    elif "half to" in time_text:
        hour = time_map.get(time_text.split()[0].lower())
        return f"{str(int(hour) % 12 + 1)}:{30:02d}" if hour else None

    parts = time_text.split()
    if len(parts) == 2:
        hour = time_map.get(parts[0].lower())
        minute = time_map.get(parts[1].lower())
        return f"{hour}:{minute.zfill(2)}" if hour and minute else None
    return None

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            ws = speechmatics.client.WebsocketClient(
                speechmatics.models.ConnectionSettings(
                    url=CONNECTION_URL,
                    auth_token=AUTH_TOKEN,
                )
            )

            result = []
            ws.add_event_handler(
                event_name=speechmatics.models.ServerMessageType.AddTranscript,
                event_handler=lambda msg: result.append(msg['metadata']['transcript'])
            )

            # Provide transcription config
            transcription_config = speechmatics.models.TranscriptionConfig(
                language=LANGUAGE,
                # Add any other necessary config options as needed
            )

            with open(file_path, "rb") as fd:
                ws.run_synchronously(fd, transcription_config)

            transcript_text = ' '.join(result)
            parsed_time = parse_time_command(transcript_text)

            return jsonify({'transcript': transcript_text, 'parsed_time': parsed_time}), 200

        except HTTPStatusError as e:
            logging.error(f"HTTP error: {e}")
            return jsonify({'error': 'HTTP error'}), 500
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            return jsonify({'error': 'Error during transcription'}), 500
    return jsonify({'error': 'File not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)