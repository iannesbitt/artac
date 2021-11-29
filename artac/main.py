import os, sys, glob
import subprocess
import json
from .texstrings import CHAPTER, PCAPTION, MCAPTION, SECTION, SUBSECTION, FIGURE, CLEAR, END
from .mapping import drawmap
import getopt

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
    ifn = glob.glob(ipath + '/*%s.DZT' % (dztno))
    if len(ifn) > 0:
        ifn = ifn[0]
    else:
        printM('File not found: %s' % (os.path.join(ipath, '/*%s.DZT' % (dztno))), color='red')
        return False, False
    ofn = os.path.join(projects[p]['out'], projects[p]['outsubdir'], os.path.basename(ifn))
    return ifn, ofn


def testparams(projects, outparams):
    '''
    Test the project files specified in the params file.
    '''
    ip, ipp = 0, 0
    ipf = 0
    for p in projects:
        for fn in projects[p]['flist']:
            ifn, ofn = assemble(projects, p, fn)
            if ifn:
                # if this file exists, increment the number of files found
                ipf += 1
                if ip == ipp:
                    # increment the number of projects if it hasn't been done
                    printM('Found project %s' % (p))
                    ip += 1
                printM(ifn, color='blue')
        # reset project counter
        ipp = ip
    
    print('Number of projects with found files: %s' % (ip))
    print('Number of files found: %s' % (ipf))
    print('LaTeX output dir: %s' % (outparams['dir']))
    print('LaTeX output file: %s' % (os.path.join(outparams['dir'], outparams['texfile'])))
    print('Figure output dir: %s' % (os.path.join(outparams['dir'], outparams['figdir'])))
    print()
    return input('Do you wish to proceed? (y/N)')


def write(out, st, append=True):
    '''
    Write the formatted LaTeX string to a file.
    '''
    mode = 'a' if append else 'w'
    with open(out, mode) as f:
        f.write(st)


def texput(part, out, projects=None, p=None, fn=None, mfn=None):
    '''
    Format a LaTeX string and send it to write to a file.
    '''
    out = os.path.join(out['dir'], out['texfile'])

    if part == "chapter":
        write(out, st=CHAPTER.substitute(), append=False)
    if part == "section":
        write(out, st=SECTION.substitute(date=projects[p]['date'],
                                         location=projects[p]['location']))
    if part == "subsection":
        write(out, st=SUBSECTION.substitute(fn=fn))
    if part == "profile":
        pfn = glob.glob('%s/%s*.png' % (out['outsubdir'], fn))[0]
        caption = PCAPTION.substitute(fn=fn,
                                      date=projects[p]['date'],
                                      location=projects[p]['location'])
        write(out, st=FIGURE.substitute(fn=fn, pfn=pfn, caption=caption))
    if part == "map":
        caption = MCAPTION.substitute(fn=fn,
                                      date=projects[p]['date'],
                                      location=projects[p]['location'])
        write(out, st=FIGURE.substitute(fn=fn, pfn=mfn, caption=caption))
    if part == "clear":
        write(out, st=CLEAR.substitute())
    if part == "end":
        write(out, st=END.substitute())


def starttex(outparams):
    '''
    Start LaTeX output.
    '''
    texput('chapter', outparams)


def run(parampath):
    '''
    Main function.
    '''
    params = getparams(parampath)
    projects = params['inparams']
    outparams = params['outparams']
    t = testparams(projects, outparams)
    if t.lower() != 'y':
        printM('User specified exit. Exiting.\n', color='yellow')
        return

    starttex(outparams=outparams)

    nf, np = enum(projects)
    i, ip = 0, 0
    for p in projects:
        texput('section', out=outparams, projects=projects, p=p)
        ip += 1
        for fn in projects[p]["flist"]:
            printM('project "%s" (%s of %s)' % (p, ip, np), color='blue')

            # process file
            ifn, ofn = assemble(projects, p, fn)
            process(ifn=ifn, ofn=ofn, gain=projects[p]["gain"])
            ffn = os.path.splitext(os.path.basename(ofn))
            mfn = drawmap(ifn=ifn, ffn=ffn, out=outparams, projects=projects, p=p)

            # write subsection title, profile, and map figure sections
            texput('subsection', out=outparams, fn=ffn, projects=projects, p=p)
            texput('profile', out=outparams, fn=ffn, projects=projects, p=p)
            texput('map', out=outparams, fn=fn, mfn=mfn, projects=projects, p=p)

            i += 1
            printM("%s/%s files processed (project %s of %s)" % (i, nf, ip, np))

        texput('clear', out=outparams)
        printM('%s/%s projects done (finished with "%s")' % (ip, np, p), color='purple')
    
    texput('end', out=outparams)


def sayparamerror():
    '''
    Repeatable printed text informing the user about the params file.
    '''
    param_url = 'https://github.com/iannesbitt/artac/blob/master/artac/params.json'
    printM('Please specify a parameters json file as the only argument.', color='red')
    printM('For an example please see %s' % (param_url), color='red')


def start():
    '''
    Get parampath from opts and send it to run().
    '''
    try:
        f = sys.argv[1]
    except IndexError:
        printM('No argument specified.', color='red')
        sayparamerror()
    if os.path.exists(f):
        # run the program
        run(f)
    else:
        printM('No parameters file found.', color='red')
        sayparamerror()


if __name__ == "__main__":
    start()
