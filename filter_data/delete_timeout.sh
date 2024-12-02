#!/bin/bash

# Input and output file paths
input_file="results/noAuto_union_n160_b20_k03_timer_proofObject_8000.json"
output_file="filtered_file_8000.json"

# Use jq to filter keys based on the value content
jq 'to_entries
    | map(select(.value[0] != "ProverResult.TIME_OUT"))
    | from_entries' "$input_file" > "$output_file"

echo "Filtered JSON saved to $output_file"