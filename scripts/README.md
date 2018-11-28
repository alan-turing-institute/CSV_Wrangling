# Script Directory

The scripts are organized as follows:

1. **analysis** contains the code necessary to generate the figures, tables, 
   and constants.

2. **common** contains shared code for analysis, detection, and preprocessing. 
   Among other things it contains definitions for the detector result and 
   dialect objects, the parser we use, and utilities for encoding detection 
   and file loading.

3. **detection** contains the code for each of the detectors. Every detector 
   has a separate file. Those implemented in Python have a common commandline 
   interface defined in ``core.py``. Code for HypoParsr and type detection are 
   in the **lib** subdir.

4. **preprocessing** contains the code for automatic dialect detection using 
   so-called ''normal forms''


The files in this folder are top-level wrapper scripts that are actually 
needed to run everything.
