import glob, os
import subprocess
import shutil
import re
from typing import List
import numpy as np

def get_config(centroid: bool) -> str:
    if centroid:
        #create msconvert command with central wavelet transformation
        return ' --filter "peakPicking cwt msLevel=1-" --zlib --32 --filter "msLevel 1-2" --filter "titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState> File:"<SourcePath>".NativeID:"<Id>""'

    #create msconvert command without central wavelet transformation
    return ' --zlib --32 --filter "msLevel 1-2" --filter "titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState> File:"<SourcePath>".NativeID:"<Id>""'

def process_all_raw(path: str, raw: List[str]) -> List[int]:
    #annotate files before conversion; delete lockmass and any higher function folders in .raw data
    ##ms2 variable will show which function in .raw data is ____ ms level 2
    ms2 = []
    ##iterate over .raw files to annotate them one by one
    for j in range(len(raw)):
        #set working directory to .raw directory
        w = os.path.join(os.getcwd(), raw[j])
        os.chdir(w)
        #list files in .raw directory
        files = glob.glob(w + '/*')
        #get _extern.inf file
        info = (w + '\\' + "_extern.inf")
        #open _extern.inf file in binary reading mode
        f1 = open(info, 'rb')
        #load lines in file as list
        Lines = f1.readlines()
        #define first searchword. Some _extern.inf files will state which function belongs to the lockmass by adding REFERENCE in the function's header.
        #This is the easiest way to locate it.
        substring = b"REFERENCE"
        #define second searchword. Some _extern.inf files will not state which function belongs to the lockmass by adding REFERENCE in the function's header.
        #To locate the lockmass function, the second searchword is contained exclusively in all function headers.
        functions = b"Function Parameters - Function"
        #fun and number variable will be changed according to tested conditions
        number = "no"
        fun = "no"
        #iterate over _extern.inf file's lines
        for line in Lines:
            #look for substring "REFERENCE" in each line
            if substring in line:
                #if line contains "REFERENCE", this line also contains the function number belonging to the lockmass
                #x will contain this target line
                x = line.strip()
                #change x to character string
                x = str(x)
                #y is returned match object of search for (first occasion of) number(=function number we are looking for) in target line x
                y = re.search(r'\d', x)
                #change y to character string
                y = str(y)
                #split character string y to retrieve the number
                ##extract part of match object that states the match (first number in line)
                y = y.split("match='")[1].split("'")[0]
                ##in case the lockmass function number has 2 or 3 digits, extract again from the target line everything that comes between the first number (y) and the nect blank space
                z = x.split(y)[1].split(' ')[0].lstrip()
                ##ref is then the function's number we are looking for. if it has only one digit, z will be empty and ref = y
                ref = y+z
                #define substring that matches lockmass function number to respective lockmass function files in .raw directory.
                #Functions in the .raw directory contain "FUNC" followed by three digits stating the function number (003, 030, 300, for function 3, 30, and 300, respectively).
                ##get length/amount of digits of function number
                p = len(ref)
                ##redefine p as the number of zeros that need to be added before the function number to get a total of three digits.
                p = 3-p
                ##redefine p as a character string of this needed number of zeros.
                p = "0"*p
                ##change fun variable from "no" to the function number including zeros (e.g., "003")
                fun = p+ref
                ##change fun again to the entire string needed to identify files belonging to a certain function in a .raw directory (e.g., FUNC003)
                fun = "FUNC"+fun
                
                #we also want to delete functions with higher number than the lockmass, e.g., UV-detector function
                ##get the lockmass function's number we eveluated earlier(ref) as an integer
                r = int(ref)
                ##i will be extended by 1 for each iteration
                i = 0
                ##iterate over files in .raw directory
                for o in files:
                    #k will list the indices of files in .raw directory that contain the target functions (starting with the lockmass function)
                    k = list()
                    ##looking for lockmass function files in .raw directory files
                    if fun in o:
                        k.append(files.index(o))
                        #change k (within this iteration) to range of file indices between the first of this iteration's targeted function file and the last file in .raw directory.
                        ##indices within range k belong to files of functions we want to delete (lockmass and higher)
                        ##and are then followed by additional files in the .raw directory that we do not want to delete.
                        k = range(k[0],len(files))
                        #set up delete as list of indices of files to delete later
                        #(we could also delete all files defined by k that contain "FUNC", however, that would include the _FUNCTIONS.INF file and other files that might be present in some different types of .raw data containing the same character string.
                        #Because we don't know exactly what the contents of different .raw directories look like, the code is more complicated to specifically target only the actual functions.)
                        delete = list()
                        #func1 is the substring searching for function files we want to delete.
                        ##These files contain "FUNC" + lockmass function number(e.g., "FUNC003"), as well as any higher functions (e.g., "FUNC004", "FUNC005", ...)
                        ##with i being 0 in the first iteration, we do NOT add to the lockmass function number and target the lockmass function using "FUNC" + p + ref as we did earlier.
                        ##for following iterations, we add 1 to the lockmass function number, targeting higher functions.
                        func1 = str("FUNC"+p+str(int(r) + i))
                        #iterate over subset list of files k that we identified earlier in the .raw directory  
                        for a in k:
                            #check if the currently targeted function number can be found in the files, set m to its index within all files of the .raw directory.
                            ##if it cannot be found we already deleted lockmass and all higher functions present in the .raw directory.
                            if func1 in files[a]:
                                m = a
                                #while loop adds all file indices containing the targeted function's substring (should be 3 different files per function) to the delete list we created earlier.
                                while func1 in files[m]:
                                    delete.append(m)
                                    m +=1
                                #end of iteration
                                ##expand i by 1
                                i +=1
                                ##subsequently annotate function number substring to define new target (higher function than before)
                                func1 = str("FUNC"+p+str(int(r) + i))
                        #delete files in .raw directory which indices we collected in the delete list.        
                        for s in [files[s] for s in delete]:
                            os.remove(s)
        #if fun is still "no", we did not find the word REFERENCE in the _extern.inf file.
        if fun == "no":
            #we are iterating again over the lines in the _extern.inf file, searching for the substring that can be found in all function headers (functions variable we defined earlier).
            #number variable will be changed to the index of a line matching the function header substring.
            #number variable will be overwritten with each iteration. Fortunately, we want to find the last occuring function header in the _extern.inf file.
            #so far, all .raw data extern_inf files contain the lockmass function as the last function listed. Higher functions (UV-detector) are not listed in the
            #_extern.inf file. Therefore, the last function header in the _extern.inf file seems to always contain the number of the lockmass function.
            for line in Lines:
                if functions in line:
                    number = line
        #if the number variable is still "no" we probably detected the substring "REFERENCE" earlier.
        #if not, we did not find any function headers because the _extern.inf file is structured differently and the software will not delete any function files;
        #this may lead to errors in output data that are similar to convential MSConvert conversion.
        #note again that in case there exists such a thing as a file without a lockmass function, the last MS function will be deleted.
        #This is the last MS 2 level function in DDA, all MS 2 data in MSe, or all MS data (if only MS1 was aquired).
        
        #if the number variable is no longer "no" we detected the line with the last function header in the _extern.inf file, from which we can extract the function number most likely to belong to the lockmass.
        if number != "no":
            #we proceed to define the substring "FUNC" + function number as explained previously, then iterate over the files in the .raw directory to delete lockmass function files and files of any higher functions, same as above.
            x = number.strip()
            x = str(x)
            y = re.search(r'\d', x)
            y = str(y)
            y = y.split("match='")[1].split("'")[0]
            z = x.split(y)[1].split(' ')[0].lstrip()
            ref = y+z
            p = len(ref)
            p = 3-p
            p = "0"*p
            fun = p+ref
            fun = "FUNC"+fun
            r = int(ref)
            i = 0
            for o in files:
                k = list()
                if fun in o:
                    k.append(files.index(o))
                    k = range(k[0],len(files))
                    delete = list()         
                    func2 = str("FUNC"+p+str(int(r) + i))
                    for a in k:
                        if func2 in files[a]:
                            m = a
                            while func2 in files[m]:
                                delete.append(m)
                                m +=1
                            i +=1
                            func2 = str("FUNC"+p+str(int(r) + i))
                    for g in [files[g] for g in delete]:
                        os.remove(g)            
        #for each file that is being processed, we add the number of the lockmass function to append the ms2 list, as an integer (e.g., 3).
        ms2.append(int(ref))
        #end of .raw directory annotation, set working directory back to input directory for next iteration.
        os.chdir(path)
    return ms2

