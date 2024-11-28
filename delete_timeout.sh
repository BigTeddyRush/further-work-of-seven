#!/bin/bash

# Input and output file paths
input_file="results/satauto_whitebox_union_n160_b20_k30_timer_withA12_withProofObject.json"
output_file="filtered_file_satauto.json"

# Use jq to filter keys based on the value content
jq 'to_entries
    | map(select(.value[0] != "ProverResult.TIME_OUT"))
    | from_entries' "$input_file" > "$output_file"

echo "Filtered JSON saved to $output_file"