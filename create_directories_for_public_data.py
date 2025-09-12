#!/usr/bin/env python3

import os
import argparse

def create_directory(path):
    """Create a directory if it doesn't already exist."""
    os.makedirs(path, exist_ok=True)
    print(f"Created: {path}")

def main():
    parser = argparse.ArgumentParser(description="Create public dataset directory structure.")

    parser.add_argument("--dest_path", required=True,
                        help="Base destination path, excluding project name (e.g., /nfs/turbo/umms-esnitkin/)")
    
    parser.add_argument("--project_name", required=True,
                        help="Project folder name (e.g., Project_MRSA)")
    
    parser.add_argument("--parent_dir_name", required=True,
                        help="Name of parent folder holding raw/assembly data (e.g., 2025-02-17_all-USA300-MRSA_NCBI)")

    parser.add_argument("--data_type", choices=["raw_fastq", "assembly"], required=True,
                        help="Choose either raw_fastq or assembly")
    
    parser.add_argument("--folder_names_illumina", required=True,
                        help="Comma-separated folder names for illumina data (e.g., 2025-04-16_USA300-MRSA,2025-05-16_USA300-MRSA)")

    args = parser.parse_args()

    # Base paths
    project_path = os.path.join(args.dest_path, args.project_name)
    public_data_path = os.path.join(project_path, "Public_datasets")
    parent_dir_path = os.path.join(public_data_path, args.parent_dir_name)

    # Create parent directory if not present
    create_directory(parent_dir_path)

    # Create shared directories
    create_directory(os.path.join(parent_dir_path, "assembly", "illumina", "passed_qc_assemblies"))
    create_directory(os.path.join(parent_dir_path, "clean_fastq_qc_pass_samples"))

    # Create individual illumina folders based on data type
    folder_list = [f.strip() for f in args.folder_names_illumina.split(",")]

    for folder_name in folder_list:
        illumina_subdir = os.path.join(parent_dir_path, "illumina", folder_name)

        if args.data_type == "raw_fastq":
            create_directory(os.path.join(illumina_subdir, "raw_fastq"))
            create_directory(os.path.join(illumina_subdir, "passed_qc_samples"))
            create_directory(os.path.join(illumina_subdir, "failed_qc_samples"))

        elif args.data_type == "assembly":
            create_directory(os.path.join(illumina_subdir, "assembly_downloads"))
            create_directory(os.path.join(illumina_subdir, "failed_qc_assemblies"))

if __name__ == "__main__":
    main()
