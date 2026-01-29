
import os
import shutil

# Define paths
BASE_DIR = os.getcwd()
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Subdirectories for frontend
HTML_DIR = os.path.join(FRONTEND_DIR, 'html')
CSS_DIR = os.path.join(FRONTEND_DIR, 'css')
JS_DIR = os.path.join(FRONTEND_DIR, 'js')
IMAGES_DIR = os.path.join(FRONTEND_DIR, 'images')

# Create directories
for d in [HTML_DIR, CSS_DIR, JS_DIR, IMAGES_DIR, SCRIPTS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)
        print(f"Created directory: {d}")

# Helper function to move files
def move_file(src, dst_folder):
    if os.path.exists(src):
        filename = os.path.basename(src)
        dst = os.path.join(dst_folder, filename)
        try:
            shutil.move(src, dst)
            print(f"Moved {filename} to {dst_folder}")
        except Exception as e:
            print(f"Error moving {filename}: {e}")

# 1. Move HTML files
for file in os.listdir(BASE_DIR):
    if file.endswith('.html'):
        move_file(os.path.join(BASE_DIR, file), HTML_DIR)

# 2. Move CSS files
old_css_dir = os.path.join(BASE_DIR, 'css')
if os.path.exists(old_css_dir):
    for file in os.listdir(old_css_dir):
        move_file(os.path.join(old_css_dir, file), CSS_DIR)
    try:
        os.rmdir(old_css_dir)
        print("Removed old css directory")
    except:
        print("Could not remove old css directory (not empty?)")

# 3. Move JS files
old_js_dir = os.path.join(BASE_DIR, 'js')
if os.path.exists(old_js_dir):
    for file in os.listdir(old_js_dir):
        move_file(os.path.join(old_js_dir, file), JS_DIR)
    try:
        os.rmdir(old_js_dir)
        print("Removed old js directory")
    except:
        print("Could not remove old js directory (not empty?)")

# 4. Move Images
old_images_dir = os.path.join(BASE_DIR, 'images')
if os.path.exists(old_images_dir):
    for file in os.listdir(old_images_dir):
        move_file(os.path.join(old_images_dir, file), IMAGES_DIR)
    try:
        os.rmdir(old_images_dir)
        print("Removed old images directory")
    except:
        print("Could not remove old images directory (not empty?)")

# 5. Move Scripts
# We move all .py files in root, EXCEPT those that might be critical or part of this script itself.
# We should NOT move `organize_project.py` while it's running (though usually fine on Linux, Windows might lock).
# We should NOT move `backend` folder (it's a folder).

current_script = os.path.basename(__file__)

for file in os.listdir(BASE_DIR):
    file_path = os.path.join(BASE_DIR, file)
    
    # Skip directories
    if os.path.isdir(file_path):
        continue
        
    # Skip this script
    if file == current_script:
        continue
        
    # Move .py files, .bat files, .log files, .sql files
    if file.endswith(('.py', '.bat', '.log', '.sql')):
        # Check if it's not in backend (already filtered by isdir check on backend folder, but file is in root)
        move_file(file_path, SCRIPTS_DIR)

print("Organization complete.")
