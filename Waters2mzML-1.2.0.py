import glob, os
import subprocess
from subprocess import call
import shutil
import re
import numpy as np


P = os.getcwd()

datatype = input("Are you trying to convert profile data that needs to be centroided? [y/n]\n")

i=1
while datatype not in "yn":
    datatype = input("Please enter 'y' for yes or 'n' for no.\n")
    i += 1

if i > 2:
    print("This took you " + str(i) + " tries." )

if datatype == "y":
    print("Data is profile data and will be centroided using CWT.")
    config = ' --filter "peakPicking cwt msLevel=1-" --zlib --32 --filter "msLevel 1-2" --filter "titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState> File:"<SourcePath>".NativeID:"<Id>""'
else:
    if datatype == "n": 
        print("Profile data will not be centroided. Centroid data will remain centroided.")
        config = ' --zlib --32 --filter "msLevel 1-2" --filter "titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState> File:"<SourcePath>".NativeID:"<Id>""'

    
os.chdir(P)
path = os.path.join(os.getcwd(), r'raw_files')
mzml = os.path.join(os.getcwd(), r'mzML_files')
msconvert = os.path.join(os.getcwd(), r'pwizLibraries-and-Installation\pwiz_Leave-Alone\msconvert.exe')

os.chdir(path)
os.getcwd()
fn = glob.glob('*[!".raw"]')
for f in fn:
    os.remove(f)
    
raw = glob.glob('*.raw')    

print("processing files:")
for j in range(len(raw)):
    print(raw[j])

ms2 = []
for j in range(len(raw)):
    w = os.path.join(os.getcwd(), raw[j])
    os.chdir(w)
    files = glob.glob(w + '/*')
    info = (w + '\\' + "_extern.inf")
    f1 = open(info, 'rb')
    Lines = f1.readlines()
    substring = b"REFERENCE"
    functions = b"Function Parameters - Function"
    number = "no"
    fun = "no"
    for line in Lines:
        if substring in line:
            x = line.strip()
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
                    func1 = str("FUNC"+p+str(int(r) + i))
                    for a in k:
                        if func1 in files[a]:
                            m = a
                            while func1 in files[m]:
                                delete.append(m)
                                m +=1
                            i +=1
                            func1 = str("FUNC"+p+str(int(r) + i))
                    for s in [files[s] for s in delete]:
                        os.remove(s)
    if fun == "no":
        for line in Lines:
            if functions in line:
                number = line
    if number != "no":
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
    ms2.append(int(ref))                     
    os.chdir(path)
            

for i in raw:
    print (path + '\\' + i + " ...converting") 
    subprocess.call(msconvert + " " + i + config) 
    print (path + '\\' + i + " conversion completed!")
 

print("\n\n","annotating files...","\n\n")

fn = glob.glob('*.mzML')  

for i in fn:
    base = os.path.splitext(i)[0]
    os.rename(i, base + '.txt')
    
for f in glob.glob(os.path.join(path,"*.txt")): 
    shutil.copy2(f, mzml)


os.chdir(mzml)
fn = glob.glob('*.txt')

for j in range(len(fn)):
    f1 = open(os.path.join(path, fn[j]), 'r')
    f2 = open(fn[j], 'w')
    
    Lines = f1.readlines()
    substring = "spectrumList count"
    
    for line in Lines:
        if substring in line:
            x = line.strip()
    totalspectra = x.split('spectrumList count="')[1].split('"')[0]
    
    replacement_index = list(range(int(totalspectra)))
    replacement_index = list(range(int(totalspectra)*3))
    
    specID_single = list(range(1,int(totalspectra)+1))
    specID = np.repeat(specID_single, 2)
    specID_single = [str(x) for x in specID_single]
    specID = [str(x) for x in specID]
    specID_comb = specID + specID_single
    
    spectra = []
    for i in range(len(Lines)):
        if "scan=" in Lines[i]:
            spectra.append(i)
    
    a = ''
    for i in replacement_index:
        index = ['scan=', Lines[spectra[i]].split('scan=')[1].split('&')[0].split('"')[0]]
        index = a.join(index)
        Lines[spectra[i]] = re.sub(index,a.join(['scan=', specID_comb[i]]),Lines[spectra[i]])
    
    level1 = "function=2"
    
    first = next(i for i in range(len(Lines)) if level1 in Lines[i])
    subset = Lines[first:len(Lines)]
    level1 = '"ms level" value="'
    line = next(i for i in range(len(subset)) if level1 in subset[i])
    level1 = subset[line].split('"ms level" value="')[1].split('&')[0].split('"')[0]
    
    if level1 == "1":
        e = range(2,ms2[j])
        z = []
        for ms in e:
            level = "function="+str(ms)
            for line in Lines:
                if level in line:
                    z.append(Lines.index(line))
        z = z[0:int((len(z)/3)*2)]
        a=[0]
        b=[1]
        for i in range(0,int(len(z)/2)-1):
            a.append(a[i]+2)
            b.append(b[i]+2)
        mslevel = '"ms level" value="'    
        v = []
        for i in range(len(a)):
            text = Lines[z[a[i]]:z[b[i]]]
            for u in text:
                if mslevel in u:
                    v.append(text.index(u)+z[a[i]])
        
        for i in range(len(v)):
            Lines[v[i]] = re.sub('value="1"','value="2"',Lines[v[i]])
    
    f2.writelines(Lines)
    f1.close()
    f2.close()    
    base = os.path.splitext(fn[j])[0]
    os.rename(fn[j], base + '.mzML')

os.chdir(path)
fn = glob.glob('*.txt')    
for f in fn:
    os.remove(f)

print("\n\n","annotation completed!","\n\n")

k=input("press close to exit")

while True:
    pass