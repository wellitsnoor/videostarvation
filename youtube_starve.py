import yt_dlp
import sys
import os
import subprocess
import shutil
import random
import argparse

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

def convert_to_lowest_quality(input_file, compress_video=True, compress_audio=True, high_quality=False):
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
    
    # Base FFmpeg command
    ffmpeg_cmd = [ffmpeg_path, '-i', input_file]

    # Add video filters if video compression is enabled
    if compress_video:
        if high_quality:
            scale_filter = "scale=1920:1080"
        else:
            scale_filter = "scale=192:108"
        ffmpeg_cmd.extend(['-vf', f"{scale_filter},noise=alls=100:allf=t+u"])
        ffmpeg_cmd.extend([
            '-c:v', 'libx264',
            '-crf', '52',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-b:v', '100k',
            '-maxrate', '300k',
            '-bufsize', '300k',
            '-r', '10'
        ])
    else:
        ffmpeg_cmd.extend(['-c:v', 'copy'])

    # Add audio filters if audio compression is enabled
    if compress_audio:
        ffmpeg_cmd.extend([
            '-c:a', 'aac',
            '-b:a', '0.1k',
            '-ar', '7350',
            '-ac', '2',
            '-af', "acrusher=bits=30:mode=log:aa=1"
        ])
    else:
        ffmpeg_cmd.extend(['-c:a', 'copy'])

    ffmpeg_cmd.append(output_file)
    
    try:
        print(f"Using FFmpeg from: {ffmpeg_path}")
        print("Converting with specified settings...")
        subprocess.run(ffmpeg_cmd, check=True)
        # Remove original file
        os.remove(input_file)
        # Rename the converted file to original name
        os.rename(output_file, input_file)
        print("Video converted successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {str(e)}")
        return False
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

def download_lowest_quality(url, compress_video=True, compress_audio=True, high_quality=False):
    # Create downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Generate random number for output file
    random_num = random.randint(1000, 9999)
    output_filename = f'output{random_num}.mp4'

    ydl_opts = {
        'format': 'worst[ext=mp4]/worst',
        'outtmpl': os.path.join('downloads', output_filename),
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                print("Error: Could not extract video information")
                return
                
            print(f"Downloading: {info['title']}")
            print("Quality: Lowest possible")
            
            ydl.download([url])
            
            downloaded_file = os.path.join('downloads', output_filename)
            
            print("\nConverting with specified settings...")
            if convert_to_lowest_quality(downloaded_file, compress_video, compress_audio, high_quality):
                print("\nDownload and conversion completed!")
                print(f"File saved in downloads/ folder")
                print("File name: ", output_filename)
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
    parser = argparse.ArgumentParser(description='Download and compress YouTube videos')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-video', action='store_true', help='Compress only video')
    parser.add_argument('-audio', action='store_true', help='Compress only audio')
    parser.add_argument('-high', action='store_true', help='Use high quality settings (1080p)')
    parser.add_argument('-low', action='store_true', help='Use low quality settings (192x108p)')
    
    args = parser.parse_args()
    
    # If neither -video nor -audio is specified, compress both
    compress_video = args.video or not (args.video or args.audio)
    compress_audio = args.audio or not (args.video or args.audio)
    
    # If both -high and -low are specified, -high takes precedence
    high_quality = args.high
    
    download_lowest_quality(args.url, compress_video, compress_audio, high_quality)

if __name__ == "__main__":
    main()