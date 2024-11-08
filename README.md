# Data Flow SOP
The following are crucial steps as part of the [Snitkin lab](https://thesnitkinlab.com/index.php) Data Flow SOP. This project provides tools and workflows for processing Illumina, Nanopore, and hybrid sequencing samples. Depending on your dataset type, follow the respective guide for instructions.

## Available Workflows

### 1. **Illumina Samples**
The necessary files for Nanopore workflow can be found in the `illumina/` directory. For detailed instructions on processing Illumina sequencing data, refer to the following documentation:
- [Processing Illumina Samples](processing-illumina-samples.md)

You can also explore the related scripts and files in the current directory:
- `create_directories.py`
- `create_higher_level_dirs.py`

### 2. **Nanopore Samples**
The necessary files for Nanopore workflow can be found in the `nanopore/` directory. If you're working with Nanopore sequencing data, please consult the guide below:
- [Processing Nanopore Samples](processing-nanopore-samples.md)

<!-- 
### 3. **Hybrid Samples (Illumina + Nanopore)**
For hybrid samples that involve both Illumina and Nanopore data, use the following instructions:
- [Processing Hybrid Samples](processing-hybrid-samples.md)

Check the `hybrid/` directory for additional tools specific to hybrid workflows.
-->
## Directory Structure

This repository is organized as follows:

```
Data-Flow-SOP
├── create_directories.py
├── create_higher_level_dirs.py
├── illumina
│   ├── move_files_to_directories_illumina.py
│   └── rename_samples_illumina.sh
├── nanopore
│   ├── move_files_to_dirs_nanopore.py
│   └── rename_samples_nanopore.sh
├── pics
│   ├── globus-raw-fastq-nanopore.png
│   ├── globus_raw_fastq.png
│   ├── transfer-nanoQC-results.png
│   └── transfer-qcd-results.png
├── processing-hybrid-samples.md
├── processing-illumina-samples.md
├── processing-nanopore-samples.md
└── README.md

```

## Getting Started
To start, choose the appropriate workflow based on your sequencing platform and follow the respective guide.

For any questions or issues, please feel free to reach out to Dhatri or add an issue in the issues tab.


