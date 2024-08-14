# Processing illumina samples
The following are crucial steps part of the Snitkin lab SOP to process your short reads. 
<!--
- [Processing illumina samples](#Processing-illumina-samples)
  - [Getting started](#Getting-started)
  - [Governance Working Group Call Procedures](#governance-working-group-call-procedures)
    - [Preparing for a Call](#preparing-for-a-call)
-->
<!-- comment -->

## Getting started
You need to install the Data Flow SOP from Github and follow the directions in this document to create your project folder on turbo. If your project folder is already created,great—that's one less step for you to do! You will need to run  `create_directories.py` to create the relevant directories in your project folder. If you run into any issues or you are unable to find the relevant files or the instructions are unclear, **_please_** slack Dhatri  and do not move forward with the SOP.<!--This script should be run in the directory you are currently in but the path you give is the path to your (already/newly created) project folder on turbo. -->

### Installation

> Clone github directory onto your system.

```
git clone https://github.com/Snitkin-Lab-Umich/Data-Flow-SOP.git
```

>Ensure you have successfully cloned Data-Flow-SOP. Type ls and you should see the newly created directory Data-Flow-SOP. Move to the newly created directory.

```
cd Data-Flow-SOP
```

### Create relevant directories in your project folder 
1. To get started, type this command `python3 create_directories.py -h`. This will give you an idea of all the flags present in the script and what you need to specify for each argument e.g.`--dest_path, --project_name, --data_type, --folder_names_illumina, --folder_names_nanopore`. 

<!--
```
usage: create_directories.py [-h] --dest_path DEST_PATH --project_name PROJECT_NAME --data_type {illumina,nanopore,both} [--folder_names_illumina [FOLDER_NAMES_ILLUMINA]]
                             [--folder_names_nanopore [FOLDER_NAMES_NANOPORE]]

Create directory structure for sequencing data.

options:
  -h, --help            show this help message and exit
  --dest_path DEST_PATH
                        Destination path where directories need to be created—do NOT include project name (e.g., /nfs/turbo/umms-esnitkin/)
  --project_name PROJECT_NAME
                        Name of your project (format: Project_Name-of-Project, e.g., Project_MDHHS)
  --data_type {illumina,nanopore,both}
                        Type of data (illumina/nanopore/both)
  --folder_names_illumina [FOLDER_NAMES_ILLUMINA]
                        Comma separated folder names for Illumina (if multiple) (format: date_PlateInfo, e.g., 2024-12-24_Plate1-to-Plate3,2024-12-25_Plate4-to-Plate6)
  --folder_names_nanopore [FOLDER_NAMES_NANOPORE]
                        Comma separated folder names for Nanopore (if multiple) (format: date_PlateInfo, e.g., 2024-09-14_Plate4-to-Plate6,2024-09-15_Plate7-to-Plate10)
```
-->

2. Create the directories

3. Visualize directory structure: `tree /nfs/turbo/umms-esnitkin/Project_Test_Illumina_Org` to look at the directories created

<!--
```
/nfs/turbo/umms-esnitkin/Project_Test_Illumina_Org
└── Sequence_data
    ├── assembly
    │   └── illumina
    └── illumina_fastq
        ├── 2024-08-01_Plate1-to-Plate4
        │   ├── failed_qc_samples
        │   ├── neg_ctrl
        │   ├── passed_qc_samples
        │   └── raw_fastq
        └── clean_fastq_qc_pass_samples
```
-->

### Rename samples

4. Navigate to this directory `/nfs/turbo/umms-esnitkin/Raw_sequencing_data/` and find the folder corresponding to your dataset. Rename samples using demultiplex file `DemuxStats_*.csv`. 

> Move to `Raw_sequencing_data` folder and navigate to your corresponding dataset folder.

```
cd /nfs/turbo/umms-esnitkin/Raw_sequencing_data
ls
cd your/samples/folder
```

> Rename samples using the `rename_samples.sh`. To understand how to use the bash script, execute the following command

```
./scratch/esnitkin_root/esnitkin1/path/to/Data-Flow-SOP/rename_samples.sh 
```

> You will need to give the folder with the fastqs and a file lookup `DemuxStats_*.csv`. If you are unable to find the fastq folder and/or the lookup file, **please do not move forward with the following steps and slack Evan**. 

```
./scratch/esnitkin_root/esnitkin1/path/to/Data-Flow-SOP/rename_samples.sh fastq_folder DemuxStats_*.csv
```

5. The samples should have been renamed. There will be a new script generated called `renamed_file_commands.sh`. This script contains a bunch of move commands that show the names of the old files and their corresponding renamed file names. 

> Check if the file has been created 

```
ls /nfs/turbo/umms-esnitkin/Raw_sequencing_data/your/samples/folder
```

Inspect contents of the file. Hit `q` to exit. 

```
less /nfs/turbo/umms-esnitkin/Raw_sequencing_data/your/samples/folder/renamed_file_commands.sh
```

> Ensure all the files have been renamed. Navigate to the fastq folder.

```
cd fastq_folder
ls
```
_**STOP AND CHECK**_: If there are some files that have not been renamed, please slack Dhatri immediately and do not move forward with the following steps.

### Run QCD
6. You are now ready to start processing your short reads. We will be using one of our in house pipelines, [QCD](https://github.com/Snitkin-Lab-Umich/QCD), to run on the renamed samples. Click on the link and follow the instructions as described on the Github page. 

_**STOP AND CHECK**_: If you run into any issues running QCD, please slack Dhatri immediately and do not move forward with the following steps. Ensure you have generated the QC report before moving on.

### Move QCD outputs to Project directory
7. Before you move QCD outputs, to relevant directories on Project folder i.e. the path to your Project folder on turbo. 

> Log onto [globus](https://app.globus.org/file-manager?two_pane=true). Move only the fastq files to the `raw_fastq` folder in your newly created Project folder on turbo `/nfs/turbo/umms-esnitkin/Project_Test_Illumina_Org/Sequence_data/illumina_fastq/2024-08-01_Plate1-to-Plate4/raw_fastq`

> Use [globus](https://app.globus.org/file-manager?two_pane=true) again to transfer the rest of the files found in your dataset folder. E.g. of files that can be found the Demultiplex lookup file (`DemuxStats_*.csv`), `README` (if applicable), `renamed_file_commands.sh`.  

<!-- > E -->

8. Start and interative session and navigate to the `Data-Flow-SOP` folder. Ensure globus has succesfully transferred the fastq files. 

> Start an interactive session. 
```
srun --account=esnitkin1 --nodes=1 --ntasks-per-node=1 --mem-per-cpu=5GB --cpus-per-task=3 --time=8:00:00 --pty /bin/bash
```

> Ensure you are in the right directory.
```
cd /scratch/esnitkin_root/esnitkin1/uniqname/path/to/Data-Flow-SOP/
```

9. Move QCD outputs using  `move_files_to_directories_illumina.py`. To understand how to use the python script, try `python3 move_files_to_directories_illumina.py -h`.

<!-- >
(base) [dhatrib@gl-gl3021 Data-Flow-SOP]$ python3 move_files_to_directories_illumina.py -h
usage: move_files_to_directories_illumina.py [-h] --plate_info_path PLATE_INFO_PATH --qcd_results_path QCD_RESULTS_PATH

Process and organize illumina sequencing data.

options:
  -h, --help            show this help message and exit
  --plate_info_path PLATE_INFO_PATH
                        Path to the date_PlateInfo directory (e.g., /nfs/turbo/umms-
                        esnitkin/Project_Marimba/Sequence_data/illumina_fastq/2024-12-24_Plate1-to-Plate3
  --qcd_results_path QCD_RESULTS_PATH
                        Path to the QCD results directory (e.g.,
                        /scratch/esnitkin_root/esnitkin1/dhatrib/QCD/results/Project_MDHHS_QCD)

-->

> Ensure you have the paths to your plate directory and QCD results in handy.

```
python3 move_files_to_directories_illumina.py --plate_info_path /nfs/turbo/umms-esnitkin/Your_project_folder/Sequence_data/illumina_fastq/your_newly_created_plate_dir --qcd_results_path /scratch/esnitkin_root/esnitkin1/uniqname/QCD/results/your_project_name_QCD
```

**Your terminal window that you used to move the QCD outputs is busy and it will take anywhere from 1-4 hours (depending on the number of samples you have) to move the files. Please open another tab/terminal window if you need to contine using the terminal to work on other things.** 

**You will see a message on your terminal once your files have been moved successfully.**

<!--
10. If you 
-->
<!-- >
### Rule of thumb(s):
If you think you are going to be performing/carrying out computationally intensive tasks that are going to use more than 2 cores and/or 4G of memory, open an interactive session
-->