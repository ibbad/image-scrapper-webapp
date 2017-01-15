import os
import zipfile

filename = '../cs.helsinki.fi.zip'
foo = zipfile.ZipFile(filename, 'w')

for root, dirs, files in os.walk(os.getcwd()):
    for f in files:
        print ("archiving file %s" % (f))
        foo.write(f, os.path.relpath(f, root))
foo.close()
