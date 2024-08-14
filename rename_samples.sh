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

# Clear the log file if it exists
> "$log_file"

# Read the CSV file line by line
while IFS=, read -r project sample_id description barcode reads; do
  # Skip the header line
  if [ "$project" == "Project" ]; then
    continue
  fi

  # Remove double quotes from variables
  project=$(echo "$project" | sed 's/"//g')
  sample_id=$(echo "$sample_id" | sed 's/"//g')
  description=$(echo "$description" | sed 's/"//g')

  # Find matching FASTQ files in the directory
  for fastq_file in $fastq_directory/*_001.fastq.gz; do
    
    # Check if the file exists
    if [ -e "$fastq_file" ]; then
      
      # Extract the read number and other parts from the original filename
      base_name=$(basename "$fastq_file")
      read_number=$(echo "$base_name" | grep -oP '_R[12]_\d{3}.fastq.gz') # Extract paired end information i.e. _R1_001.fastq.gz
      #echo "base name is:$base_name and read number is:$read_number "

      # Ensure read_number is not empty
      #if [ -z "$read_number" ]; then
      #  echo "Error: read_number is empty for file $fastq_file"
      #  continue
      #fi
      
      sample_base=$(echo "$base_name" | sed "s/${read_number}//") # Extract Sample_ID and infix i.e. 10728-ES-10_S183
      #echo "sample base is:$sample_base"
      # Ensure sample_base is not empty
      #if [ -z "$sample_base" ]; then
      #  echo "Error: sample_base is empty for file $fastq_file"
      #  continue
      #fi
      
      sample_base_trimmed=$(echo "$sample_base" | sed 's/_S[0-9]\+//') # Removing infix from Sample_ID i.e. remove _S183 from 10728-ES-10_S183
      read_number_trimmed=$(echo "$read_number" | sed 's/_001//') # Modify read_number to remove _001
      #echo "sample base is: $sample_base"
      #echo " sample base trimmed is:$sample_base_trimmed and sample_ID:$sample_id"

      #echo "sample id is:$sample_id"
      # Check if sample_base matches the sample ID
      if [[ $sample_base_trimmed == $sample_id ]]; then  
        #echo "sample base trimmed is:$sample_base_trimmed and sample id is:$sample_id"
        
        # Create the new filename
        new_file=$fastq_directory/${description}${read_number_trimmed} # New file would look like this: fastqs_10728-ES/MRBA_ISO_2050_R1_001.fastq.gz
        #echo "old file looks like this:$fastq_file and the new file looks like this: $new_file"
        
        # Rename the file
        mv "$fastq_file" "$new_file"

        # Log the rename command
        echo "mv $fastq_file $new_file" >> "$log_file"
        echo "Renaming sample $fastq_file to $new_file"
  
      fi
    fi
  done
done < <(sed '1d' "$csv_file" | sed 's/"//g')  # Pipe to sed to remove double quotes from CSV lines except the header
echo "Renaming completed. Check $log_file for details."
