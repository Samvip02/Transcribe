# Transcribe
# Flask Transcription Service

This is a Flask web application that allows users to upload audio files for transcription. The app processes the audio and extracts time commands such as "quarter past" or "half to."

## Features

- Upload audio files for transcription.
- Supports time phrases like "quarter past," "half past," "quarter to," and "half to."
- Simple and user-friendly interface.

## Requirements

To run this application, you need Python 3.x installed on your machine.

### Install Dependencies

Create a virtual environment and install the required packages:

```bash
# Create a virtual environment
python -m venv venv
# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
