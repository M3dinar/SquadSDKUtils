import sys
import os
import json
import tkinter as tk
from tkinter import filedialog
import re
import unreal

def get_squadSDK_installation_folder():
    """
    Returns the folder where SDK is installed.
    """
    # Get the base directory of the SDK editor.
    base_dir = unreal.SystemLibrary.get_project_directory()

    # Move up three directories to get the installation folder
    installation_folder = os.path.abspath(os.path.join(base_dir, ".."))

    return installation_folder

def read_ini_file(file_path):
    """
    Reads the .ini file and returns its contents as a dictionary.
    """
    config = {}
    current_section = None

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith(';'):  # Skip empty lines and comments
                    continue
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    config[current_section] = []
                elif '=' in line and current_section:
                    key, value = line.split('=', 1)
                    config[current_section].append((key.strip(), value.strip()))
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except IOError as e:
        print(f"Error: An I/O error occurred while reading the file '{file_path}'. Details: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred. Details: {e}")

    return config

def write_ini_file(file_path, config):
    """
    Writes the updated config dictionary back to the .ini file.
    """
    try:
        with open(file_path, 'w') as file:
            for section, options in config.items():
                file.write(f'[{section}]\n')
                for key, value in options:
                    file.write(f'{key}={value}\n')
                file.write('\n')
    except IOError as e:
        print(f"Error: An I/O error occurred while writing to the file '{file_path}'. Details: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred. Details: {e}")

def load_mod_json_data(json_file_path):
    """Load data from a JSON file and extract specific keys."""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        paths_to_exclude_from_asset_validator = data.get("PathToExcludeFromAssetValidator" ,[])
        asset_manager_settings = data.get("AssetManagerSettings" ,{})
        directories_to_never_cook = data.get("DirectoriesToNeverCook" ,[])
    return paths_to_exclude_from_asset_validator, asset_manager_settings, directories_to_never_cook

def load_vanilla_json_data():
    """Load data from a JSON file and extract specific keys."""
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf', 'vanilla.json')
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        asset_manager_settings = data.get("AssetManagerSettings", {})
    return asset_manager_settings

def ensure_excluded_directory(squad_sdk_path, paths_to_exclude):
    """
    Ensures that the specified path are exclude from the asset validator before the cook process

    :param squad_sdk_path: The path to the squad SDK
    :param paths_to_exclude: A list of path to exclude
    """
    ini_file_path = squad_sdk_path + '\\Squad\\Config\\DefaultEditor.ini'
    section_group = '/Script/DataValidation.EditorValidatorSubSystem'

    if not paths_to_exclude:
        print("No paths to exclude were provided.")
        return

    # Read the .ini file
    config = read_ini_file(ini_file_path)

    if section_group not in config:
        print(f"Section '{section_group}' not found in the .ini file.")
        return

    config[section_group] = [
        (key, value) for key, value in config[section_group]
        if key != '+ExcludedDirectories'
    ]

    # Add the new paths to +ExcludedDirectories
    for path_value in paths_to_exclude:
        config[section_group].append(('+ExcludedDirectories', f"(Path=\"/{path_value}/\")"))
        print(f"Added '{path_value}' to section '{section_group}' in the .ini file.")

    # Write the updated config back to the .ini file
    write_ini_file(ini_file_path, config)
    print("Updated .ini file with new excluded directories.")

def extract_key_value_pairs(config_str):
    """
    Extracts key-value pairs from the configuration string.

    :param config_str: The configuration string.
    :return: A list of key-value pairs as strings.
    """
    # Remove outer parentheses if present
    if config_str.startswith('(') and config_str.endswith(')'):
        config_str = config_str[1:-1]

    # Split the string by commas to get individual pairs
    parts = config_str.split(',')

    # Filter out parts that start with parentheses (nested structures)
    key_value_pairs = [part for part in parts if not part.startswith('(')]

    return key_value_pairs

