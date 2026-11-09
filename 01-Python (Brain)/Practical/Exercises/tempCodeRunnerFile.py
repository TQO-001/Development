import os
import re

# 1. Paste the path to your video folder here
# Example: "C:/Users/Name/Downloads/Videos" or "/Users/Name/Movies"
FOLDER_PATH = "C:/Users/Admin/Downloads/Sanjeev Thiyagarajan - Python FastAPI Playlist + testing + deployment + CI-CD"

# This looks for: Title; Part #[Number] Python API Course (extra junk)
# It captures the Title as Group 1 and the Number as Group 2
pattern = re.compile(r"^(.*?);\s*Part\s*#(\d+)\s+Python\s+API\s+Course", re.IGNORECASE)

def rename_course_videos():
    if not os.path.exists(FOLDER_PATH):
        print("Error: The specified folder path does not exist.")
        return

    count = 0
    
    for filename in os.listdir(FOLDER_PATH):
        match = pattern.search(filename)
        
        # If the file matches the course pattern, process it
        if match:
            title = match.group(1).strip()
            number = match.group(2).strip()
            
            # Get the file extension (e.g., .mp4, .mkv)
            ext = os.path.splitext(filename)[1]
            
            # Create the new clean name: "1 - What is a Database.mp4"
            new_name = f"{number} - {title}{ext}"
            
            old_file_path = os.path.join(FOLDER_PATH, filename)
            new_file_path = os.path.join(FOLDER_PATH, new_name)
            
            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(filename)
            print(f"👉 Renamed to: {new_name}\n")
            count += 1

    print(f"🎉 Done! Successfully renamed {count} course videos. Other files were ignored.")

if __name__ == "__main__":
    rename_course_videos()