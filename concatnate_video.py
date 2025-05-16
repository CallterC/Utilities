# This is a rather simple code to concatenate video files and audio files together with the help of ffmpeg
# To use this, you will need to install ffmpeg in advance.
# You will also need to add the ffmpeg to system environment variables if you are using Windows system
import os
import subprocess

dirs = [file for file in os.listdir(os.getcwd()) if ".py" not in file and file != 'temp']
output_path = "output"
os.makedirs(output_path, exist_ok=True)

def concatenate(audio_path, video_path, output_name):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", video_path,    # Input video file
        "-i", audio_path,    # Input audio file
        "-c", "copy",         # Copy streams directly (no re-encoding)
        "-movflags", "frag_keyframe+empty_moov",  # Handle fragmented MP4
        output_name           # Output file
    ]

    # Execute the command
    try:
        subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.PIPE)
        print(f"Successfully created {output_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging files: {e.stderr.decode()}")
