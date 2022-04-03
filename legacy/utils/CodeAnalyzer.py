from guesslang import Guess
import magic

import os

class CodeAnalyzer:

    def __init__(self,project_folder):
        self.project_folder=project_folder


    def get_top4_languages(self):
        languages=dict()
        onlyfiles = [os.path.join(path, name) for path, subdirs, files in os.walk(self.project_folder) for name in files]
        #onlyfiles = [join(self.project_folder,f) for f in onlyfiles]
        with magic.Magic() as davidcopperfield:
            for x in onlyfiles[0:4000]:
                try:
                    idf = davidcopperfield.id_filename(x)
                    if 'source' in idf:
                        language = idf.split('source')[0]
                        if language in languages:
                            languages[language]=languages[language]+1
                        else:
                            languages[language]=1
                except Exception:
                    continue

        return [x[0] for x in sorted(languages.items(), key=lambda item: item[1],reverse=True)][0:4]



if __name__=="__main__":
    path='/Users/giuseppe/PycharmProjects/BinBench/archdownloader/binutils-2.35.1'
    c=CodeAnalyzer(path)
    print(c.get_top10_languages())