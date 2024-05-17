#Use this script to take large, unfortmatted JSON files, and format them quickly.

import json

def prettify_json(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            raw_data = file.read()
            json_objects = []
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(raw_data):
                obj, pos = decoder.raw_decode(raw_data, pos)
                json_objects.append(obj)
                # Skip any whitespace between JSON objects
                pos = raw_data.find('{', pos)
                if pos == -1:
                    break

        with open(output_file_path, 'w', encoding='utf-8') as file:
            for obj in json_objects:
                json.dump(obj, file, indent=4, ensure_ascii=False)
                file.write('\n')

        print(f"JSON file has been prettified and saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_file = 'path/to/your/large_input.json'
output_file = 'path/to/your/pretty_output.json'
prettify_json(input_file, output_file)
