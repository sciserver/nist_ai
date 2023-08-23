from moviepy.editor import VideoFileClip
import os
import ffmpeg
from pprint import pprint
import hashlib

audio_exts = {'m4a'}

# Converts video to audio using MoviePy library that uses `ffmpeg` under the hood
def generate_audio(video_file, output_ext="mp3"):
    filename, ext = os.path.splitext(video_file)
    
    if os.path.exists(filename + '.wav'): return None
    if ext in audio_exts: return None
    
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{output_ext}")
    audio_file = video_file.replace(".mp4",".wav")
    return audio_file

def get_checksum(file_name):
    with open(file_name, 'rb') as file_to_check:
        data = file_to_check.read()    
        return hashlib.md5(data).hexdigest()
    
def local_file_v(filename):
    local_v = 'assets/test_data/' + filename.split('/')[-1]
    if not os.path.exists(local_v):
        pass
        # local_v = 'assets/test_data/pod_clip_1.mp4'
    return local_v

# assuming input is gp pro video for now
def generate_gps(video_file, input_type="go-pro"):
    filename, ext = os.path.splitext(video_file)
    
    if os.path.exists(filename + '.csv'): return None
    if input_type != 'go-pro': return None
    