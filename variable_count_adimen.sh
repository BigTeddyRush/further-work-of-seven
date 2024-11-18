#!/bin/bash

# Input TPTP file
input_file="adimen.sumo.tstp"

# Temporary file for storing matched variable counts
temp_file=$(mktemp)

# Extract variables within square brackets [], handling spaces and commas
grep -oP '\[\K[^\]]*(?=\])' "$input_file" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort | uniq -c > "$temp_file"

# Initialize an empty JSON object
json_output="{"

# Read temp file and construct JSON output
while IFS= read -r line; do
    count=$(echo "$line" | awk '{print $1}')
    variable=$(echo "$line" | awk '{print $2}')
    json_output+="\"$variable\": $count, "
done < "$temp_file"

# Remove trailing comma and space, add closing brace
json_output="${json_output%, }}"

# Print JSON to a file
echo "$json_output" > variables_count.json

# Cleanup
rm "$temp_file"

echo "Variable counts have been written to variables_count.json"