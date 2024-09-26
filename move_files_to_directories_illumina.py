import os
import shutil
import argparse
import csv

def validate_path(path):
    while not os.path.isdir(path):
        path = input(f"The path '{path}' does not exist. Please enter a valid path: ")
    return path

def move_qcd_folder(qcd_results_path, plate_info_path):
    qcd_folder_name = os.path.basename(os.path.normpath(qcd_results_path))
    shutil.move(qcd_results_path, plate_info_path)
    
    qc_summary_file = os.path.join(plate_info_path, f"{qcd_folder_name}/{qcd_folder_name}_Report/data/{qcd_folder_name}_QC_summary.csv")
    
    if not os.path.isfile(qc_summary_file):
        print(f"QC summary file not found at '{qc_summary_file}'! Are you sure you ran QCD entirely?")
        exit(1)
    return qc_summary_file

def setup_directories(plate_info_path):
    illumina_fastq_dir = os.path.dirname(plate_info_path)
    sequence_data_dir = os.path.dirname(illumina_fastq_dir)

    dirs = {
        "raw_fastq_dir": os.path.join(plate_info_path, "raw_fastq"),
        "failed_qc_samples_dir": os.path.join(plate_info_path, "failed_qc_samples"),
        "passed_qc_samples_dir": os.path.join(plate_info_path, "passed_qc_samples"),
        "neg_ctrl_dir": os.path.join(plate_info_path, "neg_ctrl"),
        "clean_fastq_qc_pass_samples_dir": os.path.join(illumina_fastq_dir, "clean_fastq_qc_pass_samples"),
        "assembly_dir": os.path.join(sequence_data_dir, "assembly", "illumina")
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    
    files = {
        "failed_samples_file": os.path.join(plate_info_path, "failed_samples.txt"),
        "passed_samples_file": os.path.join(plate_info_path, "passed_samples.txt"),
        "missing_samples_file": os.path.join(plate_info_path, "missing_samples.txt"),
        "master_qc_summary_file": os.path.join(illumina_fastq_dir, "master_qc_summary.csv")
    }
    for f in files.values():
        if not os.path.exists(f):
            open(f, 'a').close()
            if f == files["master_qc_summary_file"]:
                print(f"\nCreated master QC summary file at: {f}")
    
    with open(files["missing_samples_file"], 'w') as f:
        f.write("missing_sample,which_folder\n")

    return dirs, files

def move_neg_ctrl_samples(raw_fastq_dir, neg_ctrl_dir):
    for file in os.listdir(raw_fastq_dir):
        if "_NEG_CTL" in file:
            shutil.move(os.path.join(raw_fastq_dir, file), neg_ctrl_dir)

def process_qc_summary(qc_summary_file, dirs, files):
    with open(qc_summary_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        samples_processed = 0

        for row in reader:
            sample = row["Sample"]
            qc_check = row["QC Check"]

            forward = f"{sample}_R1.fastq.gz"
            reverse = f"{sample}_R2.fastq.gz"
            forward_path = os.path.join(dirs["raw_fastq_dir"], forward)
            reverse_path = os.path.join(dirs["raw_fastq_dir"], reverse)
            dest_dir = dirs["passed_qc_samples_dir"] if qc_check == "0" else dirs["failed_qc_samples_dir"]

            if "_NEG_CTL" in sample:
                dest_dir = dirs["neg_ctrl_dir"]

            if os.path.isfile(forward_path) and os.path.isfile(reverse_path):
                shutil.move(forward_path, dest_dir)
                shutil.move(reverse_path, dest_dir)

                if qc_check == "FAIL" and dest_dir != dirs["neg_ctrl_dir"]:
                    with open(files["failed_samples_file"], 'a') as f:
                        f.write(f"{sample}\n")
                elif qc_check == "0":
                    with open(files["passed_samples_file"], 'a') as f:
                        f.write(f"{sample}\n")

                samples_processed += 1
            else:
                if "_NEG_CTL" not in sample:
                    with open(files["missing_samples_file"], 'a') as f:
                        if not os.path.isfile(forward_path):
                            f.write(f"{forward},{dest_dir}\n")
                        if not os.path.isfile(reverse_path):
                            f.write(f"{reverse},{dest_dir}\n")
    
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

    with open(files["missing_samples_file"], 'r') as f:
        lines = f.readlines()
        
    if len(lines) > 1:
        print(f"Some files are missing and are listed in {files['missing_samples_file']}.")
    else:
        print("\nYay, all files were transferred to their respective folders successfully!")
        os.remove(files["missing_samples_file"])

def move_passed_samples(plate_info_path, clean_fastq_qc_pass_samples_dir):
    #illumina_fastq_dir = os.path.dirname(plate_info_path)
    #clean_fastq_qc_pass_samples_dir = os.path.join(illumina_fastq_dir, "clean_fastq_qc_pass_samples")

    #os.makedirs(clean_fastq_qc_pass_samples_dir, exist_ok=True)

    passed_samples_file = os.path.join(plate_info_path, "passed_samples.txt")
    if not os.path.isfile(passed_samples_file):
        print("No passed_samples.txt file found! Are you sure you moved the raw fastq reads into their respective directories (passed and failed qc folders)?")
        exit(1)

    all_files_moved = True
    with open(passed_samples_file, 'r') as f:
        for sample in f:
            sample = sample.strip()
            qcd_dir = next((d for d in os.listdir(plate_info_path) if d.endswith('_QCD') and os.path.isdir(os.path.join(plate_info_path, d, sample, "trimmomatic"))), None)
            if qcd_dir:
                qcd_dir = os.path.join(plate_info_path, qcd_dir, sample, "trimmomatic")
                forward = f"{sample}_R1_trim_paired.fastq.gz"
                reverse = f"{sample}_R2_trim_paired.fastq.gz"
                forward_path = os.path.join(qcd_dir, forward)
                reverse_path = os.path.join(qcd_dir, reverse)

                if os.path.isfile(forward_path):
                    shutil.move(forward_path, clean_fastq_qc_pass_samples_dir)
                else:
                    print(f"Warning: {forward} not found in {qcd_dir}")
                    all_files_moved = False

                if os.path.isfile(reverse_path):
                    shutil.move(reverse_path, clean_fastq_qc_pass_samples_dir)
                else:
                    print(f"Warning: {reverse} not found in {qcd_dir}")
                    all_files_moved = False
            else:
                print(f"No trimmomatic directory found for sample {sample}!")
                all_files_moved = False

    if all_files_moved:
        print("\nYay, samples from passed_samples.txt file have been moved to clean_fastq_qc_pass_samples directory!")
    else:
        print("Some files were not moved successfully. Please check the log messages above and correct any issues.")

def move_qcd_outputs_to_assembly(plate_info_path, assembly_dir):
    passed_samples_file = os.path.join(plate_info_path, "passed_samples.txt")
    if not os.path.isfile(passed_samples_file):
        print(f"passed_samples.txt not found in directory: {plate_info_path}")
        exit(1)

    all_successful = True
    with open(passed_samples_file, 'r') as f:
        for sample in f:
            sample = sample.strip()
            qcd_dir = next((d for d in os.listdir(plate_info_path) if d.endswith('_QCD')), None)
            if qcd_dir:
                qcd_dir = os.path.join(plate_info_path, qcd_dir, sample)

                prokka_dir = os.path.join(qcd_dir, "prokka")
                if os.path.isdir(prokka_dir):
                    dest_dir = os.path.join(assembly_dir, sample)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(prokka_dir, dest_dir)
                else:
                    print(f"Prokka directory not found for sample: {sample}")
                    all_successful = False

                spades_contigs = os.path.join(qcd_dir, "spades", "contigs.fasta")
                if os.path.isfile(spades_contigs):
                    spades_dir = os.path.join(assembly_dir, sample, "spades")
                    os.makedirs(spades_dir, exist_ok=True)
                    shutil.move(spades_contigs, os.path.join(spades_dir, "contigs.fasta"))
                else:
                    print(f"contigs.fasta not found for sample: {sample}")
                    all_successful = False

                quast_dir = os.path.join(qcd_dir, "quast")
                if os.path.isdir(quast_dir):
                    shutil.move(quast_dir, os.path.join(assembly_dir, sample))
                else:
                    print(f"Quast directory not found for sample: {sample}")
                    all_successful = False
            else:
                print(f"QCD directory not found in {plate_info_path}")
                all_successful = False

    if all_successful:
        print("\nYay, all specified samples have been moved to the assembly directory successfully!")
    else:
        print("Some samples or required files were not found. Please check the logs above for details.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and organize illumina sequencing data.")
    parser.add_argument("--plate_info_path", required=True, help="Path to the date_PlateInfo directory (e.g., /nfs/turbo/umms-esnitkin/Project_Marimba/Sequence_data/illumina_fastq/2024-12-24_Plate1-to-Plate3)")
    parser.add_argument("--qcd_results_path", required=True, help="Path to the QCD results directory (e.g., /scratch/esnitkin_root/esnitkin1/dhatrib/QCD/results/Project_MDHHS_QCD)")

    args = parser.parse_args()

    plate_info_path = validate_path(args.plate_info_path)
    qcd_results_path = validate_path(args.qcd_results_path)

    qc_summary_file = move_qcd_folder(qcd_results_path, plate_info_path)
    dirs, files = setup_directories(plate_info_path)
    move_neg_ctrl_samples(dirs["raw_fastq_dir"], dirs["neg_ctrl_dir"])
    process_qc_summary(qc_summary_file, dirs, files)
    move_passed_samples(plate_info_path, dirs["clean_fastq_qc_pass_samples_dir"])
    move_qcd_outputs_to_assembly(plate_info_path, dirs["assembly_dir"])
