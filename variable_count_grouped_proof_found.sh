#!/bin/bash

# Output file for variable counts grouped by JSON file
variable_counts_output_file="evaluation/variable_counts_grouped_proof_found_timer.json"

# Initialize the output JSON string
echo "{" > "$variable_counts_output_file"

# Function to count variables within the brackets on the second line of a given file
count_variables() {
    local file_path=$1
    if [[ -f "$file_path" ]]; then
        # Read the contents of the second line
        second_line=$(sed -n '2p' "$file_path")

        # Extract content between the square brackets [ ]
        bracket_content=$(echo "$second_line" | sed -n 's/.*\[\([^]]*\)\].*/\1/p')

        # Count variables by splitting on commas and counting non-empty entries
        variable_count=$(echo "$bracket_content" | tr ',' '\n' | grep -c '[^[:space:]]')
        echo "$variable_count"
    else
        echo 0  # Return 0 if the file doesn't exist
    fi
}

# Iterate over each JSON file in the 'results' directory
for json_file in ./result_timer/*.json; do
    # Extract the filename without its path
    file_name=$(basename "$json_file")

    # Start building the output string for the current JSON file
    echo "  \"$file_name\": {" >> "$variable_counts_output_file"
    
    # Use jq to parse keys and values from the JSON file
    cat "$json_file" | jq -r 'to_entries[] | "\(.key)|\(.value|tostring)"' | while IFS='|' read -r file_path prover_result; do
        # Determine if prover_result is "ProverResult.PROOF_FOUND" or if it includes it in an array
        if [[ "$prover_result" == "ProverResult.PROOF_FOUND" ]] || [[ "$prover_result" == *"ProverResult.PROOF_FOUND"* ]]; then
            # Count the variables in the extracted file path
            variable_count=$(count_variables "$file_path")

            # Append the result to the JSON output under the current file
            echo "    \"$file_path\": $variable_count," >> "$variable_counts_output_file"
        fi
    done

    # Remove trailing comma for the current file section and close it
    sed -i '' -e '$ s/,$//' "$variable_counts_output_file"
    echo "  }," >> "$variable_counts_output_file"
done

# Remove trailing comma for the last JSON object and close it
sed -i '' -e '$ s/,$//' "$variable_counts_output_file"
echo "}" >> "$variable_counts_output_file"

echo "Variable counts grouped by JSON files written to $variable_counts_output_file"