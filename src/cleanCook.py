import os
import glob
import json
import tkinter as tk
from tkinter import filedialog

def load_json_data(json_file_path):
    """Load data from a JSON file and extract specific keys."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        squad_sdk_path = data.get("SquadSDKPath", "")
        mod_name = data.get("ModName", "")
    return squad_sdk_path, mod_name

def remove_files(squad_sdk_path, mod_name):
    """Find and remove specific files within the specified path."""
    file_paths = glob.glob(os.path.join(squad_sdk_path, "Squad\\ModSDK\\" + mod_name, '**', 'DevelopmentAssetRegistry.bin'), recursive=True)
    if not file_paths:
        print("No files found to remove.")
        return
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f"Removed: {file_path}")
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}")

def main():
    # Create a Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select the JSON file
    json_file_path = filedialog.askopenfilename(
        title="Select the JSON file",
        filetypes=[("JSON Files", "*.json")],
        defaultextension=".json"
    )

    # Check if a file was selected
    if not json_file_path:
        print("No file selected. Exiting.")
        return
    
    # Load JSON data and extract necessary information
    squad_sdk_path, mod_name = load_json_data(json_file_path)
    
    # Remove files based on the Squad SDK path
    remove_files(squad_sdk_path, mod_name)
    
    print("Done.")

if __name__ == "__main__":
    main()