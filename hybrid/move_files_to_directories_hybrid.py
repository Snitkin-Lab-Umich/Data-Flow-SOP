import os
import shutil
import argparse
import csv
import sys

def validate_path(path):
    while not os.path.isdir(path):
        path = input(f"The path '{path}' does not exist. Please enter a valid path: ")
    return path

def validate_file(path):
    while not os.path.exists(path):
        path = input(f"The path '{path}' does not exist. Please enter a valid path to samples file: ")
    return path

def move_samples_nanosake(Nanosake_results_path, samples):
    Nanosake_results_path = os.path.normpath(Nanosake_results_path)
    hybrid_dir = os.path.dirname(Nanosake_results_path)

    with open(samples, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                long_read = row["barcode_id"]
                short_read = row["sample_id"]

    all_files_moved = True
    with open(samples, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                long_read = row["barcode_id"]
                short_read = row["sample_id"]
                nanosake_dir = next((d for d in os.listdir(hybrid_dir) if d.endswith('_Nanosake')), None)
                if nanosake_dir:
                    
                    # Move prokka dir
                    prokka_dir = os.path.join(hybrid_dir, nanosake_dir, "prokka", long_read, short_read)
                    if os.path.isdir(prokka_dir):
                        dest_dir = os.path.join(hybrid_dir, "prokka")
                        os.makedirs(dest_dir, exist_ok=True)
                        prokka_dest_dir = os.path.join(hybrid_dir, "prokka", long_read, short_read)
                        shutil.move(prokka_dir, prokka_dest_dir)
                    else:
                        print(f"\nProkka directory not found for: {prokka_dir}")
                        all_files_moved = False

                    # Move polypolish dir
                    polypolish_dir = os.path.join(hybrid_dir, nanosake_dir, "polypolish", long_read, short_read)
                    polypolish_file = f"{short_read}_flye_medaka_polypolish.fasta"
                    polypolish_file_path = os.path.join(polypolish_dir, polypolish_file)
                    if os.path.isfile(polypolish_file_path):
                        dest_dir = os.path.join(hybrid_dir, "polypolish", long_read, short_read)
                        os.makedirs(dest_dir, exist_ok=True)
                        shutil.move(polypolish_file_path, dest_dir)
                    else:
                        print(f"\nPolypolish directory not found here: {polypolish_file_path}.")
                        all_files_moved = False
                    
                    # Move quast dir
                    quast_dir = os.path.join(hybrid_dir, nanosake_dir, "quast", long_read, short_read, f"{short_read}_flye_medaka_polypolish")
                    if os.path.isdir(quast_dir):
                        dest_dir = os.path.join(hybrid_dir, "quast")
                        os.makedirs(dest_dir, exist_ok=True)
                        quast_dest_dir = os.path.join(hybrid_dir, "quast", long_read, short_read, f"{short_read}_flye_medaka_polypolish")
                        shutil.move(quast_dir, quast_dest_dir)
                    else:
                        print(f"\nQuast directory not found for: {quast_dir}")
                        all_files_moved = False
                
                else:
                    print(f"Are you sure you named your Nansoake run correctly? Your run folder name is: {nanosake_dir}")
                    all_files_moved = False

    if all_files_moved:
        print("\nYay, all specified samples have been moved to the hybrid directory successfully!")
    else:
        print("\nSome Nanosake output files were not moved successfully. Please check the log messages above and correct any issues.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and organize Nanosake data.")
    parser.add_argument("--samples_path", required=True, help="Path to samples sheet in scratch directory (e.g., /scratch/esnitkin_root/esnitkin1/dhatrib/Nanosake/config/samples.csv)")
    parser.add_argument("--Nanosake_results_path", required=True, help="Path to Nanosake results in hybrid directory (e.g., /nfs/turbo/umms-esnitkin/Project_MDHHS_genomics/Sequence_data/assembly/hybrid/2024_10_01_Project_MDHHS_genomics_Nanosake)")

    args = parser.parse_args()

    samples_path = validate_file(args.samples_path)
    results_path = validate_path(args.Nanosake_results_path)

    # Move passed samples after processing
    move_samples_nanosake(results_path, samples_path)