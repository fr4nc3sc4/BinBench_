# prova
import subprocess
import os
import sys
from argparse import ArgumentParser

# shared_dir: name of the volume shared between the docker container and the OS


parser = ArgumentParser(description='Debugs two programs and finds out if the hit lines are different')
parser.add_argument('--src_folder', dest='src', type=str, help='source folder of the project to be compiled', default=None)
parser.add_argument('--parallel', dest="parallel", type=int, help='numero di thread per make -j', default=4)
parser.add_argument('--password', dest="password", type=str, help='sudo password', default="4")

args = parser.parse_args()
proj_name = "curl"
shared_dir = args.src
parallel=args.parallel
password=args.password

dir = os.getcwd().split("/")

# subprocess.call("docker images",shell=True)
# subprocess.call("export LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LIBRARY_PATH",shell=True)
lista_compilatori = [
    'docker-gcc5',
]

for x in lista_compilatori:
    print("Compiling with " + str(x))

    #subprocess.call("docker start " + x + " -v", shell=True)

    # d = subprocess.call("pwd")

    for y in ['O0', 'O1', 'O2', 'O3']:
        print("Optimization level "+y)
        directory_compilati=os.getcwd()+"/"+shared_dir+"_compilati/"+ x + "/" + str(y)
        subprocess.call("mkdir -p "+directory_compilati, shell=True)
        proj_dir= os.getcwd()+"/"+shared_dir+"/"
        #subprocess.call("mkdir -p ../" + dir + "_compilati/" + str(x.split('/')[3]) + "/" + str(y), shell=True)
        print("Forcing the compiler optimization to" + str(y) + " in configure")
        subprocess.call("sed -i -e 's/-O3/-" + str(y) + "/g' "+shared_dir+"/configure", shell=True)
        subprocess.call("sed -i -e 's/-O2/-" + str(y) + "/g' "+shared_dir+"/configure", shell=True)
        subprocess.call("sed -i -e 's/-O1/-" + str(y) + "/g' "+shared_dir+"/configure", shell=True)
        subprocess.call("sed -i -e 's/-O0/-" + str(y) + "/g' "+shared_dir+"/configure", shell=True)


        print("Starting Configure") # aggiungere colore
        subprocess.call(
        'docker run -w /home/ -it -v '+proj_dir+':/home/ '+ x + ' ./configure CFLAGS="-g -' + y + '" CXXFLAGS="-g -' + y + ' "',
        shell=True)
        print("Ending Configure")

        #print("Executing:"+ "find "+proj_dir+" -type f -exec sed -i -e 's/-O3/-"+str(y)+"/g' {} \;")
        #sys.stdout.flush()
        #subprocess.call("find "+proj_dir+" -type f -exec sed -i -e 's/-O3/-"+str(y)+"/g' {} \;", shell=True)
        #print("Executing:"+"find "+proj_dir+" -type f -exec sed -i -e 's/-O2/-" + str(y) + "/g' {} \;")
        #sys.stdout.flush()
        #subprocess.call("find "+proj_dir+" -type f -exec sed -i -e 's/-O2/-" + str(y) + "/g' {} \;", shell=True)
        #print("Executing:"+"find "+proj_dir+" -type f -exec sed -i -e 's/-O1/-" + str(y) + "/g' {} \;")
        #sys.stdout.flush()
        #subprocess.call("find "+proj_dir+" -type f -exec sed -i -e 's/-O1/-" + str(y) + "/g' {} \;", shell=True)
        #print("Executing:"+"find "+proj_dir+" -type f -exec sed -i -e 's/-O0/-" + str(y) + "/g' {} \;")
        #sys.stdout.flush()
        #subprocess.call("find "+proj_dir+" -type f -exec sed -i -e 's/-O0/-" + str(y) + "/g' {} \;", shell=True)


        print("Making")
        subprocess.call(
            'docker run -w /home/ -it -v ' + proj_dir + ':/home/ ' + x + ' make -j'+str(parallel),
            shell=True)

        print("Change ownership")
        subprocess.call(
            "echo "+password+" | sudo chown  -R fconsole " + proj_dir,
            shell=True)

        print("Saving binary files")
        subprocess.call(
            "find "+proj_dir+" -name '*.o' -exec mv -f {} "+directory_compilati+" \;",
            shell=True)

        for subdir, dirs, files in os.walk(proj_dir):
            for file in files:

               f = os.path.join(subdir, file)
               output = subprocess.check_output('file ' + f, shell=True)

               if 'executable' in output and 'ELF' in output:
                   # sposti il file in directory_compilati
                   print("ELF FILE: " + f)
                   print("output FILE: " + output)
                   print("move ELF file in "+directory_compilati+"/"+file)
                   os.rename(f, directory_compilati+"/"+file)

        subprocess.call("cd " + proj_dir + "&& make clean && make distclean", shell=True)

"""
        ##spostare non solo gli o ma tutti gli elf file
        #girare su tutti i file ni project -- no docker
        for file in files:
            f = os.join(subdir, file)
            output = subprocess.check_output('file ' + f, shell=True)
            print(output)
            if 'executable' in output and 'ELF' in output:
                print('sposta')
                # sposti il file in directory_compilati
                #os.rename(f, "../" + os.path.basename(f) + "_compilati" + str(x.split('/')[3]) + str(y))

        subprocess.call("cd "+proj_dir+"&& make clean && make distclean", shell=True)
"""

"""
    subprocess.call("find . -name '*.o' -exec mv {} ../"+dir+"_compilati/"+str(x.split('/')[3])+"/"+str(y)+"/ \;", shell=True)
    for subdir, dirs, files in os.walk("."):

    subprocess.call("make clean", shell=True)
    subprocess.call("make distclean", shell=True)
    print("Finished Compilation with"+str(x))


"""