def ms_convert(path: str, msconvert: str, raw: List[str], config: str):
    #start actual conversion with msconvert.exe
    ##iterate over files in input directory, converting them individually.
    for i in raw:
        #print directory of file that is currently being converted
        print (path + '\\' + i + " ...converting")
        #call msconvert.exe (msconvert variable is directory of msconvert.exe), file to convert, and config file that has been defined in the beginning based on user input for centroiding.
        subprocess.call(msconvert + " " + i + config) 
        #print directory of file that is now converted to .mzML
        print (path + '\\' + i + " conversion completed!")

def annotate(path: str, mzml: str, ms2:List[int]):
    #start post-conversion annotation
    print("\n\n","annotating files...","\n\n")

    #msconvert.exe will save output .mzML files in the same directory of input .raw data, because it has not been specified otherwise in the config file.
    #get list with these .mzML files in input directory
    fn = glob.glob('*.mzML')  

    #change the .mzML files into .txt files by changing the file extensions from ".mzML" to ".txt".
    ##iterate over files to change them one by one
    for i in fn:
        #base = actual filename (before ".mzML")
        base = os.path.splitext(i)[0]
        #rename file i to base + extension ".txt".
        os.rename(i, base + '.txt')

    #copy these .txt files into output directory ("mzml" variable defined in the beginning).
    ##iterate over all files' entire directories
    for f in glob.glob(os.path.join(path,"*.txt")):
        #copy them to output directory
        shutil.copy2(f, mzml)

    #change working directory to ouput directory
    os.chdir(mzml)
    #get list with all .txt files now in ouput directory
    fn = glob.glob('*.txt')

    #iterate over all .txt files
    for j in range(len(fn)):
        #open the respective original .txt file that remained in the input directory in reading mode.
        ##specify the directory by using path variable(input file directory) and the same file name (j) it has in the output directory.
        f1 = open(os.path.join(path, fn[j]), 'r')
        #open the newer, copied .txt file in the ouput directory in writing mode.
        f2 = open(fn[j], 'w')
        
        #get a list of the lines contained in the file
        Lines = f1.readlines()
        #towards the beginning of the file, after the string "spectrumList count", it is stated how many spectra were acquired. We will search for this substring.
        substring = "spectrumList count"
        
        #we iterate over all lines to find the substring, then extract the line containing the substring in variable x
        for line in Lines:
            if substring in line:
                x = line.strip()
        #totalspectra variable extracts the number after the substring, the total amount of spectra        
        totalspectra = x.split('spectrumList count="')[1].split('"')[0]
        
        #replacement_index variable is the range of three times the amount of spectra.
        #This is because in the .txt file, every spectrum will be referenced 3 times. We will use the created range list to iterate over all these references/occurences in the .txt file.
        replacement_index = list(range(int(totalspectra))) #ignore this line
        replacement_index = list(range(int(totalspectra)*3))
        
        #specID_single is the range list of the actual scan IDs (scan IDs start with 1, not with 0, therefore, we shift the range)
        specID_single = list(range(1,int(totalspectra)+1))
        #specID is doubling these scan IDs (from 1,2,3,...,n -> 1,1,2,2,3,3,...,n,n)
        specID = np.repeat(specID_single, 2)
        #we change the entries in both specID_single and specID to character strings
        specID_single = [str(x) for x in specID_single]
        specID = [str(x) for x in specID]
        #specID_comb combines specID and specID_single (1,1,2,2,3,3,...,n,n,1,2,3,...,n)
        #This is because in the .txt file the scans are referenced in this order. First, spectral data and metadata is being listed for each scan, referencing the scan ID two times.
        #Then, at the end of the file, there is again a list of all scans ID references (their unique names), containing the scan ID as well.
        specID_comb = specID + specID_single
        
        #We want to change all scan IDs to a chronological order/correlating with RT. Other Vendors assign their scan IDs like this per default.
        #Waters starts numbering their scans seperately within the functions, i.e., first scan in function 1, first scan in function 2, first scan in function 3, etc., will all have the ID 1.
        #This can e.g., cause an MS 2 level scan at RT of 3min to have a lower scan ID than an MS 1 level scan at a RT of 4min. This appears to be an issue for some data processing softwares (e.g., MZmine 3).
        
        #we now identify the lines in the .txt file that contain the string "scan=" and append that list with the lines' indices by iterating over the lines in the .txt file.
        spectra = []
        for i in range(len(Lines)):
            if "scan=" in Lines[i]:
                spectra.append(i)
        
        #the length of the spectra variable must be the same as the length of replacement_index variable. 
        
        #we extract the number after "scan=", meaning the scan ID. This is the string between "scan=" and the next "&" or '"'.
        #we need a as an empty string to join two character strings ("scan=" and the ID).
        a = ''
        ##iteration as many times as "scan=" should be found in the .txt file.
        for i in replacement_index:
            index = ['scan=', Lines[spectra[i]].split('scan=')[1].split('&')[0].split('"')[0]]
            #join "scan=" and the extracted ID. This string will be replaced in the same line as "scan=" and the "correct", chronological ID.
            #we also substitute "scan=" instead of just the number, because the number alone may be present several times at different positions in the same line without referring to the scan ID.
            index = a.join(index)
            #substitute index variable (old "scan=" + ID) for "scan=" + new ID(from specID_comb defined earlier) in the current line (Lines[spectra[i]]).
            Lines[spectra[i]] = re.sub(index,a.join(['scan=', specID_comb[i]]),Lines[spectra[i]])
        
        #2nd part of post-conversion annotation is checking weather "high energy" MSe MS 2 level scans are listed as MS 1 and if so, correct them to MS 2. 
    
        #we are looking for data belonging to a scan in function 2. For MS/MS data, function 1 should be MS level 1, function 2 and higher should be MS level 2.
        #Additional other functions is what we deleted in .raw directory before conversion. Therefore, function 2 (if present) should be MS level 2.
        level1 = "function=2"
        
        #we are looking for the first occurence of "function=2" in the file. We define the "first" variable as that line in the .txt file.
        first = next(i for i in range(len(Lines)) if level1 in Lines[i])
        #we subset the list of lines in the document, discarding all lines before the first occurence of "function=2".
        subset = Lines[first:len(Lines)]
        #redifine the substring variable to search for '"ms level" value="', after which we find the assigned MS level.
        level1 = '"ms level" value="'
        #just like before, extract the first line in our subset (starting with the first occurence of "function=2"), that contains this new substring.
        ##This way we make sure to find the MS level belonging to the first function 2 scan.
        line = next(i for i in range(len(subset)) if level1 in subset[i])
        #extract the value of the MS level: Everything between '"ms level" value="' and the next '"'.
        level1 = subset[line].split('"ms level" value="')[1].split('&')[0].split('"')[0]
        
        #we check if the value of this first function 2 scan equals 1. If that is true, we will change it to 2 for all scans belonging to functions >1.
        ##(assuming that if the ms level is incorrect for the first function 2 scan, it will be incorrect for all MS/MS data)
        if level1 == "1":
            #we want to change the MS level values for all functions >=2 and < reference function.
            #with the ms2 variable, we already defined the function number of the reference function for each file we want to process.
            #e is the range of function numbers we want to target: all functions in the respective .txt file that are > 1.
            e = range(2,ms2[j])
            #we look for all lines containing "function=" + n, 1<n<lockmass, and save their indices in list z by iterating over the lines in the .txt file.
            z = []
            for ms in e:
                level = "function="+str(ms)
                for line in Lines:
                    if level in line:
                        z.append(Lines.index(line))
            #redefine z as a range from 0 to the last occurence (length of z).
            #BUT we need to cut off the aforementioned list at the end of the .txt file that lists all the scan names.
            #These names also contain "function=" + the function number, but there is no connection between this list at the end and the MS level value data.
            #Therefore, we only need the first 2/3 of the occurences of the substring "function=" + n.        
            z = z[0:int((len(z)/3)*2)]
            #2 consecutive line indices in z always belong to the same scan. The MS level value information for this scan can be found between these two lines.
            #for each scan, we want to extract a subset of lines belonging to this scan (between the 1st and 2nd index, the 3rd and 4th index, and so on)
            #we devide the entries in z into odd and even numbers and create 2 new lists, a(even) and b(odd).
            #Because we want to use a and b values as indices for z, we start with 0 (targeting the first entry of z) and end with the value length of z/2 - 1.
            #(z is devided by 2 to devide into a and b, half the numbers will be even, the other half odd.)
            a=[0]
            b=[1]
            for i in range(0,int(len(z)/2)-1):
                a.append(a[i]+2)
                b.append(b[i]+2)
            #mslevel is the substring we use to find the line containing the MS level value
            mslevel = '"ms level" value="'    
            #iterate over the number of scans which need their MS level changed (= length of z/2 = length of a = length of b) to extract the lines between a pair of "function=".
            #variable v will gather the indices of all lines in the .txt file with mslevel value occurences we need to change to "2".
            v = []
            for i in range(len(a)):
                #text variable is the subset of lines belonging to one scan
                text = Lines[z[a[i]]:z[b[i]]]
                #iterate over the subset of lines, looking for mslevel substring
                for u in text:
                    if mslevel in u:
                        #append index of line in .txt file. This is the index of the line in the subset (index(u), if mslevel in u) + the index of the first line of this subset when considering the entire .txt file (not just within the subset).
                        v.append(text.index(u)+z[a[i]])
            #iterate over all lines in v to substitute the MS level value "1" for "2".
            for i in range(len(v)):
                Lines[v[i]] = re.sub('value="1"','value="2"',Lines[v[i]])
        
        #write lines in the .txt file opened in writing mode in the mzML output folder.
        f2.writelines(Lines)
        #close both .txt files
        f1.close()
        f2.close() 
        #change .txt files back to .mzML by changing the extension back from ".txt" to ".mzML", like we did before but in the other direction.
        base = os.path.splitext(fn[j])[0]
        os.rename(fn[j], base + '.mzML')

    #delete initial .txt files used for reading
    ##change working directory back to input folder
    os.chdir(path)
    #list the .txt files
    fn = glob.glob('*.txt')
    #delete the .txt files
    for f in fn:
        os.remove(f)

    #annotation is completed
    print("\n\n","annotation completed!","\n\n")

