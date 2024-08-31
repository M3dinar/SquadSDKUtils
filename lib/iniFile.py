import os

def read_ini_file(file_path):
    """
    Reads the .ini file and returns its contents as a dictionary.
    """
    config = {}
    current_section = None

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

    return config

def write_ini_file(file_path, config):
    """
    Writes the updated config dictionary back to the .ini file.
    """
    with open(file_path, 'w') as file:
        for section, options in config.items():
            file.write(f'[{section}]\n')
            for key, value in options:
                file.write(f'{key}={value}\n')
            file.write('\n')