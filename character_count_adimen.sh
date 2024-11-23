#!/bin/bash

input_file="adimen.sumo.tstp"
output_file="axiom_counts_sumo.json"

# Initialize the JSON file with an opening bracket
echo "{" > "$output_file"

# Variable to track if this is the first entry
first_entry=true

# Iterate through the axioms in the file
grep -oP '^fof\(\K[^,]+' "$input_file" | while read axiom_name; do
    # Define the start and end patterns for the axiom, with a space before the axiom name and escaping parentheses
    start_pattern="fof\\( $axiom_name,"
    end_pattern="\\)."

    # Extract the axiom content and calculate the character count
    axiom_content=$(awk "/$start_pattern/,/$end_pattern/" "$input_file")

    # Calculate character count ignoring multiple lines
    char_count=$(echo "$axiom_content" | tr -d '\n' | wc -c)

    # Check if this is the first entry
    if [ "$first_entry" = false ]; then
        echo "," >> "$output_file"  # Add a comma separator for JSON format
    fi

    # Store the result as a JSON object
    echo -e "\t\"$axiom_name\": $char_count" >> "$output_file"
    
    # After the first entry, set first_entry to false
    first_entry=false
done

# Close the JSON object with a closing bracket
echo -e "\n}" >> "$output_file"

echo "Axiom character counts have been stored in $output_file."