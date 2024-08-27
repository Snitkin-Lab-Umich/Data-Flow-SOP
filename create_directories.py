import os
import argparse
import sys
import difflib
import re

class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_flags = {
            '--dest_path': '--dest_path',
            '--project_name': '--project_name',
            '--data_type': '--data_type',
            '--folder_names_illumina': '--folder_names_illumina',
            '--folder_names_nanopore': '--folder_names_nanopore',
        }

    def parse_args(self, args=None, namespace=None):
        if args is None:
            args = sys.argv[1:]

        unknown_args = [arg for arg in args if arg.startswith('--') and arg.split('=')[0] not in self.correct_flags]
        if unknown_args:
            self.error(f"Unknown arguments: {', '.join(unknown_args)}")

        return super().parse_args(args, namespace)

    def error(self, message):
        args = sys.argv[1:]
        suggestions = []

        for arg in args:
            if arg.startswith('--') and arg not in self.correct_flags:
                suggestion = self.get_suggestion(arg)
                if suggestion:
                    suggestions.append(f"\nDid you mean '{suggestion}' instead of '{arg}'?")

        if suggestions:
            message += '\n' + '\n'.join(suggestions)
        sys.exit(message + "\n")

    def get_suggestion(self, arg):
        close_matches = difflib.get_close_matches(arg, self.correct_flags.keys(), n=1, cutoff=0.7)
        return close_matches[0] if close_matches else None

def main():
    parser = CustomArgumentParser(description="Create directory structure for illumina data.")
    parser.add_argument("--dest_path", required=True, help="Destination path where directories need to be created—do NOT include project name (e.g., /nfs/turbo/umms-esnitkin/)")
    parser.add_argument("--project_name", required=True, help="Name of your project (format: Project_Name-of-Project, e.g., Project_MDHHS)")
    parser.add_argument("--data_type", choices=["illumina", "nanopore", "both"], required=True, help="Type of data (illumina/nanopore/both)")
    parser.add_argument("--folder_names_illumina", nargs='?', const='', help="Comma separated folder names for Illumina (if multiple) (format: date_PlateInfo, e.g., 2024-12-24_Plate1-to-Plate3,2024-12-25_Plate4-to-Plate6)")
    parser.add_argument("--folder_names_nanopore", nargs='?', const='', help="Comma separated folder names for Nanopore (if multiple) (format: date_PlateInfo, e.g., 2024-09-14_Plate4-to-Plate6,2024-09-15_Plate7-to-Plate10)")

    args = parser.parse_args()

    dest_path = args.dest_path
    project_name = args.project_name
    data_type = args.data_type
    folder_names_illumina = args.folder_names_illumina
    folder_names_nanopore = args.folder_names_nanopore

    if not project_name.startswith("Project_"):
        parser.error("The project name must start with 'Project_'")

    project_path = os.path.join(dest_path, project_name)

    # Validate folder names before creating any directories
    print(f"\nValidating folders at {project_path} for data type {data_type}")
    if not validate_folders(parser, project_path, data_type, folder_names_illumina, folder_names_nanopore):
        parser.error("\nFolder validation failed. See above for details.")  # Use parser.error to handle argument-related errors

    # Create common directories
    create_common_directories(project_path)

    # Create assembly directory with subfolders based on data type
    create_assembly_structure(project_path, data_type)

    # Create directories if validation passes
    if data_type in ["illumina", "both"]:
        process_folders(project_path, "illumina", folder_names_illumina)

    elif data_type in ["both"]:
        process_folders(project_path, "illumina", folder_names_illumina)
        process_folders(project_path, "ONT", folder_names_nanopore)

    else: #data_type in ["nanopore", "both"]:
        process_folders(project_path, "ONT", folder_names_nanopore)

    print("\nSuccess! All specified directories have been created.")

