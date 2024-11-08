import os
import shutil
import argparse
import csv
import sys

def validate_path(path):
    while not os.path.isdir(path):
        path = input(f"The path '{path}' does not exist. Please enter a valid path: ")
    return path

def setup_directories(batch_info_path):
    # Normalize the batch_info_path by removing any trailing slashes
    batch_info_path = os.path.normpath(batch_info_path)
    nanopore_dir = os.path.dirname(batch_info_path)
    sequence_data_dir = os.path.dirname(nanopore_dir)


    # Define the directory paths based on the corrected structure
    dirs = {
        "raw_fastq_dir": os.path.join(batch_info_path, "raw_fastq"),
        "failed_qc_samples_dir": os.path.join(batch_info_path, "failed_qc_samples"),
        "passed_qc_samples_dir": os.path.join(batch_info_path, "passed_qc_samples"),
        "clean_fastq_qc_pass_samples_dir": os.path.join(nanopore_dir, "clean_fastq_qc_pass_samples"),
        "assembly_dir": os.path.join(sequence_data_dir, "assembly", "ONT")
    }

    # Create the directories if they don't exist
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    return dirs

def setup_files(batch_info_path, results_path):
    batch_info_path = os.path.normpath(batch_info_path)
    nanopore_dir = os.path.dirname(batch_info_path)

    # Define the file paths
    files = {
        "failed_samples_file": os.path.join(batch_info_path, "failed_samples.txt"),
        "passed_samples_file": os.path.join(batch_info_path, "passed_samples.txt"),
        "missing_samples_file": os.path.join(batch_info_path, "missing_samples.txt"),
        "master_qc_summary_file": os.path.join(nanopore_dir, "master_qc_summary.csv")
    }

    nano_qc_folder_name = os.path.basename(os.path.normpath(results_path))
    
    qc_summary_file = os.path.join(results_path, f"{nano_qc_folder_name}_report/{nano_qc_folder_name}_report.csv")

    if not os.path.isfile(qc_summary_file):
        print(f"QC summary file not found at '{qc_summary_file}'! Are you sure you ran nanoQC entirely?")
        exit(1)
    else:
        for f in files.values():
            if not os.path.exists(f):
                open(f, 'a').close()
                if f == files["master_qc_summary_file"]:
                    print(f"\nCreated master QC summary file at: {f}")
        
        with open(files["missing_samples_file"], 'w') as f:
            f.write("missing_sample,which_folder\n")

    return files, qc_summary_file


