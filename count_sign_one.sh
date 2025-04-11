#!/bin/bash

json_file="whitebox_candidates.json"
total=0

# Characters to count
chars='|'

# Extract file paths from the JSON and iterate
while read -r file_path; do
    # Remove quotes
    file_path="${file_path//\"/}"

    # Skip lines that aren't real paths
    [[ "$file_path" != .* ]] && continue

    if [[ -f "$file_path" ]]; then
        # Count all specified characters
        count=$(tr -cd "$chars" < "$file_path" | wc -c)
        total=$((total + count))
    fi
done < <(grep -oE '"[^"]+"' "$json_file")

echo "$total"
