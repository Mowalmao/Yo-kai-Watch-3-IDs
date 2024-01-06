import json
import csv

def get_entry(entries, prefix_search):
    for entry in entries:
        if entry["Name"].startswith(prefix_search):
            return entry  # Return the first matching entry
    return None  # Return None if no matching entry is found

def search_variable(json_data, search_value):
    if search_value == 0:
        return "Unnamed"

    for entry in json_data.get("Entries", []):
        entry_name = entry.get("Name", "")
        
        if entry_name.startswith("NOUN_INFO_BEGIN") or entry_name.startswith("TEXT_INFO_BEGIN"):
            for child in entry.get("Children", []):
                variables = child.get("Variables", [])
                first_variable_value = variables[0].get("Value", None)
                
                if first_variable_value == search_value:
                    if entry_name.startswith("NOUN_INFO_BEGIN"):
                        return variables[5].get("Value", "Unnamed")
                    elif entry_name.startswith("TEXT_INFO_BEGIN"):
                        return variables[2].get("Value", "Unnamed")

    return "Unnamed"

def int_to_bytes(value):
    # Convert integer to bytes using two's complement representation
    if value < 0:
        value = (1 << (value.bit_length() + 1)) + value
    return value.to_bytes((value.bit_length() + 7) // 8, 'little')

def entry_to_csv(entry, header_names, variable_names, show_as_hex, search_text, data_text):
    # Create a CSV row with header names
    csv_row = ";".join(str(header) for header in header_names)

    # Add a newline character after the header names
    csv_row += "\n"

    for child in entry.get("Children", []):
        variables = child.get("Variables", [])
        row_values = []
        for name_or_index, show_hex, show_text in zip(variable_names, show_as_hex, search_text):
            if isinstance(name_or_index, int):
                value = variables[name_or_index]["Value"]
                if show_text:
                    row_values.append(search_variable(data_text, value))
                elif show_hex:
                    # Convert the integer to bytes and format as hex
                    hex_value = int_to_bytes(value).hex().upper()
                    row_values.append(hex_value)
                else:
                    row_values.append(str(value))
            else:
                variable = next((var["Value"] for var in variables if var["Name"] == name_or_index), "")
                if show_text:
                    row_values.append(search_variable(data_text, variable))
                elif show_hex:
                    # Convert the variable to bytes and format as hex
                    hex_variable = int_to_bytes(variable).hex().upper()
                    row_values.append(hex_variable)
                else:
                    row_values.append(str(variable))

        csv_row += ";".join(row_values)

        # Add a newline character after each child's values
        csv_row += "\n"

    return csv_row

# Load the JSON file
with open('chara_ability.json', 'r') as json_file:
    data = json.load(json_file)
    
# Load the JSON file
with open('chara_ability_en.json', 'r') as json_text_file:
    data_text = json.load(json_text_file)    

# Specify the prefix of the entry you're looking for
prefix_search = "CHARA_ABILITY_CONFIG_INFO_LIST_BEG"

# Get children of entries that start with the specified prefix
config = get_entry(data.get("Entries", []), prefix_search)

# Specify the header names and variable names/indices
header_names = ['SkillID', 'Name']
variable_names = ["SkillID", 'NameID']  # Adjust this list according to your needs

# Specify whether to format values as hex
show_as_hex = [True, True]

# Specify if the value text is to be searched
search_text = [False, True]

print(entry_to_csv(config, header_names, variable_names, show_as_hex, search_text, data_text))