if __name__ == '__main__':
    #get the working directory; the .py file needs to be in the software folder, next to the .exe file for it to work
    P = os.getcwd()

    #get user input: should msconvert.exe's central wavelet transformation be applied? 
    datatype = input("Are you trying to convert profile data that needs to be centroided? [y/n]\n")

    i=1
    while datatype not in "yn":
        datatype = input("Please enter 'y' for yes or 'n' for no.\n")
        i += 1

    if i > 2:
        print("This took you " + str(i) + " tries." )

    config = get_config(datatype=='y')
    if datatype == "y":
        print("Data is profile data and will be centroided using CWT.")
    else:
        if datatype == "n": 
            print("Profile data will not be centroided. Centroid data will remain centroided.")

    #set working directory to main folder    
    os.chdir(P)
    #define directories for input and output folders, and msconvert.exe
    path = os.path.join(os.getcwd(), r'raw_files')
    mzml = os.path.join(os.getcwd(), r'mzML_files')
    msconvert = os.path.join(os.getcwd(), r'pwizLibraries-and-Installation\pwiz_Leave-Alone\msconvert.exe')

    #set working directory to input folder
    os.chdir(path)
    os.getcwd() #checking directory
    #list files in input folder that are NOT .raw
    fn = glob.glob('*[!".raw"]')
    #delete files in list
    for f in fn:
        os.remove(f)

    #list remaining .raw folders in input folder   
    raw = glob.glob('*.raw')    

    #print names of .raw folders that will be processed
    print("processing files:")
    for j in range(len(raw)):
        print(raw[j])

    ms2 = process_all_raw(path, raw)
    ms_convert(path, msconvert, raw, config)
    annotate(path, mzml, ms2)

    k=input("press close to exit")

    #keep window open
    while True:
        pass
