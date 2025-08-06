import os
import logging
from datetime import datetime
from pydub import AudioSegment
import tempfile

# Setup logging
logger = logging.getLogger(__name__)

# Create recordings directory if it doesn't exist
RECORDINGS_DIR = "recordings"
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

async def process_voice_recording(temp_path, original_filename):
    """
    Process uploaded audio file and convert to MP3
    """
    try:
        logger.info(f" [VOICE] Processing voice recording: {original_filename}")
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(original_filename)[0]
        mp3_filename = f"voice_recording_{timestamp}_{base_name}.mp3"
        mp3_path = os.path.join(RECORDINGS_DIR, mp3_filename)
        
        # Convert audio to MP3 using pydub
        logger.info(" [VOICE] Converting audio to MP3...")
        
        # Load audio file (pydub can handle various formats)
        audio = AudioSegment.from_file(temp_path)
        
        # Export as MP3 with good quality settings
        audio.export(
            mp3_path,
            format="mp3",
            bitrate="192k",
            parameters=["-q:a", "0"]  # High quality
        )
        
        # Get file info
        file_size = os.path.getsize(mp3_path)
        duration = len(audio) / 1000  # Duration in seconds
        
        logger.info(f" [VOICE] MP3 created successfully: {mp3_filename}")
        logger.info(f" [VOICE] File size: {file_size} bytes, Duration: {duration:.2f} seconds")
        
        result = {
            "success": True,
            "filename": mp3_filename,
            "file_path": mp3_path,
            "download_url": f"http://localhost:8000/download/{mp3_filename}",
            "file_size": file_size,
            "duration": duration,
            "format": "mp3",
            "bitrate": "192k",
            "timestamp": timestamp
        }
        
        return result
        
    except Exception as e:
        logger.error(f" [VOICE] Error processing voice recording: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "filename": None,
            "download_url": None
        }

def get_recording_info(filename):
    """
    Get information about a specific recording
    """
    try:
        file_path = os.path.join(RECORDINGS_DIR, filename)
        
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
        
        # Try to get audio duration
        try:
            audio = AudioSegment.from_mp3(file_path)
            duration = len(audio) / 1000
        except:
            duration = None
        
        return {
            "filename": filename,
            "file_size": file_size,
            "duration": duration,
            "modified_time": modified_time,
            "download_url": f"http://localhost:8000/download/{filename}"
        }
        
    except Exception as e:
        logger.error(f"Error getting recording info: {e}")
        return {"error": str(e)}

def list_all_recordings():
    """
    List all available recordings
    """
    try:
        recordings = []
        
        if os.path.exists(RECORDINGS_DIR):
            for filename in os.listdir(RECORDINGS_DIR):
                if filename.endswith('.mp3'):
                    info = get_recording_info(filename)
                    if "error" not in info:
                        recordings.append(info)
        
        # Sort by modified time (newest first)
        recordings.sort(key=lambda x: x.get('modified_time', 0), reverse=True)
        
        return {
            "recordings": recordings,
            "total_count": len(recordings)
        }
        
    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        return {
            "error": str(e),
            "recordings": [],
            "total_count": 0
        }

def delete_recording(filename):
    """
    Delete a specific recording
    """
    try:
        file_path = os.path.join(RECORDINGS_DIR, filename)
        
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        os.remove(file_path)
        logger.info(f" [VOICE] Deleted recording: {filename}")
        
        return {"success": True, "message": f"Recording {filename} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting recording: {e}")
        return {"error": str(e)}

def cleanup_old_recordings(days_old=30):
    """
    Clean up recordings older than specified days
    """
    try:
        if not os.path.exists(RECORDINGS_DIR):
            return {"message": "No recordings directory found"}
        
        import time
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        deleted_count = 0
        
        for filename in os.listdir(RECORDINGS_DIR):
            if filename.endswith('.mp3'):
                file_path = os.path.join(RECORDINGS_DIR, filename)
                file_time = os.path.getmtime(file_path)
                
                if file_time < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f" [CLEANUP] Deleted old recording: {filename}")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} recordings older than {days_old} days"
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {"error": str(e)}
