# Waters2mzML V1.2.0

Waters2mzML converts and subsequently annotates Waters .raw MS1 or MSn data (both MSe and DDA) into functional .mzML files. Obtained .mzML files can be processed in MZmine 3. It is currently being tested if it works for all Waters .raw data and other processing streamlines. Feel free to try it and let me know.

Based on the raw data's "_extern" file, Waters2mzML deletes obsolete functions, e.g., lockmass (reference mass) - if present - and converts the files to .mzML using ProteoWizard‘s msconvert.exe. Obtained .mzML files are annotated as .txt files, renumbering the scans and reassigning the correct MS-levels if missing.

## Prerequisites
Our data was aquired with a Waters Synapt G2 Si, MassLynx V4.2. Waters2mzML V1.1.2 now also includes Waters Xevo G2 DDA .raw data.
It is yet unclear if it will work for other Waters .raw data.
Waters2mzML has so far only been tested on Windows 10, 64bit.

## How to use
-	Do not delete or rename any of the initial files or folders.
-	Put COPIES of your Waters .raw files into raw_files folder (files will be annotated)
-	Execute Waters2mzML-1.2.0.exe
- The program will ask if you are trying to convert profile data into centroid data. Enter 'y' or 'n'.
  If you answer no, centroid data will remain centroid and profile data will remain profile.
-	Wait for console window to show „annotation completed!“
-	Find functional .mzML files in the mzML_files folder.
- Please check the output files and compare them to raw data before proceeding with your analysis. 

Before converting a new batch: Remove previously processed files from mzML_files folder.

### Profile data to centroid

V1.2.0 is being centroided using ProteoWizard's CWT peak picking filter. The vendor conversion appears not to be applicable to Waters .raw data.


## Developers

I developed Waters2mzML in an effort to use my Waters .raw MSn data to do nontargeted metabolomics for my master’s thesis. Feel free to let me know if the software worked for your data or if you have any comments. I am happy to have a look at data you couldn't process and make :
anja.prisching@uni-oldenburg.de


## References

1.	Chambers, M., Maclean, B., Burke, R. et al. A cross-platform toolkit for mass spectrometry and proteomics. Nat Biotechnol 30, 918–920 (2012).
2.	https://proteowizard.sourceforge.io/tools/msconvert.html  
