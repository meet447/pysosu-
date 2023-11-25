import json

def parse_osu_beatmap(file_path):
    beatmap_data = {
        "circle_spawn_interval": 500,  # milliseconds
        "shrink_rate": 30,
        "positions": [],
        "title": "",
        "artist": "",
        "audio": "",
        "background_image": "",
        "difficulty": {
            "HPDrainRate": 0,
            "CircleSize": 0,
            "OverallDifficulty": 0,
            "ApproachRate": 0,
            "SliderMultiplier": 0,
            "SliderTickRate": 0,
        }
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # Flags to determine if hit objects and difficulty sections are reached
        hit_objects_section = False
        difficulty_section = False

        for line in lines:
            line = line.strip()

            # Check if the hit objects section is reached
            if line == "[HitObjects]":
                hit_objects_section = True
                continue

            if hit_objects_section:
                # Split the line to get hit object details
                elements = line.split(',')

                # Extract x and y coordinates
                x, y = map(int, elements[:2])
                beatmap_data["positions"].append([x, y])

            # Check if the difficulty section is reached
            if line == "[Difficulty]":
                difficulty_section = True
                continue

            if difficulty_section:
                # Split the line to get difficulty details
                elements = line.split(':')
                if len(elements) == 2:
                    key, value = map(str.strip, elements)
                    # Check if the key is in the difficulty dictionary
                    if key in beatmap_data["difficulty"]:
                        beatmap_data["difficulty"][key] = float(value)

            # Extract general metadata
            if line.startswith("Title:"):
                beatmap_data["title"] = line[len("Title:"):].strip()
            elif line.startswith("Artist:"):
                beatmap_data["artist"] = line[len("Artist:"):].strip()
            elif line.startswith("AudioFilename:"):
                beatmap_data["audio"] = line[len("AudioFilename:"):].strip()
            elif line.startswith("0,0,"):
                beatmap_data["background_image"] = line.split('"')[1]

    return beatmap_data

def save_beatmap_to_json(beatmap_data, filename):
    with open(filename, 'w') as file:
        json.dump(beatmap_data, file, indent=2)

# Example: Replace 'your_beatmap.osu' with the path to your osu! beatmap file
osu_beatmap_file = 'test.osu'

# Parse osu! beatmap file
beatmap_data = parse_osu_beatmap(osu_beatmap_file)

# Save beatmap to JSON file
save_beatmap_to_json(beatmap_data, 'osu_beatmap.json')
