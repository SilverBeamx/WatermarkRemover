# WatermarkRemover
Python script used to remove/deactivate watermarks in PDF files.

This script is only able to remove watermarks that have been registered as "Watermark" PDF Artifacts. If the script fails to remove watermarks it means that the PDF it was used on employs a custom solution, and thus must be handled with a custom script.

Each file, before being manipulated, is backed up into the "backup" folder.
The output files replace the input ones in the directory they originated from. The original files' creation time is preserved in the new files for easy date sorting.

A Windows batch file is provided in order to enable drag-and-dropping of files. Select the files you want to work on and drop them onto the batch file in order to launch the script with them as arguments.

Usage: python WatermarkRemover.py <file1.pdf>, <file2.pdf>, ...
