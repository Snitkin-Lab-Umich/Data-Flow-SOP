#!/bin/bash

# Author Dhatri Badri

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <fastq_directory> <DemuxStats_*.csv>"
  exit 1
fi

# Assign arguments to variables
fastq_directory=$1
csv_file=$2
log_file="renamed_file_commands.sh"

# Remove any trailing slashes from the fastq_directory path
fastq_directory=$(echo "$fastq_directory" | sed 's:/*$::')

# Clear the log file if it exists
> "$log_file"

# Flag to check if any file was renamed
rename_fastq=false

# Read the CSV file line by line, skipping the header
while IFS=, read -r project sample_id description barcode reads; do
    # Skip the header line
    if [ "$project" == "Project" ]; then
        continue
    fi

    # Clean sample_id
    project=$(echo "$project" | sed 's/"//g')
    sample_id=$(echo "$sample_id" | xargs | sed 's/"//g')
    description=$(echo "$description" | sed 's/"//g')

    #echo "Processing sample: $sample_id"  

    # Find matching FASTQ files in the directory
    for fastq_file in "$fastq_directory"/*_R[12]_*.fastq.gz; do
        # Check if the file exists
        if [ -e "$fastq_file" ]; then
            base_name=$(basename "$fastq_file")
            read_number=$(echo "$base_name" | grep -oP '_R[12]')
            sample_base=$(echo "$base_name" | xargs | sed -E "s/_R[12]_.*//")

            #echo "Base Name: $sample_base, Sample ID: $sample_id, Read Number: $read_number"  
            
            # Check if sample_base matches the sample ID from the CSV
            if [[ $sample_base == $sample_id ]]; then  
                new_file="${fastq_directory}/${description}${read_number}.fastq.gz"
                echo "Renaming sample $fastq_file to $new_file"
                echo "mv $fastq_file $new_file" >> "$log_file"
                
                mv "$fastq_file" "$new_file"
                rename_fastq=true
            fi
        fi
    done
done < <(sed '1d' "$csv_file" | sed 's/"//g') 


# Check if any files were renamed
if ! $rename_fastq; then
  echo "Error: No files were renamed!"
  exit 1
fi

echo "Renaming completed. Check $log_file for details."
