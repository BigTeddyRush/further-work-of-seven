#!/bin/bash

# Output files for letter counts
output_file="letter_counts_grouped.json"
stats_output_file="letter_counts_stats.json"

# Initialize the output JSON strings
echo "{" > "$output_file"
echo "{" > "$stats_output_file"

# Function to count letters in a given file
count_letters() {
    local file_path=$1
    if [[ -f "$file_path" ]]; then
        letter_count=$(tr -cd '[:alpha:]' < "$file_path" | wc -c)
        echo "$letter_count"
    else
        echo 0  # Return 0 if the file doesn't exist (or handle as needed)
    fi
}

# Iterate over each JSON file in the 'results' directory
for json_file in ./results/*.json; do
    # Extract the filename without its path
    file_name=$(basename "$json_file")

    # Initialize variables to calculate stats
    min_count=-1
    max_count=0
    total_count=0
    count_entries=0

    # Start building the output string for the current JSON file
    echo "  \"$file_name\": {" >> "$output_file"
    
    # Read JSON file line by line
    while IFS= read -r line; do
        # Check if the line contains "ProverResult.PROOF_FOUND"
        if echo "$line" | grep -q "ProverResult.PROOF_FOUND"; then
            # Extract the key which contains the file path
            file_path=$(echo "$line" | grep -oE '".+?"' | head -n 1 | tr -d '"')
            # Count letters in the extracted file path
            letter_count=$(count_letters "$file_path")
            
            # Append the result to the JSON output under the current file
            echo "    \"$file_path\": $letter_count," >> "$output_file"

            # Update statistics
            if [[ $min_count -eq -1 || $letter_count -lt $min_count ]]; then
                min_count=$letter_count
            fi
            if [[ $letter_count -gt $max_count ]]; then
                max_count=$letter_count
            fi
            total_count=$((total_count + letter_count))
            ((count_entries++))
        fi
    done < "$json_file"

    # Remove trailing comma for the current file section and close it
    sed -i '' -e '$ s/,$//' "$output_file"
    echo "  }," >> "$output_file"

    # Calculate the mean
    if [[ $count_entries -gt 0 ]]; then
        mean_count=$((total_count / count_entries))
    else
        mean_count=0
    fi

    # Store the statistics for this file
    echo "  \"$file_name\": {" >> "$stats_output_file"
    echo "    \"min\": $min_count," >> "$stats_output_file"
    echo "    \"max\": $max_count," >> "$stats_output_file"
    echo "    \"mean\": $mean_count" >> "$stats_output_file"
    echo "  }," >> "$stats_output_file"
done

# Remove trailing comma for the last JSON objects and close them
sed -i '' -e '$ s/,$//' "$output_file"
sed -i '' -e '$ s/,$//' "$stats_output_file"
echo "}" >> "$output_file"
echo "}" >> "$stats_output_file"

echo "Results written to $output_file"
echo "Statistics written to $stats_output_file"