# rename files in a folder, based on title name and extension type, increment 1 to the final name
# mostly used for movie series

import glob, os

def rename(dir, pattern):
    for pathAndFilename in glob.iglob(os.path.join(os.getcwd(), pattern)):
            filename, ext = os.path.splitext(os.path.basename(pathAndFilename))
            wordsRaw = filename.split(" ")
            titleRaw = wordsRaw[-1]
            titleWords = titleRaw.split("_")
            titles = titleWords[:-2]
            titlefinal = " ".join(str(x.title()) for x in titles)
            print("2: ", titlefinal)
            os.rename(pathAndFilename, os.path.join(os.getcwd(), titlefinal + ext))
            

## call the function, specify directory, pattern, and title pattern

if __name__ == '__main__':
    rename(r'./', r'*.mp4')
