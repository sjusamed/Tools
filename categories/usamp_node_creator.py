import pandas as pd
import numpy as np
import re

def load_data(file_path):
    """Load CSV data with appropriate encoding."""
    return pd.read_csv(file_path, encoding='ISO-8859-1')

def clean_categories(data, category_columns):
    """Extract categories and clean parentheses."""
    category_list = []
    for index, row in data.iterrows():
        for i, col in enumerate(category_columns):
            if pd.notna(row[col]):
                category_list.append((row[col], i+1))  # (category name, level)

    # Remove parentheses from category names
    category_list = [(re.sub(r"\s*\([^)]*\)", "", cat).strip(), level) for cat, level in category_list]
    # Remove duplicates
    return list(set(category_list))

def generate_ids(category_list):
    """Generate unique IDs with level-specific prefixes."""
    id_dict = {}
    for cat, level in category_list:
        prefix = level  # prefix based on category level
        while True:
            new_id = f"{prefix}{np.random.randint(10000, 99999)}"  # 5-digit ID
            if new_id not in id_dict.values():  # ensure ID is unique
                id_dict[cat] = new_id
                break
    return id_dict

def save_to_csv(data, output_file_path):
    """Save data to CSV."""
    data.to_csv(output_file_path, index=False)

# Set the paths and columns
file_path = 'path_to_your_file.csv'
output_file_path = 'path_to_output_file.csv'
category_columns = ['Main Category', 'Category', 'Sub-Category', 'Sub-Sub-Category', 'Sub-Sub-Sub-Category']

# Process the data
data = load_data(file_path)
category_list = clean_categories(data, category_columns)
id_map = generate_ids(category_list)
final_df = pd.DataFrame(list(id_map.items()), columns=['Category Name', 'usamp_node'])

# Save the result
save_to_csv(final_df, output_file_path)
print(f"Data saved to {output_file_path}")
