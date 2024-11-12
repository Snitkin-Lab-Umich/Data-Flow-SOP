import os
import argparse
import sys
import difflib

class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_flags = {
            '--dest_path': '--dest_path',
            '--project_name': '--project_name',
            '--data_type': '--data_type'
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
    parser = CustomArgumentParser(description="Create project folder and higher level directory structure for illumina and nanopore data.")
    parser.add_argument("--dest_path", required=True, help="Destination path where directories need to be created—do NOT include project name (e.g., /nfs/turbo/umms-esnitkin/)")
    parser.add_argument("--project_name", required=True, help="Name of your project (format: Project_Name-of-Project, e.g., Project_MDHHS)")
    parser.add_argument("--data_type", choices=["illumina", "nanopore", "both"], required=True, help="Type of data (illumina/nanopore/both)")
    
    args = parser.parse_args()

    dest_path = args.dest_path
    project_name = args.project_name
    data_type = args.data_type
   
    if not project_name.startswith("Project_"):
        parser.error("The project name must start with 'Project_'")

    project_path = os.path.join(dest_path, project_name)

    # Create common directories
    create_common_directories(project_path)

    # Create assembly directory with subfolders based on data type
    create_assembly_structure(project_path, data_type)

    # Create directories specific to data type
    if data_type in ["illumina"]:
        create_illumina_structure(project_path)

    elif data_type in ["both"]:
        create_illumina_structure(project_path)
        create_ont_structure(project_path)

    else:
        create_ont_structure(project_path)

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
    #print(f"\nCreating assembly directory at {assembly_path}")
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

        print(f"\nAssembly directory structure created successfully at {assembly_path}.")

    except Exception as e:
        print(f"Error creating assembly directory: {str(e)}")

def create_illumina_structure(project_path):
    illumina_path = os.path.join(project_path, "Sequence_data", "illumina_fastq")
    try:
        os.makedirs(illumina_path, exist_ok=True)
       # print(f"\nIllumina directory structure created successfully.")
        print(f"\nCreated Illumina directory structure under {project_path}")
    except Exception as e:
        print(f"Error creating Illumina directories: {str(e)}")

def create_ont_structure(project_path):
    ont_path = os.path.join(project_path, "Sequence_data", "ONT")
    try:
        os.makedirs(ont_path, exist_ok=True)
        #print(f"\nONT directory structure created successfully.")
        print(f"\nCreated ONT directory structure under {project_path}")
    except Exception as e:
        print(f"Error creating ONT directories: {str(e)}")

if __name__ == "__main__":
    main()