def create_common_directories(project_path):
    metadata_path = os.path.join(project_path, "Sequence_data", "metadata")
    sample_lookup_path = os.path.join(project_path, "Sequence_data", "metadata", "sample_lookup")
    AGC_submission_path = os.path.join(project_path, "Sequence_data", "metadata", "AGC_submission")
    plasmidsaurus_path = os.path.join(project_path, "Sequence_data", "metadata", "plasmidsaurus")
    variant_calling_path = os.path.join(project_path, "Sequence_data", "variant_calling")
    try:
        os.makedirs(metadata_path, exist_ok=True)
        os.makedirs(sample_lookup_path, exist_ok=True)
        os.makedirs(AGC_submission_path, exist_ok=True)
        os.makedirs(plasmidsaurus_path, exist_ok=True)
        print(f"\nMetadata and subdirectories created successfully at {metadata_path}.")
        
        os.makedirs(variant_calling_path, exist_ok=True)
        print(f"\nVariant calling folder created successfully at {variant_calling_path}.")
    
    except Exception as e:
        print(f"Error creating common directories: {str(e)}")

def create_assembly_structure(project_path, data_type):
    assembly_path = os.path.join(project_path, "Sequence_data", "assembly")
    print(f"\nCreating assembly directory at {assembly_path}")
    try:
        os.makedirs(assembly_path, exist_ok=True)

        if data_type in ["illumina"]:
            illumina_path = os.path.join(assembly_path, "illumina")
            os.makedirs(illumina_path, exist_ok=True)
        
        elif data_type in ["both"]:
            illumina_path = os.path.join(assembly_path, "illumina")
            ont_path = os.path.join(assembly_path, "ONT")
            hybrid_path = os.path.join(assembly_path, "hybrid")
            os.makedirs(illumina_path, exist_ok=True)
            os.makedirs(ont_path, exist_ok=True)
            os.makedirs(hybrid_path, exist_ok=True)
        
        else: #data_type in ["nanopore", "both"]:
            ont_path = os.path.join(assembly_path, "ONT")          
            os.makedirs(ont_path, exist_ok=True)

        print(f"\nAssembly directory structure created successfully.")
    except Exception as e:
        print(f"Error creating assembly directory: {str(e)}")

def create_illumina_structure(project_path, folder_name):
    print(f"\nCreating Illumina directory structure for {folder_name} under {project_path}")
    base_path = os.path.join(project_path, "Sequence_data", "illumina_fastq", folder_name)
    os.makedirs(os.path.join(base_path, "failed_qc_samples"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "neg_ctrl"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "passed_qc_samples"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "raw_fastq"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "Sequence_data", "illumina_fastq", "clean_fastq_qc_pass_samples"), exist_ok=True)
    print(f"\nIllumina directory structure for {folder_name} created successfully.")

def create_ont_structure(project_path, folder_name):
    print(f"\nCreating ONT directory structure for {folder_name} under {project_path}")
    base_path = os.path.join(project_path, "Sequence_data", "ONT", folder_name)
    os.makedirs(os.path.join(base_path, "failed_qc_samples"), exist_ok=True)
    #os.makedirs(os.path.join(base_path, "neg_ctrl"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "passed_qc_samples"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "raw_fastq"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "Sequence_data", "ONT", "clean_fastq_qc_pass_samples"), exist_ok=True)
    print(f"\nONT directory structure for {folder_name} created successfully.")

def process_folders(project_path, data_type, folder_names):
    for folder_name in folder_names.split(','):
        if data_type == "illumina":
            create_illumina_structure(project_path, folder_name)
        else:
            create_ont_structure(project_path, folder_name)

