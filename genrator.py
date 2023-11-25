import re
import json

def parse_osu_file(osu_file_content):
    beatmap = {}

    # Remove comments and split lines
    lines = [line.strip() for line in osu_file_content.split('\n') if not line.strip().startswith('//')]

    current_section = None

    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            beatmap[current_section] = {}
        elif current_section:
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                beatmap[current_section][key] = value
            else:
                # Handle lines without ':', e.g., empty lines
                beatmap[current_section][line] = None

    return beatmap

def convert_to_json(beatmap):
    json_data = json.dumps(beatmap, indent=2)
    return json_data

def read_osu_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_json_to_file(json_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json_data)

def main():
    osu_file_path = 'test.osu'  # Replace with the path to your osu file
    output_json_path = 'output.json'

    osu_file_content = read_osu_file(osu_file_path)
    beatmap_data = parse_osu_file(osu_file_content)
    json_data = convert_to_json(beatmap_data)

    save_json_to_file(json_data, output_json_path)

if __name__ == "__main__":
    main()
