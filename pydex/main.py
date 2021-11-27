import os, sys, glob
import subprocess
import json
from .texstrings import CHAPTER, SECTION, FIGURE, CLEAR, END

DPI = 150
COLOR = {
	'purple': '\033[95m',
	'blue': '\033[94m',
	'green': '\033[92m',
	'yellow': '\033[93m',
	'red': '\033[91m',
	'white': '\033[0m',
	'bold': "\033[1m",
}

def getparams(parampath):
    '''
    Load the projects and files in the parameters file.
    '''
    return json.load(parampath)


def enum(projects):
    '''
    Count the number of files to process.
    '''
    n, p = 0, 0
    for p in projects:
        n += len(projects[p]['flist'])
        p += 1
    return n, p


def printM(msg, color='green'):
    '''
    Display a printed message in color.
    '''
    print('%s%s%s%s' % (COLOR['bold'], COLOR[color], msg, COLOR['white']))


def process(ifn, ofn, gain, dpi=DPI):
    '''
    Call the process with the desired flags.
    Flags are detailed here:
    https://readgssi.readthedocs.io/en/latest/general.html#bash-usage
    '''
    subprocess.call(['readgssi',
                     '-i', ifn,         # input file
                     '-g', gain,        # gain
                     '-o', ofn,         # output file
                     '-T',              # plot title off
                     '-n',              # don't show plot window
                     '-N',              # distance normalization
                     '-Z', '233',       # time zero
                     '-s', 'auto',      # stacking (auto)
                     '-r', '75',        # boxcar noise removal
                     '-t', '65-100',    # vertical triangular FIR filter
                     '-p', '10',        # plot 10 inches wide
                     '-d', dpi,         # dots per inch
                     '-x', 'm',         # x axis units
                     '-z', 'ns',        # z axis units
                     ])


def assemble(projects, p, fn):
    '''
    Assemble file parameters.
    '''
    dztno = '%03d' % fn
    ipath = os.path.join(projects[p]['path'], p, projects[p]['subdir'])
    ifn = glob.glob(ipath + '/*%s.DZT' % (dztno))[0]
    ofn = os.path.join(projects[p]['out'], os.path.basename(ifn))
    return ifn, ofn


def testparams(parampath):
    '''
    Test the project files specified in the params file.
    '''


def write(fstring, append=True):
    '''
    Write the formatted LaTeX string to a file.
    '''
    mode = 'a' if append else 'w'
    with open(texfile, mode) as f:
        f.write('\n' + fstring + '\n')

def texput(string, projects, p, fn, ):
    '''
    Format a LaTeX string.
    '''
    if string == "chapter":
        write(CHAPTER, append=False)
    if string == "section":
        write(SECTION % (projects[p]['date'], projects[p]['location']))
    if string == "figure":
        write(CHAPTER % ())
    if string == "clear":
        write(CLEAR)
    if string == "end":
        write(END)


def run(parampath):
    '''
    Main function.
    '''
    projects = getparams(parampath)
    t = testparams(projects)
    if t.lower() != 'y':
        printM('User specified exit. Exiting.\n', color='yellow')
        return
    nf, np = enum(projects)
    i, ip = 0, 0
    for p in projects:
        ip += 1
        for fn in projects[p]["flist"]:
            printM('project "%s" (%s of %s)' % (p, ip, np), color='blue')
            ifn, ofn = assemble(projects, p, fn)
            process(ifn=ifn, ofn=ofn, gain=projects[p]["gain"])
            i += 1
            printM("%s/%s files processed (project %s of %s)" % (i, nf, ip, np))
        printM('%s/%s projects done (finished with "%s")' % (ip, np, p), color='purple')


if __name__ == "__main__":
    run()