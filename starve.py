import yt_dlp
import sys
import os
import subprocess
import shutil
import random

def find_ffmpeg():
    # First check if ffmpeg is in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # Check common installation locations on Windows
    common_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
        os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def convert_to_lowest_quality(input_file):
    # Find FFmpeg
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        print("Error: FFmpeg not found!")
        print("\nPlease install FFmpeg:")
        print("1. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extract the zip file")
        print("3. Add the 'bin' folder to your system PATH")
        print("   OR")
        print("   Place the 'bin' folder in one of these locations:")
        print("   - C:\\Program Files\\ffmpeg\\bin")
        print("   - C:\\Program Files (x86)\\ffmpeg\\bin")
        print("   - %USERPROFILE%\\ffmpeg\\bin")
        return False

    # Generate random number for output file
    random_num = random.randint(1000, 9999)
    output_file = os.path.join('downloads', f'output{random_num}.mp4')
    
    # FFmpeg command with absolute lowest quality settings
    ffmpeg_cmd = [
        ffmpeg_path,
        '-i', input_file,
        '-vf', 'scale=256:144,noise=alls=20:allf=t+u',  # Lowest common resolution
        '-c:v', 'libx264',       # H.264 codec
        '-crf', '52',            # Maximum compression (worst quality)
        '-preset', 'ultrafast',  # Fastest encoding
        '-tune', 'zerolatency',  # Optimize for lowest latency
        '-b:v', '1k',           # Very low video bitrate
        '-maxrate', '1',       # Maximum bitrate
        '-bufsize', '1',       # Buffer size
        '-r', '5',              # 10 fps
        '-c:a', 'aac',           # AAC audio codec
        '-b:a', '2k',           # 16kbps audio (lowest reasonable)
        '-ar', '7350',           # 8kHz audio sample rate
        '-ac', '2',              # Mono audio
        '-af', 'acrusher=bits=4:mode=log:aa=1,volume=2',
        output_file
    ]
    
    try:
        print(f"Using FFmpeg from: {ffmpeg_path}")
        print("Converting to lowest possible quality...")
        subprocess.run(ffmpeg_cmd, check=True)
        # Remove original file
        os.remove(input_file)
        # Rename the converted file to original name
        os.rename(output_file, input_file)
        print("Video converted to lowest possible quality")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {str(e)}")
        return False
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

def download_lowest_quality(url):
    # Create downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Generate random number for output file
    random_num = random.randint(1000, 9999)
    output_filename = f'output{random_num}.mp4'

    ydl_opts = {
        # Format selection for worst possible quality
        'format': 'worst[ext=mp4]/worst',  # This ensures we get the worst quality without needing to merge streams
        'outtmpl': os.path.join('downloads', output_filename),  # Save to downloads/ folder with simple name
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                print("Error: Could not extract video information")
                return
                
            print(f"Downloading: {info['title']}")
            print("Quality: Lowest possible")
            
            # Download the video
            ydl.download([url])
            
            # Get the downloaded file path
            downloaded_file = os.path.join('downloads', output_filename)
            
            # Convert to lowest possible quality
            print("\nConverting to lowest possible quality...")
            if convert_to_lowest_quality(downloaded_file):
                print("\nDownload and conversion completed!")
                print(f"File saved in downloads/ folder")
            else:
                print("\nDownload completed but conversion failed!")
                print(f"Original file saved in downloads/ folder")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the video URL is correct")
        print("2. Check your internet connection")
        print("3. Try using a different YouTube video URL")
        print("4. Make sure FFmpeg is installed and in your system PATH")

def main():
    if len(sys.argv) != 2:
        print("Usage: python starve.py <youtube_url>")
        print("Example: python starve.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)
    
    url = sys.argv[1]
    download_lowest_quality(url)

if __name__ == "__main__":
    main()