# Data Flow SOP

This repository outlines the steps for processing data as part of the [Snitkin Lab](https://thesnitkinlab.com/index.php) Data Flow Standard Operating Procedure (SOP). The Data Flow SOP details how to process your samples after they've been sequenced by either the Genomics Core or Plasmidsaurus. To begin, select the guide that corresponds to your sample type—Illumina, Nanopore, or hybrid (Illumina + Nanopore).

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

### 3. **Hybrid Samples (Illumina + Nanopore)**
*This section is coming soon.*

<!-- For hybrid samples that involve both Illumina and Nanopore data, use the following instructions:
- [Processing Hybrid Samples](processing-hybrid-samples.md)
<!-- 
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

To begin, select the appropriate workflow based on your sequencing method and follow the corresponding guide.

For any questions or issues, please open an issue on [Github](https://github.com/Snitkin-Lab-Umich/Data-Flow-SOP/issues). For urgent inquiries, contact Dhatri on Slack or via email at dhatrib@umich.edu.