def move_samples_to_dirs(dirs, files, qc_summary_file): #results_path, batch_info_path,

    samples_moved = True  # Initialize the flag as True

    try:
        with open(qc_summary_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            samples_processed = 0

            for row in reader:
                sample = row["sample_long_read"]
                qc_check = row["qc_check"]

                #long_read = f"{sample}.fastq.gz"
                long_read_path = os.path.join(dirs["raw_fastq_dir"], f"{sample}.fastq.gz")
                #passed_qc_dir = os.path.join(dirs["passed_qc_samples_dir"])
                #failed_qc_dir = os.path.join(dirs["failed_qc_samples_dir"])
                dest_dir = dirs["passed_qc_samples_dir"] if qc_check == "PASS" else dirs["failed_qc_samples_dir"]

                if os.path.isfile(long_read_path):
                    os.makedirs(dest_dir, exist_ok=True)
                    #dest_path = dest_dir
                    shutil.move(long_read_path, dest_dir)

                    # Remove the empty sample directory if it exists
                    #sample_dir = os.path.join(dirs["raw_fastq_dir"], sample)
                    #if os.path.isdir(sample_dir) and not os.listdir(sample_dir):
                    #    os.rmdir(sample_dir)

                    if qc_check == "PASS":
                        with open(files["passed_samples_file"], 'a') as f:
                            f.write(f"{sample}\n")
                    elif qc_check == "FAIL":
                        with open(files["failed_samples_file"], 'a') as f:
                            f.write(f"{sample}\n")

                    samples_processed += 1
                else:
                    with open(files["missing_samples_file"], 'a') as f:
                        f.write(f"{sample},{dest_dir}\n")

        # Append the QC summary file to the master QC summary file
        try:
            with open(qc_summary_file, newline='') as csvfile:
                reader = csv.reader(csvfile)
                with open(files["master_qc_summary_file"], 'a', newline='') as masterfile:
                    writer = csv.writer(masterfile)
                    for i, row in enumerate(reader):
                        if i == 0:
                            if os.path.getsize(files["master_qc_summary_file"]) == 0:
                                writer.writerow(row)  # Write header only if master file is empty
                        else:
                            writer.writerow(row)
            print(f"\nAppended {qc_summary_file} to {files['master_qc_summary_file']}")
        except Exception as e:
            raise RuntimeError(f"Failed to append QC summary to master file: {e}")

        with open(files["missing_samples_file"], 'r') as f:
            lines = f.readlines()

        if len(lines) > 1:
            print(f"Some files are missing and are listed in {files['missing_samples_file']}.")
            samples_moved = False  # Set flag to False if there are missing files
        else:
            os.remove(files["missing_samples_file"])

        # Move the results folder to the batch_info_path after detection of qc summary file
        #shutil.move(results_path, batch_info_path)

        if samples_moved:
            print("Yay, passed and failed sample files were transferred to their respective folders successfully!")
        else:
            raise RuntimeError("Not all sample files were moved successfully. Check log message(s) above.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def move_passed_samples_nano_qc(batch_info_path, clean_fastq_qc_pass_samples_dir, assembly_dir):
    passed_samples_file = os.path.join(batch_info_path, "passed_samples.txt")
    if not os.path.isfile(passed_samples_file):
        print("No passed_samples.txt file found! Are you sure you moved the raw fastq reads into their respective directories (passed and failed qc folders)?")
        exit(1)

    all_files_moved = True
    with open(passed_samples_file, 'r') as f:
        for sample in f:
            sample = sample.strip()
            nano_qc_dir = next((d for d in os.listdir(batch_info_path) if d.endswith('_nanoQC')), None)
            if nano_qc_dir:
                
                # Move trimmed sample 
                trimmed_sample = os.path.join(batch_info_path, nano_qc_dir, "filtlong", sample, f"{sample}.trimmed.fastq.gz")
                #trimmed_long_read = f"{sample}.trimmed.fastq.gz"
                #trimmed_long_read_path = os.path.join(fitlong_dir, trimmed_long_read)
                if os.path.isfile(trimmed_sample):
                    #dest_dir = clean_fastq_qc_pass_samples_dir
                    #os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(trimmed_sample, clean_fastq_qc_pass_samples_dir)
                else:
                    print(f"\nTrimmed long read not found for sample: {sample} in this path: {trimmed_sample}")
                    all_files_moved = False
                
                # Move prokka dir
                prokka_dir = os.path.join(batch_info_path, nano_qc_dir, "prokka", sample)
                if os.path.isdir(prokka_dir):
                    dest_dir = os.path.join(assembly_dir, "prokka")
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(prokka_dir, dest_dir)
                else:
                    print(f"\nProkka directory not found for sample: {sample}")
                    all_files_moved = False

                # Move medaka dir
                medaka_dir = os.path.join(batch_info_path, nano_qc_dir, "medaka", sample)
                medaka_file = f"{sample}_medaka.fasta"
                medaka_file_path = os.path.join(medaka_dir, medaka_file)
                if os.path.isfile(medaka_file_path):
                    dest_dir = os.path.join(assembly_dir, "medaka", sample)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(medaka_file_path, dest_dir)
                else:
                    print(f"\nMedaka directory not found for sample: {sample} and invalid file path given: {medaka_file_path}")
                    all_files_moved = False
                
                # Move quast dir
                quast_dir = os.path.join(batch_info_path, nano_qc_dir, "quast", sample)
                if os.path.isdir(quast_dir):
                    dest_dir = os.path.join(assembly_dir, "quast")
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(quast_dir, dest_dir)
                else:
                    print(f"\nQuast directory not found for sample: {sample}")
                    all_files_moved = False
            
            else:
                print(f"Are you sure you named your nanoQC run correctly? Your run folder name is: {nano_qc_dir}")
                all_files_moved = False

    if all_files_moved:
        print("\nYay, samples from passed_samples.txt file have been moved to clean_fastq_qc_pass_samples directory and all specified samples have been moved to the assembly directory successfully!")
    else:
        print("\nSome nano_qc output files were not moved successfully. Please check the log messages above and correct any issues.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and organize nanopore and hybrid sequencing data.")
    parser.add_argument("--batch_info_path", required=True, help="Path to the date_BatchInfo directory (e.g., /nfs/turbo/umms-esnitkin/Project_Marimba/Sequence_data/ONT/2024-12-24_Batch1")
    parser.add_argument("--nanoQC_results_path", required=True, help="Path to the nanoQC results  (e.g., /nfs/turbo/umms-esnitkin/Project_Marimba/Sequence_data/ONT/2024-12-24_Batch1/2024-12-24_Project_MDHHS_Nano_QC)")

    args = parser.parse_args()

    batch_info_path = validate_path(args.batch_info_path)
    results_path = validate_path(args.nanoQC_results_path)

    #transfer_type = args.transfer_type

    #dirs, files = setup_directories(batch_info_path)
    
    #dirs, files = setup_directories(results_path, batch_info_path)
    #move_samples_to_dirs(results_path, batch_info_path, dirs, files)
    #move_passed_samples_nano_qc(batch_info_path, dirs["clean_fastq_qc_pass_samples_dir"], dirs["assembly_dir"])


    # Set up directories
    dirs = setup_directories(batch_info_path)

    # Set up files and check for QC summary file
    files, qc_summary_file = setup_files(batch_info_path, results_path)

    # Move samples to their respective directories
    move_samples_to_dirs(dirs, files, qc_summary_file) #results_path, batch_info_path, 

    # Move passed samples after processing
    move_passed_samples_nano_qc(batch_info_path, dirs["clean_fastq_qc_pass_samples_dir"], dirs["assembly_dir"])
