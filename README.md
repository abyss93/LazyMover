    __                      __  ___                    
   / /   ____ _____  __  __/  |/  /___ _   _____  _____
  / /   / __ `/_  / / / / / /|_/ / __ \ | / / _ \/ ___/
 / /___/ /_/ / / /_/ /_/ / /  / / /_/ / |/ /  __/ /    
/_____/\__,_/ /___/\__, /_/  /_/\____/|___/\___/_/     
                  /____/                               

Have an easy life moving iPhone photos/videos imported in Linux

# Dependencies:
https://pypi.org/project/pillow/

# Usage
python3 lazymover.py source_dir dest_dir [-d | --dry-run]

source_dir = root dir of media that you have to order
dest_dir = root dir where sorted files will be MOVED
--dry-run = print what would happen...
    
# Sort logic
each file is examined using EXIF DateTime tag, if that is not found it fallbacks to stat modification date (os.path.getmtime).
Then the file is moved to destination directory dest_dir/year/month/day/sorted_<filename>