def validate_folders(parser, project_path, data_type, folder_names_illumina, folder_names_nanopore):
    valid = True

    if data_type in ["illumina"]:
        if folder_names_illumina:
            for folder_name in folder_names_illumina.split(','):
                if not re.match(r'^\d{4}-\d{2}-\d{2}_Plate\d+(-to-Plate\d+)?$', folder_name.strip()):
                    parser.error(f"Invalid format for Illumina folder name: {folder_name}. Format should be 'year-month-day_PlateNumber-to-PlateNumber'.")
                    return False
                folder_path = os.path.join(project_path, "Sequence_data", "illumina_fastq", folder_name.strip())
                if os.path.exists(folder_path):
                    parser.error(f"\nThe folder name '{folder_name}' already exists under {project_path}/Sequence_data/illumina_fastq/. Please choose a different folder name.")
                    valid = False
            if folder_names_nanopore:
                parser.error(f"\nOops, looks like you gave two arguments: --folder_names_illumina and --folder_names_nanopore. Please use the right argument: --folder_names_illumina")
                return False
        
        elif not folder_names_illumina and folder_names_nanopore:
            parser.error(f"\nOops, looks like you gave --folder_names_nanopore instead of --folder_names_illumina. Please use the right argument: --folder_names_illumina")
            return False
        
        else:
            parser.error(f"\nComma separated folder names for Illumina are required.")
            return False                
               
        #if not folder_names_illumina:
            #print("\nComma separated folder names for Illumina are required.")
            #return False
        
        #if folder_names_illumina and folder_names_nanopore:
            #print("\nOops, looks like you gave two arguments: --folder_names_illumina and --folder_names_nanopore. Please use the right argument: --folder_names_illumina")
            #return False

    if data_type in ["nanopore"]:
        if folder_names_nanopore:
            for folder_name in folder_names_nanopore.split(','):
                if not re.match(r'^\d{4}-\d{2}-\d{2}_Batch\d+(-to-Batch\d+)?(_rerun)?$', folder_name.strip()):
                    parser.error(f"\nInvalid format for ONT folder name: {folder_name}. Format should be 'year-month-day_BatchNum-to-BatchNum', 'year-month-day_BatchNum-to-BatchNum_rerun', 'year-month-day_BatchNum', or 'year-month-day_BatchNum_rerun'.")
                    return False
                folder_path = os.path.join(project_path, "Sequence_data", "ONT", folder_name.strip())
                if os.path.exists(folder_path):
                    parser.error(f"\nThe folder name '{folder_name}' already exists under {project_path}/Sequence_data/ONT/. Please choose a different folder name.")
                    valid = False
            if folder_names_illumina:
                parser.error(f"\nOops, looks like you gave two arguments: --folder_names_nanopore and --folder_names_illumina. Please use the right argument: --folder_names_nanopore")
                return False
        
        elif not folder_names_nanopore and folder_names_illumina:
            parser.error(f"\nOops, looks like you gave --folder_names_illumina instead of --folder_names_nanopore. Please use the right argument: --folder_names_nanopore")
            return False
         
        else:
            parser.error(f"\nComma separated folder names for Nanopore are required.")
            return False 

        #if not folder_names_nanopore and folder_names_illumina:
            #print("\nOops, looks like you gave --folder_names_illumina instead of --folder_names_nanopore. Please use the right argument: --folder_names_nanopore")
            #return False

        #if not folder_names_nanopore:
            #print("\nComma separated folder names for Nanopore are required.")
            #return False
        
        #if folder_names_nanopore and folder_names_illumina:
            #print("\nOops, looks like you gave two arguments: --folder_names_nanopore and --folder_names_illumina. Please use the right argument: --folder_names_nanopore")
            #return False
    

    if data_type in ["both"]:
        if folder_names_illumina and not folder_names_nanopore:
            for folder_name in folder_names_illumina.split(','):
                folder_path = os.path.join(project_path, "Sequence_data", "illumina_fastq", folder_name.strip())
                if os.path.exists(folder_path):
                    print(f"The folder name '{folder_name}' already exists under {project_path}/Sequence_data/illumina_fastq/. Please choose a different folder name.\n")
                    valid = False
        
            for folder_name in folder_names_nanopore.split(','):
                folder_path = os.path.join(project_path, "Sequence_data", "ONT", folder_name.strip())
                if os.path.exists(folder_path):
                    print(f"The folder name '{folder_name}' already exists under {project_path}/Sequence_data/ONT/. Please choose a different folder name.\n")
                    valid = False
        else:
            print("\nComma separated folder names for Illumina and ONT are required. The following arguments are required: --folder_names_illumina and --folder_names_nanopore")
            return False 

        #if not folder_names_illumina:
            #print("\nComma separated folder names for Illumina are required.")
            #return False

        #if not folder_names_nanopore:
            #print("\nComma separated folder names for Nanopore are required.")
            #return False

        #if not folder_names_illumina and not folder_names_nanopore:
        #    print("\nComma separated folder names for Illumina and ONT are required. The following arguments are required: --folder_names_illumina and --folder_names_nanopore")
        #    return False
        

    return valid

if __name__ == "__main__":
    main()
