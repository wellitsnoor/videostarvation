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
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return False

    # Create downloads directory if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

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
    file_ext = os.path.splitext(input_file)[1]
    
    # For audio files, use AAC output
    audio_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg']
    if file_ext.lower() in audio_extensions:
        output_file = os.path.join('output', f'testing{random_num}.aac')
    else:
        output_file = os.path.join('output', f'testing{random_num}{file_ext}')
    
    # Base FFmpeg command
    ffmpeg_cmd = [ffmpeg_path, '-i', input_file]

    # Check if input is video file
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']

    
    is_video = file_ext.lower() in video_extensions

    

    # Add video filters if video compression is enabled and input is video
    if compress_video and is_video:
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
    elif is_video:
        ffmpeg_cmd.extend(['-c:v', 'copy'])

    # Check if input has audio
    audio_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg']
    has_audio = file_ext.lower() in audio_extensions or is_video

    # Add audio filters if audio compression is enabled and input has audio
    if compress_audio and has_audio:
        ffmpeg_cmd.extend([
            '-c:a', 'aac',
            '-b:a', '0.01k',
            '-ar', '7350',
            '-ac', '2',
            '-strict', 'experimental'
        ])
    elif has_audio:
        ffmpeg_cmd.extend(['-c:a', 'copy'])

    ffmpeg_cmd.append(output_file)
    
    try:
        print(f"Using FFmpeg from: {ffmpeg_path}")
        print("Converting with specified settings...")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}")  # Print the full command
        
        # Run FFmpeg with output capture
        result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        print("FFmpeg output:", result.stdout)
        print("FFmpeg errors:", result.stderr)
        
        # Check if output file exists and has size
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"Output file created with size: {size} bytes")
            print(f"Converted file saved to: {output_file}")
            return True
        else:
            print("Error: Output file was not created!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {str(e)}")
        print(f"FFmpeg error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert media files to lowest quality')
    parser.add_argument('input_file', help='Path to the input media file')
    parser.add_argument('-video', action='store_true', help='Disable video compression')
    parser.add_argument('-audio', action='store_true', help='Disable audio compression')
    parser.add_argument('-high', action='store_true', help='Use higher quality settings')
    
    args = parser.parse_args()
    
    convert_to_lowest_quality(
        args.input_file,
        compress_video=not args.video,
        compress_audio=not args.audio,
        high_quality=args.high
    )
