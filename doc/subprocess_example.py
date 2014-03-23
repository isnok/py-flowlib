import sys
import subprocess

def pipe(src, dest):
    acc = chunk = src.read(1)
    while chunk != '':
        acc += chunk
        chunk = src.read(1)
    dest.write(acc + '\n')
    dest.flush()

cmdping = "./etst.sh"
p = subprocess.Popen(cmdping, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

while True:

    pipe(p.stdout, sys.stdout)
    if p.poll() is not None:
        print "one"
        break

    pipe(p.stderr, sys.stdout)
    if p.poll() is not None:
        print "two"
        break


sys.stdout.write("p finished.\n")
sys.stdout.write("Return code was: %s\n" % p.returncode)
sys.stdout.flush()
