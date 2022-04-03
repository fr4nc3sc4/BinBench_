import requests
import os
import subprocess
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
import tqdm


def processPGKBUILD(pckgbuildfile):
    try:
        p=PkgParser(pckgbuildfile)
        p.download()
        p.extract()
        for y in ['O0','O1','O2','O3']:
            dir_proj=p.filezip.split('.tar')[0] #assuming tar
            p.get_compile_bash_script(scriptname=dir_proj+'/ourbuild'+y+'.sh',sedtrick=True, force_opt_level=y)
        subprocess.call('cp '+pckgbuildfile+' '+dir_proj+'/')
        #p.removePkg()
    except Exception as e:
        print("error when handling "+str(pckgbuildfile) +' '+str(e))


class DatasetCreation:

    def __init__(self,folder):
        self.folder=folder
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
        self.all_files = [join(self.folder,f) for f in onlyfiles]


    def process(self,nprocesses=10):
        pool=Pool(processes=nprocesses)
        list(tqdm.tqdm(pool.imap(processPGKBUILD, self.all_files), total=len(self.all_files)))


class PkgParser:

    def __init__(self,filename):
        self.file=filename
        self.vars={}
        self.build_lines=[]
        os.chdir('/'.join(filename.split('/')[:-1]))
        with open(self.file,'r') as f:
            build=False
            for x in f.readlines():
                x = x.strip()
                if 'build' in x and '{' in x:
                    build=True
                elif '=' in x and not build:
                    key=x.split('=')[0]
                    value=x.split('=')[1]
                    self.vars[key]=value
                elif x=='}':
                    build=False
                elif build:
                    #print(x)
                    self.build_lines.append(x)
        self.adjust_vars()


    def adjust_vars(self):
        for x in self.vars.keys():
            for y in self.vars.keys():
                substring="$"+str(x)
                val=self.vars[y]
                if substring in val:
                    newval=val.replace(substring,self.vars[x])
                    self.vars[y]=newval


    def download(self):
        if 'source' not in self.vars:
            print('source not found for package')
        try:
            url=self.vars['source']
            #print(url)
            if ')' in url:
                url=url[1:-1]
            else:
                url=url[1:]
            if '"' in url:
                url=url.split('"')[1]

            if '{' in url:
                url=url.split('{')[0]
            #print(url)
            #r = requests.get(url, allow_redirects=True)
            subprocess.call('wget '+url,shell=True, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            #open(url.split('/')[-1], 'wb').write(r.content)
            self.filezip=os.path.abspath(url.split('/')[-1])
            return self.filezip
        except Exception as e:
            print('Error on downloading'+str(e))
            return None


    def extract(self):
        # this battery of if is the same but if some fails than the corresponding
        # extraction utils should be installed
        # e.g. if tar.lz fails than lzip should be installed maybe we have to throw
        # a specific error?
        #print(self.filezip)
        if '.tar.gz' in self.filezip:
            uncompress_string="tar -xzvf "+self.filezip+""
            subprocess.call(uncompress_string,shell=True)
        elif '.tar.bz2' in self.filezip:
            uncompress_string = "tar -xjf " + self.filezip + ""
            subprocess.call(uncompress_string, shell=True)
        elif '.tar.lzma' in self.filezip:
            uncompress_string = "tar -xvf " + self.filezip + ""
            subprocess.call(uncompress_string, shell=True)
        elif '.tar.lz' in self.filezip:
            uncompress_string = "tar --lzip -xvf " + self.filezip + ""
            subprocess.call(uncompress_string, shell=True)
        elif '.zip' in self.filezip:
            uncompress_string = "unzip " + self.filezip + ""
            subprocess.call(uncompress_string, shell=True)
        elif '.xz' in self.filezip:
            uncompress_string = "tar -xJf " + self.filezip + ""
            subprocess.call(uncompress_string, shell=True)
        else:
            uncompress_string = "tar -xzvf " + self.filezip + ""
            subprocess.call(uncompress_string, shell=True)


    def clean_build_lines(self):
        r=[]
        for l in self.build_lines:
            ns=l
            for x in self.vars.keys():
                substring = "$" + str(x)
                if substring in l:
                    ns = ns.replace(substring, self.vars[x])
            r.append(ns)
        #print(r)
        return r



    def get_compile_bash_script(self,scriptname='build.sh',sedtrick=False, force_opt_level='O0'):
        r=self.clean_build_lines()
        if not sedtrick:
            with open(scriptname,'w') as f:
                for x in r:
                    f.write(x+'\n')
        else:
            #we force the opt_level with the seed trick
            pointer=0
            sed_lines=[]
            sed_lines.append("")
            sed_lines.append("sed -i -e 's/-O3/-" + str(force_opt_level) + "/g' ./configure")
            sed_lines.append("sed -i -e 's/-O2/-" + str(force_opt_level) + "/g' ./configure")
            sed_lines.append("sed -i -e 's/-O1/-" + str(force_opt_level) + "/g' ./configure")
            sed_lines.append("sed -i -e 's/-O0/-" + str(force_opt_level) + "/g' ./configure")
            sed_lines.append("")

            for i,x in enumerate(r):
                if 'cd' in x:
                    pointer=i
                    break
            r=r[:pointer+1]+sed_lines+r[pointer+2:]

            # we force the opt_level with the seed trick
            pointer = 0
            sed_lines = []
            sed_lines.append("")
            sed_lines.append("find . -type f -exec sed -i -e 's/-O3/-"+str(force_opt_level)+"/g' {} \;")
            sed_lines.append("find . -type f -exec sed -i -e 's/-O2/-"+str(force_opt_level)+"/g' {} \;")
            sed_lines.append("find . -type f -exec sed -i -e 's/-O1/-"+str(force_opt_level)+"/g' {} \;")
            sed_lines.append("find . -type f -exec sed -i -e 's/-O0/-"+str(force_opt_level)+"/g' {} \;")
            sed_lines.append("")

            for i, x in enumerate(r):
                if 'make' in x and '#' not in x:
                    pointer = i
                    break
            r = r[:pointer - 1] + sed_lines + r[pointer:]
            with open(scriptname,'w') as f:
                for x in r:
                    f.write(x+'\n')

    #this remove the file
    def removePkg(self):
        os.remove(self.file)
        os.remove(self.filezip)




if __name__ == "__main__":
    dc=DatasetCreation('/home/luca/binbench/archdownloader/PKGBUILD-list')
    dc.process()
    #p=PkgParser('/home/luca/binbench/archdownloader/PKGBUILD-list/aeolus.PKGBUILD')
    #print(p.download())
    #print(p.build_lines)
    #p.extract()
    #p.get_compile_bash_script(sedtrick=True)