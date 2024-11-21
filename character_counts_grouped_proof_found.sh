#!/bin/bash

# Output file for character counts excluding spaces
output_file="evaluation/character_counts_grouped_proof_found_timer.json"

# Initialize the output JSON string
echo "{" > "$output_file"

# Function to count all characters except spaces in a given file
count_characters() {
    local file_path=$1
    if [[ -f "$file_path" ]]; then
        # Count all characters except spaces
        character_count=$(tr -cd '[:graph:]' < "$file_path" | wc -c)
        echo "$character_count"
    else
        echo "File not found: $file_path"
        return 1
    fi
}

# Iterate over each JSON file in the 'results' directory
for json_file in ./result_timer/*.json; do
    # Extract the filename without its path
    file_name=$(basename "$json_file")

    # Start building the output string for the current JSON file
    echo "  \"$file_name\": {" >> "$output_file"

    # Use jq to parse keys and values from the JSON file
    cat "$json_file" | jq -r 'to_entries[] | "\(.key)|\(.value|tostring)"' | while IFS='|' read -r file_path prover_result; do
        # Check if the prover result is "ProverResult.PROOF_FOUND"
        if [[ "$prover_result" == "ProverResult.PROOF_FOUND" ]] || [[ "$prover_result" == *"ProverResult.PROOF_FOUND"* ]]; then
            # Count all non-space characters in the extracted file path
            character_count=$(count_characters "$file_path")
            
            if [ $? -eq 0 ]; then
                # Append the result to the JSON output under the current file
                echo "    \"$file_path\": $character_count," >> "$output_file"
            fi
        fi
    done

    # Remove trailing comma for the current file section and close it
    sed -i '' -e '$ s/,$//' "$output_file"
    echo "  }," >> "$output_file"
done

# Remove trailing comma for the last JSON object and close it
sed -i '' -e '$ s/,$//' "$output_file"
echo "}" >> "$output_file"

echo "Results written to $output_file"