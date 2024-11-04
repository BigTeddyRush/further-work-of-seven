#!/bin/bash

# Output file for letter counts
output_file="letter_counts_grouped.json"

# Initialize the output JSON string
echo "{" > "$output_file"

# Function to count letters in a given file
count_letters() {
    local file_path=$1
    if [[ -f "$file_path" ]]; then
        # Count letters and store in a variable
        letter_count=$(tr -cd '[:alpha:]' < "$file_path" | wc -c)
        echo "$letter_count"
    else
        echo "File not found: $file_path"
    fi
}

# Iterate over each JSON file in the 'results' directory
for json_file in ./results/*.json; do
    # Extract the filename without its path
    file_name=$(basename "$json_file")

    # Start building the output string for the current JSON file
    echo "  \"$file_name\": {" >> "$output_file"
    
    # Read JSON file line by line
    while IFS= read -r line; do
        # Check if the line contains "ProverResult.PROOF_FOUND"
        if echo "$line" | grep -q "ProverResult.PROOF_FOUND"; then
            # Extract the key which contains the file path
            file_path=$(echo "$line" | grep -oE '".+?"' | head -n 1 | tr -d '"')
            # Call the function to count letters in the extracted file path
            letter_count=$(count_letters "$file_path")
            
            # Append the result to the JSON output under the current file
            echo "    \"$file_path\": $letter_count," >> "$output_file"
        fi
    done < "$json_file"

    # Remove trailing comma for the current file section and close it
    sed -i '' -e '$ s/,$//' "$output_file"
    echo "  }," >> "$output_file"
done

# Remove trailing comma for the last JSON object and close it
sed -i '' -e '$ s/,$//' "$output_file"
echo "}" >> "$output_file"

echo "Results written to $output_file"