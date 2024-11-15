#!/bin/bash

# Output file for variable counts grouped by JSON file
variable_counts_output_file="evaluation/signs_counts_grouped_proof_found.json"

# Initialize the output JSON string
echo "{" > "$variable_counts_output_file"

# Function to count specific characters (|, ?, !, ~, &) in the entire file
count_special_characters() {
    local file_path=$1
    if [[ -f "$file_path" ]]; then
        # Define the characters to count
        local characters='[|?!~&]'
        
        # Count occurrences of each character in the whole file
        character_count=$(grep -o "$characters" "$file_path" | wc -l)
        echo "$character_count"
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
        # Check if the prover result is "ProverResult.PROOF_FOUND" in either string or array form
        if [[ "$prover_result" == "ProverResult.PROOF_FOUND" ]] || [[ "$prover_result" == *"ProverResult.PROOF_FOUND"* ]]; then
            # Count the special characters in the extracted file path
            character_count=$(count_special_characters "$file_path")

            # Append the result to the JSON output under the current file
            echo "    \"$file_path\": $character_count," >> "$variable_counts_output_file"
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