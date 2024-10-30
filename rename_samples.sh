#!/bin/bash

# Author: Dhatri Badri

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <fastq_directory> <DemuxStats_*.csv>"
  exit 1
fi

# Assign arguments to variables
fastq_directory=$1
csv_file=$2
log_file="renamed_file_commands.sh"
rename_fastq=false

# Check if the fastqs directory exists
if [[ ! -d "$fastq_directory" ]]; then
    echo "Error: Directory '$fastq_directory' does not exist!"
    exit 1
fi

# Check if the Demux file for core/plasmisaurus exists
if [[ ! -f "$csv_file" ]]; then
    echo "Error: File '$csv_file' does not exist!"
    exit 1
fi

# Remove any trailing slashes from the fastq_directory path
fastq_directory=$(echo "$fastq_directory" | sed 's:/*$::')

# Clear the log file if it exists
> "$log_file"

# Ensure the CSV file ends with a newline
if ! tail -c 1 "$csv_file" | read -r _; then
  echo "" >> "$csv_file"
fi

# Convert the CSV file to Unix format
dos2unix "$csv_file"

# Loop through FASTQ files in the directory
for fastq_file in "$fastq_directory"/*.fastq.gz; do
    
    base_name=$(basename "$fastq_file")

    # If file ends with '_001', remove it
    if [[ "$base_name" == *_001.fastq.gz ]]; then
        base_name=$(echo "$base_name" | sed 's/_001//')
    fi

    # Read the CSV file depending on its structure
    column_count=$(head -n 1 "$csv_file" | awk -F',' '{print NF}')

    if [[ "$column_count" -eq 5 ]]; then
        # Handle 5-column CSV
        while IFS=, read -r project sample_id description barcode reads; do
            # Skip header
            if [ "$project" == "Project" ]; then 
                continue
            fi

            # Clean sample_id and description
            sample_id=$(echo "$sample_id" | xargs | sed 's/"//g')
            description=$(echo "$description" | sed 's/"//g')
           
            # Handle _SXXX in FASTQ filenames
            if [[ "$base_name" =~ _S[0-9]+_R[12] ]]; then
                new_base_name=$(echo "$base_name" | sed -E 's/_S[0-9]+//')
            else
                new_base_name="$base_name"  # Keep base name unchanged if no _SXXX
            fi

            read_number=$(echo "$new_base_name" | grep -oP 'R[12]')
            sample_base=$(echo "$new_base_name" | sed -E "s/_R[12].*//")

            # If the sample_base matches the sample ID from the CSV
            if [[ "$sample_base" == "$sample_id" ]]; then
                new_file="${fastq_directory}/${description}_${read_number}.fastq.gz"
                if mv "$fastq_file" "$new_file"; then
                    echo "Renaming sample $fastq_file to $new_file"
                    echo "mv $fastq_file $new_file" >> "$log_file"
                    rename_fastq=true
                    #break  # break the CSV reading loop
                else
                    echo "Error renaming $fastq_file"
                    exit 1
                fi
            fi
        done < "$csv_file"

    elif [[ "$column_count" -eq 4 ]]; then   
        # Handle 4-column CSV
        while IFS=, read -r sample_id genome_id submission_id batch; do
            # Clean genome_id and submission_id
            genome_id=$(echo "$genome_id" | xargs | sed 's/"//g')
            submission_id=$(echo "$submission_id" | sed 's/"//g')

            # Remove _L001 and _SXXX from the base name 
            modified_base_name=$(echo "$base_name" | sed -E 's/_L001//; s/_S[0-9]+//; s/_R[12].*//')

            read_number=$(echo "$base_name" | grep -oP 'R[12]')

            if [[ "$modified_base_name" == "$submission_id" ]]; then
                new_file="$fastq_directory/${genome_id}_${read_number}.fastq.gz"
                if mv "$fastq_file" "$new_file"; then
                    echo "Renaming sample $fastq_file to $new_file"
                    echo "mv $fastq_file $new_file" >> "$log_file"
                    rename_fastq=true
                    break  # break the CSV reading loop
                else
                    echo "Error renaming $fastq_file"
                    exit 1
                fi
            fi
        done < "$csv_file"

    elif [[ "$column_count" -eq 7 ]]; then
        # Handle 7-column CSV
        while IFS=, read -r project sample_id description barcode cf_sample_id poolid reads; do
            # Skip header
            if [ "$project" == "Project" ]; then
                continue
            fi

            # Clean sample_id and description
            sample_id=$(echo "$sample_id" | xargs | sed 's/"//g')
            description=$(echo "$description" | sed 's/"//g')

            # Handle _SXXX in FASTQ filenames
            if [[ "$base_name" =~ _S[0-9]+_R[12] ]]; then
                new_base_name=$(echo "$base_name" | sed -E 's/_S[0-9]+//')
            else
                new_base_name="$base_name"  # Keep base name unchanged if no _SXXX
            fi

            read_number=$(echo "$new_base_name" | grep -oP 'R[12]')
            sample_base=$(echo "$new_base_name" | sed -E "s/_R[12].*//")

            # If the sample_base matches the sample_id from the CSV
            if [[ "$sample_base" == "$sample_id" ]]; then
                new_file="${fastq_directory}/${description}_${read_number}.fastq.gz"
                if mv "$fastq_file" "$new_file"; then
                    echo "Renaming sample $fastq_file to $new_file"
                    echo "mv $fastq_file $new_file" >> "$log_file"
                    rename_fastq=true
                    #break  # break the CSV reading loop
                else
                    echo "Error renaming $fastq_file"
                    exit 1
                fi
            fi
        done < "$csv_file"
    else
        echo "There are $column_count columns and this script only supports CSV files with 4,5 and 7 columns."
        exit 1
    fi

done

# Check if any files were renamed
if ! $rename_fastq; then
    echo "Error: No files were renamed!"
    exit 1
else
    echo "Renaming completed. Check $log_file for details."
fi