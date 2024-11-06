#!/bin/bash

# Output file for storing matched lines
output_file="matched_lines_grouped.json"

# Initialize the output JSON string
echo "{" > "$output_file"

# Function to process each JSON file in the 'results' directory
for json_file in ./results/*.json; do
    # Extract the filename without its path
    file_name=$(basename "$json_file")

    # Initial grouping for this JSON file
    echo "  \"$file_name\": [" >> "$output_file"

    # Read JSON file line by line
    while IFS= read -r line; do
        # Check if the line contains "ProverResult.PROOF_FOUND"
        if echo "$line" | grep -q "ProverResult.PROOF_FOUND"; then
            # Extract the key and simplify it to the desired format
            key=$(echo "$line" | grep -oE '".+?"' | tr -d '"' | sed -E 's/.*\/(whiteBoxTruthTest[^.]*).*/\1/')

            # Search for the key in whiteBox.txt and append matched lines
            while IFS= read -r result; do
                if [[ -n $result ]]; then
                    # Append matched result as a separate JSON string
                    echo "    \"$(echo "$result" | sed 's/"/\\"/g')\"," >> "$output_file"
                fi
            done < <(grep "$key" whiteBox.txt)
        fi
    done < "$json_file"

    # Remove trailing comma for the current file section and close it
    sed -i '' -e '$ s/,$//' "$output_file"
    echo "  ]," >> "$output_file"
done

# Remove trailing comma for the last JSON object and close it
sed -i '' -e '$ s/,$//' "$output_file"
echo "}" >> "$output_file"

echo "Results written to $output_file"