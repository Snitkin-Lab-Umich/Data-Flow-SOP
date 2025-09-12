import os
import shutil
import argparse
import csv

def validate_path(path):
    while not os.path.isdir(path):
        path = input(f"The path '{path}' does not exist. Please enter a valid path: ")
    return path

def setup_directories(data_download_folder, input_type):
    if input_type == "raw_fastq":
        data_download_folder = os.path.normpath(data_download_folder)
        illumina_dir = os.path.dirname(data_download_folder)
        parent_public_genome_dir = os.path.dirname(illumina_dir)

        dirs = {
            "raw_fastq_dir": os.path.join(data_download_folder, "raw_fastq"),
            "failed_qc_samples_dir": os.path.join(data_download_folder, "failed_qc_samples"),
            "passed_qc_samples_dir": os.path.join(data_download_folder, "passed_qc_samples"),
            "clean_fastq_qc_pass_samples_dir": os.path.join(illumina_dir, "clean_fastq_qc_pass_samples"),
            "assembly_dir": os.path.join(parent_public_genome_dir, "assembly", "illumina")
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)
        
        files = {
            "failed_samples_file": os.path.join(data_download_folder, "failed_samples.txt"),
            "passed_samples_file": os.path.join(data_download_folder, "passed_samples.txt"),
            "missing_samples_file": os.path.join(data_download_folder, "missing_samples.txt"),
            "master_qc_summary_file": os.path.join(illumina_dir, "master_qc_summary_raw_reads.csv")
        }
        for f in files.values():
            if not os.path.exists(f):
                open(f, 'a').close()
                if f == files["master_qc_summary_file"]:
                    print(f"\nCreated master QC summary file at: {f}")
        
        with open(files["missing_samples_file"], 'w') as f:
            f.write("missing_sample,which_folder\n")
    else:
        data_download_folder = os.path.normpath(data_download_folder)
        illumina_dir = os.path.dirname(data_download_folder)
        parent_public_genome_dir = os.path.dirname(illumina_dir)

        dirs = {
            "assembly_downloads_dir": os.path.join(data_download_folder, "assembly_downloads"),
            "failed_qc_assemblies_dir": os.path.join(data_download_folder, "failed_qc_assemblies"),
            "assembly_dir": os.path.join(parent_public_genome_dir, "assembly", "illumina")
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)
        
        files = {
            "failed_samples_file": os.path.join(data_download_folder, "failed_samples.txt"),
            "passed_samples_file": os.path.join(data_download_folder, "passed_samples.txt"),
            "missing_samples_file": os.path.join(data_download_folder, "missing_samples.txt"),
            "master_qc_summary_file": os.path.join(illumina_dir, "master_qc_summary_assembly.csv")
        }
        for f in files.values():
            if not os.path.exists(f):
                open(f, 'a').close()
                if f == files["master_qc_summary_file"]:
                    print(f"\nCreated master QC summary file at: {f}")
        
        with open(files["missing_samples_file"], 'w') as f:
            f.write("missing_sample,which_folder\n")

    return dirs, files

