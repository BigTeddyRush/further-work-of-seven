#!/bin/bash

# Output file
output_file="evaluation_jb/summary.json"

# Initialize the output JSON string
echo "{" > "$output_file"

# Iterate over each JSON file in the results directory
for json_file in ./results_jb/*.json; do
    # Extract the filename without the path
    file_name=$(basename "$json_file")

    # Temporary file to store counts
    temp_file=$(mktemp)

    # Read file line by line
    while IFS= read -r line; do
        # Extract the result
        result=$(echo "$line" | grep -o 'ProverResult\.[^"]*')
        
        if [[ -n "$result" ]]; then
            # Check if the result already exists in the temporary file
            if grep -q "^$result " "$temp_file"; then
                # Increment the existing count
                awk -v res="$result" '{ if ($1 == res) $2 = $2 + 1 } 1' "$temp_file" > "${temp_file}.tmp"
                mv "${temp_file}.tmp" "$temp_file"
            else
                # Add a new entry for this result with a count of 1
                echo "$result 1" >> "$temp_file"
            fi
        fi
    done < "$json_file"

    # Start building the output string for the current file
    output_str="  \"$file_name\": {"

    # Append each result and its count to the output string
    while read -r count_line; do
        result_type=$(echo "$count_line" | cut -d' ' -f1)
        result_count=$(echo "$count_line" | cut -d' ' -f2)
        output_str+=" \"$result_type\": $result_count,"
    done < "$temp_file"

    # Remove the trailing comma and close the current file's JSON object
    output_str="${output_str%,} },"
    
    # Append the output for the current file to the main JSON
    echo "$output_str" >> "$output_file"

    # Remove the temporary file
    rm "$temp_file"
done

# Remove trailing comma and close the JSON file
sed -i '' '$ s/,$//' "$output_file"
echo "}" >> "$output_file"

echo "Results written to $output_file"