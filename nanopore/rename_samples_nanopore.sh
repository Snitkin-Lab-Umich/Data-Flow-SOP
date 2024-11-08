#!/bin/bash
#set -x  # This enables debugging output

# Author Dhatri Badri

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <fastq_directory> <*_sample_lookup.csv> <long_read_batch_name>"
  exit 1
fi

# Assign arguments to variables
fastq_directory=$1
csv_file=$2
log_file="renamed_file_commands.sh"
batch_name=$3

# Clear the log file if it exists
> "$log_file"

# Use awk to filter lines in CSV matching the batch name and skip the header line
awk -F',' -v batch="$batch_name" 'NR > 1 && $4 == batch { 
    print $0 
}' "$csv_file" | while IFS=',' read -r sample_id genome_id submission_id batch; do
    # Debug output to confirm reading the correct values
    #echo "Processing sample ID: $submission_id, Genome ID: $genome_id"

    # Find matching FASTQ files in the directory
    for fastq_file in "$fastq_directory"/*.fastq.gz; do
      
      # Check if the file exists
      if [ -e "$fastq_file" ]; then
        
        # Extract the base name without the extension
        base_name=$(basename "$fastq_file" .fastq.gz)

        # Debug output to confirm base name and submission ID
        #echo "Found FASTQ file: $fastq_file (base name: $base_name) matching submission ID: $submission_id"

        # Check if the base name matches the submission ID
        if [[ "$base_name" == "$submission_id" ]]; then  

          # Create the new filename
          new_file="$fastq_directory/${genome_id}.fastq.gz"
          
          # Rename the file 
          if mv "$fastq_file" "$new_file"; then

            # Log the rename command
            echo "Renaming sample $fastq_file to $new_file"
            echo "mv $fastq_file $new_file" >> "$log_file"
          
          else
            echo "Error renaming $fastq_file"
            exit 1
          fi
        fi
      fi
    done
done

# Check if the log file exists and has content
if [ -s "$log_file" ]; then
  echo "Renaming completed. Check $log_file for details."
else
  echo "Error renaming files."
fi