def process_qc_summary(qcd_results_path, dirs, files, input_type):
    if input_type == "raw_fastq":
        qcd_folder_name = os.path.basename(os.path.normpath(qcd_results_path))

        qcd_results_path = os.path.normpath(qcd_results_path)
    
        qc_summary_file = os.path.join(qcd_results_path, f"{qcd_folder_name}_Report/data/{qcd_folder_name}_QC_summary.csv")
        
        if not os.path.isfile(qc_summary_file):
            print(f"QC summary file not found at '{qc_summary_file}'! Are you sure you ran pubQCD entirely?")
            exit(1)

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
                dest_dir = dirs["passed_qc_samples_dir"] if qc_check == "PASS" else dirs["failed_qc_samples_dir"]

                # if "_NEG_CTL" in sample:
                #     dest_dir = dirs["neg_ctrl_dir"]

                if os.path.isfile(forward_path) and os.path.isfile(reverse_path):
                    # shutil.move(forward_path, dest_dir)
                    # shutil.move(reverse_path, dest_dir)

                    if qc_check == "FAIL":
                        with open(files["failed_samples_file"], 'a') as f:
                            f.write(f"{sample}\n")
                    elif qc_check == "PASS":
                        with open(files["passed_samples_file"], 'a') as f:
                            f.write(f"{sample}\n")

                    samples_processed += 1
                else:
                    # if "_NEG_CTL" not in sample:
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
    else:
        qcd_folder_name = os.path.basename(os.path.normpath(qcd_results_path))

        qcd_results_path = os.path.normpath(qcd_results_path)
    
        qc_summary_file = os.path.join(qcd_results_path, f"{qcd_folder_name}_Report/data/{qcd_folder_name}_QC_summary.csv")
        
        if not os.path.isfile(qc_summary_file):
            print(f"QC summary file not found at '{qc_summary_file}'! Are you sure you ran pubQCD entirely?")
            exit(1)

        with open(qc_summary_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            samples_processed = 0

            for row in reader:
                sample = row["Sample"]
                qc_check = row["QC Check"]

                # Check if files have fasta or fna extension
                #if dirs["assembly_downloads"]:
                first_file = next(f for f in os.listdir(dirs["assembly_downloads_dir"]) if os.path.isfile(os.path.join(dirs["assembly_downloads_dir"], f)))
                file_name_and_extension = os.path.basename(first_file)
                file_extension = os.path.splitext(file_name_and_extension)[1]
                assembly = f"{sample}{file_extension}" 
                # reverse = f"{sample}_R2.fastq.gz"
                assembly_path = os.path.join(dirs["assembly_downloads_dir"], assembly)
                
                if os.path.isfile(assembly_path): 

                    if qc_check == "FAIL":
                        shutil.move(assembly_path, dirs["failed_qc_assemblies_dir"])

                        with open(files["failed_samples_file"], 'a') as f:
                            f.write(f"{sample}\n")
                    elif qc_check == "PASS":
                        with open(files["passed_samples_file"], 'a') as f:
                            f.write(f"{sample}\n")

                    samples_processed += 1
                else:
                    # if "_NEG_CTL" not in sample:
                    with open(files["missing_samples_file"], 'a') as f:
                        if not os.path.isfile(assembly_path):
                            f.write(f"{assembly},{qc_check}\n")
                        # if not os.path.isfile(reverse_path):
                        #     f.write(f"{reverse},{dest_dir}\n")
        
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

def move_passed_samples(data_download_folder, qcd_results_path, clean_fastq_qc_pass_samples_dir):

    qcd_results_path = os.path.normpath(qcd_results_path)
    data_download_folder = os.path.normpath(data_download_folder)

    passed_samples_file = os.path.join(data_download_folder, "passed_samples.txt")
    if not os.path.isfile(passed_samples_file):
        print("No passed_samples.txt file found! Are you sure you moved the raw fastq reads into their respective directories (passed and failed qc folders)?")
        exit(1)

    all_files_moved = True
    with open(passed_samples_file, 'r') as f:
        for sample in f:
            sample = sample.strip()
            #qcd_dir = next((d for d in os.listdir(data_download_folder) if d.endswith('_QCD') and os.path.isdir(os.path.join(data_download_folder, d, sample, "trimmomatic"))), None)
            
            if qcd_results_path:
                trimmomatic_dir = os.path.join(qcd_results_path, "trimmomatic", sample)
                forward = f"{sample}_R1_trim_paired.fastq.gz"
                reverse = f"{sample}_R2_trim_paired.fastq.gz"
                forward_path = os.path.join(trimmomatic_dir, forward)
                reverse_path = os.path.join(trimmomatic_dir, reverse)

                if os.path.isfile(forward_path):
                    shutil.move(forward_path, clean_fastq_qc_pass_samples_dir)
                else:
                    print(f"Warning: {forward} not found in {trimmomatic_dir}")
                    all_files_moved = False

                if os.path.isfile(reverse_path):
                    shutil.move(reverse_path, clean_fastq_qc_pass_samples_dir)
                else:
                    print(f"Warning: {reverse} not found in {trimmomatic_dir}")
                    all_files_moved = False
            else:
                print(f"No trimmomatic directory found for sample: {sample}!")
                all_files_moved = False

    if all_files_moved:
        print("\nYay, samples from passed_samples.txt file have been moved to clean_fastq_qc_pass_samples directory!")
    else:
        print("Some files were not moved successfully. Please check the log messages above and correct any issues.")

def move_qcd_outputs_to_assembly(data_download_folder, qcd_results_path, assembly_dir, input_type):
    if input_type == "raw_fastq":
        qcd_results_path = os.path.normpath(qcd_results_path)
        data_download_folder = os.path.normpath(data_download_folder)

        passed_samples_file = os.path.join(data_download_folder, "passed_samples.txt")
        if not os.path.isfile(passed_samples_file):
            print(f"passed_samples.txt not found in directory: {data_download_folder}")
            exit(1)

        all_successful = True
        with open(passed_samples_file, 'r') as f:
            for sample in f:
                sample = sample.strip()
                #qcd_dir = next((d for d in os.listdir(data_download_folder) if d.endswith('_QCD')), None)
                if qcd_results_path:
                    #qcd_dir = os.path.join(data_download_folder, qcd_dir, sample)

                    prokka_dir = os.path.join(qcd_results_path, "prokka", sample)
                    if os.path.isdir(prokka_dir):
                        dest_dir = os.path.join(assembly_dir, "prokka")
                        os.makedirs(dest_dir, exist_ok=True)
                        shutil.move(prokka_dir, dest_dir)
                    else:
                        print(f"Prokka directory not found for sample: {sample}")
                        all_successful = False

                    spades_contigs = os.path.join(qcd_results_path, "spades", sample, f"{sample}_contigs_l1000.fasta")
                    if os.path.isfile(spades_contigs):
                        spades_dir = os.path.join(assembly_dir, "passed_qc_assemblies", sample)
                        os.makedirs(spades_dir, exist_ok=True)
                        shutil.move(spades_contigs, spades_dir)
                    else:
                        print(f"assembly fasta file not found for sample: {sample} in {spades_dir}")
                        all_successful = False

                    quast_dir = os.path.join(qcd_results_path, "quast", sample)
                    if os.path.isdir(quast_dir):
                        shutil.move(quast_dir, os.path.join(assembly_dir, "quast", sample))
                    else:
                        print(f"Quast directory not found for sample: {sample}")
                        all_successful = False
                else:
                    print(f"pubQCD directory not found in {data_download_folder}")
                    all_successful = False

        if all_successful:
            print("\nYay, all specified samples have been moved to the assembly directory successfully!")
        else:
            print("Some samples or required files were not found. Please check the logs above for details.")
    else:
        qcd_results_path = os.path.normpath(qcd_results_path)
        data_download_folder = os.path.normpath(data_download_folder)

        passed_samples_file = os.path.join(data_download_folder, "passed_samples.txt")
        if not os.path.isfile(passed_samples_file):
            print(f"passed_samples.txt not found in directory: {data_download_folder}")
            exit(1)

        all_successful = True
        with open(passed_samples_file, 'r') as f:
            for sample in f:
                sample = sample.strip()
                #qcd_dir = next((d for d in os.listdir(data_download_folder) if d.endswith('_QCD')), None)
                if qcd_results_path:
                    #qcd_dir = os.path.join(data_download_folder, qcd_dir, sample)

                    prokka_dir = os.path.join(qcd_results_path, "prokka", sample)
                    if os.path.isdir(prokka_dir):
                        dest_dir = os.path.join(assembly_dir, "prokka")
                        os.makedirs(dest_dir, exist_ok=True)
                        shutil.move(prokka_dir, dest_dir)
                    else:
                        print(f"Prokka directory not found for sample: {sample}")
                        all_successful = False

                    spades_contigs = os.path.join(qcd_results_path, "bioawk", sample, f"{sample}_contigs_l1000.fasta")
                    if os.path.isfile(spades_contigs):
                        bioawk_dir = os.path.join(assembly_dir, "passed_qc_assemblies", sample)
                        os.makedirs(bioawk_dir, exist_ok=True)
                        shutil.move(spades_contigs, bioawk_dir)
                    else:
                        print(f"assembly fasta file not found for sample: {sample} in {bioawk_dir}")
                        all_successful = False

                    quast_dir = os.path.join(qcd_results_path, "quast", sample)
                    if os.path.isdir(quast_dir):
                        shutil.move(quast_dir, os.path.join(assembly_dir, "quast", sample))
                    else:
                        print(f"Quast directory not found for sample: {sample}")
                        all_successful = False
                else:
                    print(f"pubQCD directory not found in {data_download_folder}")
                    all_successful = False

        if all_successful:
            print("\nYay, all specified samples have been moved to the assembly directory successfully!")
        else:
            print("Some samples or required files were not found. Please check the logs above for details.")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and organize illumina sequencing data.")
    parser.add_argument("--data_download_folder", required=True, help="Path to the downloaded data directory in Public_datasets directory (e.g., /nfs/turbo/umms-esnitkin/Project_MRSA_CM/Public_datasets/2025-04-16_all-USA300-MRSA_NCBI/illumina/2025-04-16_USA300-MRSA-raw-reads-ONLY_NCBI)")
    parser.add_argument("--qcd_results_path", required=True, help="Path to the pubQCD results directory in project folder (e.g., /nfs/turbo/umms-esnitkin/Project_MRSA_CM/Public_datasets/2025-04-16_all-USA300-MRSA_NCBI/illumina/2025-04-16_USA300-MRSA-raw-reads-ONLY_NCBI/2025-03-25_Project_USA_300_pubQCD)")
    parser.add_argument("--input_type", required=True, choices=["raw_fastq", "assembly"], help="Type of data you processed in the pipeline—raw fastq or assembly")

    args = parser.parse_args()

    data_download_folder = validate_path(args.data_download_folder)
    qcd_results_path = validate_path(args.qcd_results_path)
    input_type = args.input_type

    #qc_summary_file = move_qcd_folder(qcd_results_path, data_download_folder)
    dirs, files = setup_directories(data_download_folder, input_type) # Done
    # move_neg_ctrl_samples(dirs["raw_fastq_dir"], dirs["neg_ctrl_dir"])
    process_qc_summary(qcd_results_path, dirs, files, input_type) # Done
    if input_type == "raw_fastq":
        move_passed_samples(data_download_folder, qcd_results_path, dirs["clean_fastq_qc_pass_samples_dir"])
    move_qcd_outputs_to_assembly(data_download_folder, qcd_results_path, dirs["assembly_dir"], input_type)