def update_asset_manager(squad_sdk_path, asset_paths):
    """
    Set the asset manager to the mod configuration.

    :param squad_sdk_path: The path to the squad SDK.
    :param asset_paths: A dictionary mapping asset types to their corresponding paths.
    """
    ini_file_path = os.path.join(squad_sdk_path, 'Squad', 'Config', 'DefaultAssetManagerSettings.ini')
    section_group = '/Script/Engine.AssetManagerSettings'

    # Read the .ini file
    config = read_ini_file(ini_file_path)

    if section_group not in config:
        config[section_group] = []

    for i, (key, value) in enumerate(config[section_group]):
        if key == '+PrimaryAssetTypesToScan':
            for asset_type, paths in asset_paths.items():
                if asset_type in value:
                    parts = extract_key_value_pairs(value)

                    # Modify the Directories part
                    for j, part in enumerate(parts):
                        if 'Directories=' in part:
                            parts[j] = f"Directories=(" + ','.join([f'(Path="{path}")' for path in paths]) + ")"
                            break

                    # Reassemble the value
                    new_value = f"({','.join(parts)})"
                    config[section_group][i] = (key, new_value)
                    print(f"Updated Directories for {asset_type} in '{section_group}'.")
                    break  # Exit the loop once the relevant asset type is processed

    # Write the updated config back to the .ini file
    write_ini_file(ini_file_path, config)
    print("Asset manager configuration updated.")

def update_directories_to_never_cook(squad_sdk_path, paths_to_not_cook):
    """
    Ensures that the specified path are exclude from the asset validator before the cook process

    :param squad_sdk_path: The path to the squad SDK
    :param paths_to_not_cook: A list of path to exclude
    """
    ini_file_path = squad_sdk_path + '\\Squad\\Config\\DefaultGame.ini'
    section_group = '/Script/UnrealEd.ProjectPackagingSettings'

    if not paths_to_not_cook:
        print("No paths to not cook were provided.")
        return

    # Read the .ini file
    config = read_ini_file(ini_file_path)

    if section_group not in config:
        print(f"Section '{section_group}' not found in the .ini file.")
        return

    config[section_group] = [
        (key, value) for key, value in config[section_group]
        if key != '+DirectoriesToNeverCook'
    ]

    # Add the new paths to +DirectoriesToNeverCook
    for path_value in paths_to_not_cook:
        config[section_group].append(('+DirectoriesToNeverCook', f"(Path=\"{path_value}/\")"))
        print(f"Added '{path_value}' to section '{section_group}' in the .ini file.")

    # Write the updated config back to the .ini file
    write_ini_file(ini_file_path, config)
    print("Updated .ini file with new directories to never cook.")

def main():

    squad_sdk_path = get_squadSDK_installation_folder()

    # Create a Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select the JSON file
    json_mod_file_path = filedialog.askopenfilename(
        title="Select the JSON file",
        filetypes=[("JSON Files", "*.json")],
        defaultextension=".json"
    )

    # Check if a file was selected
    if not json_mod_file_path:
        print("No file selected. Exiting.")
        return
    
    paths_to_exclude_from_asset_validator, mod_asset_manager_settings, directories_to_never_cook = load_mod_json_data(json_mod_file_path)
    vanilla_asset_manager_settings = load_vanilla_json_data()
    
    # Add the mod as exclude for the asset validator during cook
    ensure_excluded_directory(squad_sdk_path, paths_to_exclude_from_asset_validator)
    
    # Update asset manager
    new_asset_manager = {
        'PrimaryAssetLabel': vanilla_asset_manager_settings.get("PrimaryAssetLabel", []) + mod_asset_manager_settings.get("PrimaryAssetLabel", []),
        'SQLevel': vanilla_asset_manager_settings.get("SQLevel", []) + mod_asset_manager_settings.get("SQLevel", []),
        'SQLayer': vanilla_asset_manager_settings.get("SQLayer", []) + mod_asset_manager_settings.get("SQLayer", []),
        'SQFaction': vanilla_asset_manager_settings.get("SQFaction", []) + mod_asset_manager_settings.get("SQFaction", []),
        'SQFactionSetup': vanilla_asset_manager_settings.get("SQFactionSetup", []) + mod_asset_manager_settings.get("SQFactionSetup", [])
    }

    update_asset_manager(squad_sdk_path, new_asset_manager)
    
    # Update directory to never cook
    update_directories_to_never_cook(squad_sdk_path, directories_to_never_cook)
    
    print("Restart the SDK to take the new configuration into account.")

if __name__ == "__main__":
    main()
