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
    #echo "Processing description: $description" 

    # Find matching FASTQ files in the directory
    for fastq_file in "$fastq_directory"/*.fastq.gz; do
        # Check if the file exists
        if [ -e "$fastq_file" ]; then
            base_name=$(basename "$fastq_file")

            # Check if the file ends with '_001' and remove it if present
            if [[ "$base_name" == *_001.fastq.gz ]]; then
                base_name=$(echo "$base_name" | sed 's/_001//')
            fi
            
             # Check if the base_name contains '_SXXX' preceding '_R1' or '_R2' and remove '_SXXX'
            if [[ "$base_name" =~ _S[0-9]+_R[12] ]]; then
                new_base_name=$(echo "$base_name" | sed -E 's/_S[0-9]+//')
            else
                new_base_name="$base_name"  # If no '_SXXX' found, keep the base name unchanged
            fi

            # Display base name before and after
            #echo "Original Base Name: $base_name"
            #echo "Updated Base Name: $new_base_name"

            read_number=$(echo "$new_base_name" | grep -oP 'R[12]')
            sample_base=$(echo "$new_base_name" | xargs | sed -E "s/_R[12].*//")

            #echo "read num is: $read_number and sample base is $sample_base"
            # Check if sample_base matches the sample ID from the CSV
            if [[ $sample_base == $sample_id ]]; then  
                new_file="${fastq_directory}/${description}_${read_number}.fastq.gz"
                
                # echo "Renaming sample $fastq_file to $new_file"
                # echo "mv $fastq_file $new_file" >> "$log_file"
                # rename_fastq=true
                if mv "$fastq_file" "$new_file":
                    echo "Renaming sample $fastq_file to $new_file"
                    echo "mv $fastq_file $new_file" >> "$log_file"
                    rename_fastq=true
                fi
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
