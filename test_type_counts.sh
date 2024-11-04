#!/bin/bash

# Input file containing the grouped matched lines
input_file="matched_lines_grouped.json"
# Output file to store the counts of test types
output_file="test_type_counts.json"

# Initialize the output JSON string
echo "{" > "$output_file"

# Temporary directory for storing interim results
temp_dir=$(mktemp -d)

# Function to handle cleanup
cleanup() {
    rm -rf "$temp_dir"
}
trap cleanup EXIT

# Use jq to parse the input JSON file
# Iterate over each JSON object
jq -c 'to_entries[]' "$input_file" | while IFS= read -r entry; do
    # Get the key (filename)
    json_file=$(echo "$entry" | jq -r '.key')
    
    # Temp storage for counts per file
    temp_counts_file="$temp_dir/${json_file}_counts.tmp"
    echo "{}" > "$temp_counts_file"
    
    # Iterate over each value (array of lines)
    echo "$entry" | jq -r '.value[]' | while IFS= read -r test_line; do
        # Extract the test type
        test_type=$(echo "$test_line" | awk -F ' - ' '{ print $3 }')
        
        # Continue only with valid test types
        if [[ -n "$test_type" ]]; then
            # Increment the count in a temporary file, using jq's ability to update JSON
            jq --arg key "$test_type" '.[$key] += 1' "$temp_counts_file" > "${temp_counts_file}.new" || echo "{\"$test_type\": 1}" > "${temp_counts_file}.new"
            mv "${temp_counts_file}.new" "$temp_counts_file"
        fi
    done

    # Let's add the file with its counts to the main output
    echo "  \"$json_file\": " >> "$output_file"
    cat "$temp_counts_file" >> "$output_file"
    echo "," >> "$output_file"
done

# Remove trailing comma for the last JSON object and close them
sed -i '' -e '$ s/,$//' "$output_file"
echo "}" >> "$output_file"

echo "Counts of test types written to $output_file"