# Waters2mzML V1.1.3

*currently issues with profile data and MSe data, see below*


Waters2mzML converts and subsequently annotates Waters .raw MSn data (both MSe and DDA) into functional .mzML files. Obtained .mzML files can be processed in MZmine 3. It would be interesting to see if it works for all Waters .raw data and other processing streamlines.

Based on the raw data's "_extern" file, Waters2mzML deletes lockmass (reference mass) functions - if present - and converts the files to .mzML using ProteoWizard‘s MSConvert. Obtained .mzML files are annotated as .txt files, renumbering the scans.

## Prerequisites
Our data was aquired with a Waters Synapt G2 Si, MassLynx V4.2. Waters2mzML V1.1.2 now also includes Waters Xevo G2 DDA .raw data.
It is yet unclear if it will work for other Waters .raw data.
Waters2mzML has so far only been tested on Windows 10, 64bit.

## How to use
-	Do not delete or rename any of the files or folders.
-	Put COPIES of your Waters .raw files into raw_files folder (files will be annotated)
-	Execute Waters2mzML-1.1.3exe
-	Wait for console window to show „annotation completed!“
-	Find functional .mzML files in the mzML_files folder. Desktop

Before converting a new batch: Remove previously processed files from mzML_files folder. The software will process them again. While this will not corrupt them, it will extend execution time.

### MSe data

V1.1.3 can convert MSe data, but for all MS level 2 scans a constant precursor mass is assigned.

### Profile data

V1.1.3 output is still profile data. Converting the .mzML output files again using msconvert GUI and vendor peakPicking filter can centroid them. As this does not seem to work in command line, you need to do this yourself after processing the files in Waters2mzML.
After you generate centroid data, MZmine3 still shows an error message (Scans containing 0 values). Please check/compare to your raw data and make sure the .mzML output is reliable.

## Developers

I developed Waters2mzML in an effort to use my Waters .raw MSn data to do nontargeted metabolomics for my master’s thesis. Feel free to let me know if the software worked for your data or if you have any comments:
anja.prisching@uni-oldenburg.de


## References

1.	Chambers, M., Maclean, B., Burke, R. et al. A cross-platform toolkit for mass spectrometry and proteomics. Nat Biotechnol 30, 918–920 (2012).
2.	https://proteowizard.sourceforge.io/tools/msconvert.html  
