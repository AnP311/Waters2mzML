# Waters2mzML
Waters2mzML converts and subsequently annotates Waters .raw MSn data (both MSe and DDA) into functional .mzML files. Obtained .mzML files can be processed in MZmine 3. It would be interesting to see if it works for all Waters .raw data and other processing streamlines.

Waters2mzML deletes lockmass and UV detector functions and converts the files to .mzML using ProteoWizard‘s MSConvert. Obtained .mzML files are annotated as .txt files, renumbering the scans.

##Prerequisites
Our data was aquired with a Waters Synapt G2i, MassLynx V4.2. It is yet unclear if it will work for other Waters .raw data.
Waters2mzML will currently only work if the last two functions in your .raw folder belong to lockmass and UV detector, consisting of 3 and 2 files, respectively, and are followed by three additional files (“_FUNCTNS“, “_HEADER“, and “_INLET“). See .raw setup example pic: /Example_.raw_DDA_file
Waters2mzML has so far only been tested on Windows 10, 64bit.

##How to use
-	Do not delete or rename any of the files or folders.
-	Put COPIES of your Waters .raw files into raw_files folder (files will be annotated)
-	Execute Waters2mzML1.0.exe
-	Wait for console window to show „annotation completed!“
-	Find functional .mzML files in the mzML_files folder.

Before converting a new batch: Remove previously processed files from mzML_files folder. The software will process them again. While this will not corrupt them, it will extend execution time.

###Config file

The config file can be changed according to ProteoWizard‘s MSConvert command line input:
https://proteowizard.sourceforge.io/tools/msconvert.html
Make sure not to delete spaces before and after command. 


##Developers

I developed Waters2mzML in an effort to use my Waters .raw MSn data to do nontargeted metabolomics for my master’s thesis. Feel free to let me know if the software worked for your data or if you have any comments:
anja.prisching@uni-oldenburg.de


##References

1.	Chambers, M., Maclean, B., Burke, R. et al. A cross-platform toolkit for mass spectrometry and proteomics. Nat Biotechnol 30, 918–920 (2012).
2.	https://proteowizard.sourceforge.io/tools/msconvert.html  
