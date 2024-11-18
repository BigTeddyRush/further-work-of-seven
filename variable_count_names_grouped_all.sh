#!/bin/bash

# Output file for variable counts grouped by JSON file
variable_counts_output_file="evaluation/variable_count_names_grouped_all.json"

# Initialize the output JSON string
echo "{" > "$variable_counts_output_file"

# Load the variables and their values from ./variables_count.json into an associative array
declare -A variable_value_map
while IFS=":" read -r key value; do
    # Strip quotes from keys and values
    key=$(echo "$key" | sed 's/[[:space:]]*"\(.*\)"[[:space:]]*/\1/')
    value=$(echo "$value" | sed 's/[[:space:]]*\([0-9]*\),*/\1/')
    variable_value_map["$key"]="$value"
done < <(jq -r 'to_entries[] | "\(.key):\(.value)"' ./variables_count.json)

# Function to compute the sum of values for variables within TPTP logic format
sum_variable_values() {
    local file_path=$1
    if [[ -f "$file_path" ]]; then
        # Read the contents of the second line (or any other relevant lines)
        tptp_content=$(sed -n '2p' "$file_path")

        # Extract variables in the form of quantified variables or predicates
        variables=$(echo "$tptp_content" | grep -oP '(?<=\?\[)[A-Za-z0-9_]+(?=\])|\b[A-Za-z0-9_]+\b')

        # Initialize sum
        sum=0

        # Iterate over each extracted variable, look up its value and add to sum
        for variable in $variables; do
            # Check existence and add its value to sum
            if [[ -n "${variable_value_map[$variable]}" ]]; then
                sum=$((sum + variable_value_map[$variable]))
            fi
        done

        echo "$sum"
    else
        echo 0  # Return 0 if the file doesn't exist
    fi
}

# Iterate over each JSON file in the 'results' directory
for json_file in ./results/*.json; do
    # Extract the filename without its path
    file_name=$(basename "$json_file")

    # Start building the output string for the current JSON file
    echo "  \"$file_name\": {" >> "$variable_counts_output_file"

    # Use jq to parse keys and values from the JSON file
    cat "$json_file" | jq -r 'to_entries[] | "\(.key)|\(.value|tostring)"' | while IFS='|' read -r file_path prover_result; do

        # Compute the sum of variable values in the extracted file path
        variable_sum=$(sum_variable_values "$file_path")

        # Append the result to the JSON output under the current file
        echo "    \"$file_path\": $variable_sum," >> "$variable_counts_output_file"

    done

    # Remove trailing comma for the current file section and close it
    sed -i '$ s/,$//' "$variable_counts_output_file"
    echo "  }," >> "$variable_counts_output_file"
done

# Remove trailing comma for the last JSON object and close it
sed -i '$ s/,$//' "$variable_counts_output_file"
echo "}" >> "$variable_counts_output_file"

echo "Variable value sums grouped by JSON files written to $variable_counts_output_file"