import os, sys, glob
import subprocess
import json
from .texstrings import CHAPTER, PCAPTION, MCAPTION, SECTION, SUBSECTION, FIGURE, CLEAR, END
from .mapping import drawmap
from . import printM
from readgssi.readgssi import readgssi


def getparams(parampath):
    '''
    Load the projects and files in the parameters file.
    '''
    with open(parampath, 'r') as paramfile:
        return json.load(paramfile)


def process(ifn, ofn, gain, dpi=150, method='subprocess'):
    '''
    Call the process with the desired flags.
    Flags are detailed here:
    https://readgssi.readthedocs.io/en/latest/general.html#bash-usage
    '''
    if method == 'subprocess':
        subprocess.call(['readgssi',
                         '-i', '%s' % ifn,  # input file
                         '-g', '%s' % gain, # gain
                         '-o', '%s' % ofn,  # output file
                         '-T',              # plot title off
                         '-n',              # don't show plot window
                         '-N',              # distance normalization
                         '-Z', '233',       # time zero
                         '-s', 'auto',      # stacking (auto)
                         '-r', '75',        # boxcar noise removal
                         '-t', '65-100',    # vertical triangular FIR filter
                         '-p', '10',        # plot 10 inches wide
                         '-d', '%s' % dpi,  # dots per inch
                         '-x', 'm',         # x axis units
                         '-z', 'ns',        # z axis units
                         ])
    else:
        readgssi(infile=ifn, outfile=ofn, gain=gain, dpi=dpi,
                 plotting=True, figsize=10, title=False,
                 stack='auto', x='m', z='ns', zero=[233,0,0,0],
                 noshow=True, normalize=True, bgr=True, win=75,
                 freqmax=100, freqmin=65, verbose=False, frmt='png')


def assemble(projects, p, fn, outparams):
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
    ofn = os.path.join(outparams['dir'], outparams['figdir'], os.path.basename(ifn))
    return ifn, ofn


def testparams(projects, outparams):
    '''
    Test the project files specified in the params file.
    '''
    ip, ipp = 0, 0
    ipf = 0
    for p in projects:
        printM('Looking for project %s in base path' % (p), color='bold')
        printM(os.path.join(projects[p]['path'], p, projects[p]['subdir']), color='bold')
        for fn in projects[p]['flist']:
            ifn, ofn = assemble(projects, p, fn, outparams)
            if ifn:
                # if this file exists, increment the number of files found
                ipf += 1
                if ip == ipp:
                    # increment the number of projects if it hasn't been done
                    printM('Found project %s' % (p))
                    ip += 1
                printM(ifn, color='blue')
            else:
                del projects[p]['flist'][fn]
        # reset project counter
        if ip == ipp:
            printM('Could not find project %s' % (p), color='red')
            del projects[p]
        else:
            ipp = ip
    
    print('Number of projects with found files: %s' % (ip))
    print('Number of files found: %s' % (ipf))
    print('LaTeX output dir: %s' % (outparams['dir']))
    print('LaTeX output file: %s' % (os.path.join(outparams['dir'], outparams['texfile'])))
    print('Figure output dir: %s' % (os.path.join(outparams['dir'], outparams['figdir'])))
    print()
    chal = input('Do you wish to proceed? (y/N) ')
    # returns the challenge answer, num projects, and num files
    return chal, ip, ipf, projects


def write(texf, st, append=True):
    '''
    Write the formatted LaTeX string to a file.
    '''
    mode = 'a' if append else 'w'
    with open(texf, mode) as f:
        f.write(st)


def texput(part, out, projects=None, p=None, fn=None, mfn=None):
    '''
    Format a LaTeX string and send it to write to a file.
    '''
    texf=texf = os.path.join(out['dir'], out['texfile'])

    if part == "chapter":
        write(texf=texf, st=CHAPTER.substitute(), append=False)
    if part == "section":
        write(texf=texf, st=SECTION.substitute(date=projects[p]['date'],
                                         location=projects[p]['location']))
    if part == "subsection":
        write(texf=texf, st=SUBSECTION.substitute(fn=fn))
    if part == "profile":
        pfn = '%s/%s*.png' % (out['figdir'], fn)
        caption = PCAPTION.substitute(fn=fn,
                                      date=projects[p]['date'],
                                      location=projects[p]['location'])
        write(texf=texf, st=FIGURE.substitute(fn=fn, pfn=pfn, caption=caption))
    if part == "map":
        caption = MCAPTION.substitute(fn=fn,
                                      date=projects[p]['date'],
                                      location=projects[p]['location'])
        write(texf=texf, st=FIGURE.substitute(fn=fn, pfn=mfn, caption=caption))
    if part == "clear":
        write(texf=texf, st=CLEAR.substitute())
    if part == "end":
        write(texf=texf, st=END.substitute())


def starttex(outparams):
    '''
    Start LaTeX output.
    '''
    texput('chapter', outparams)


def note_err(ifn, outparams, err):
    '''
    Note error in errors.txt.
    '''
    mode = 'a' if err > 0 else 'w'
    errf = os.path.join(outparams['dir'], outparams['figdir'], 'errors.txt')
    with open(errf, mode) as errfile:
        errfile.write(ifn + '\n')


def run(parampath):
    '''
    Main function.
    '''
    params = getparams(parampath)
    projects = params['inparams']
    outparams = params['outparams']
    chal, np, nf, projects = testparams(projects, outparams)
    if chal.lower() != 'y':
        printM('User specified exit. Exiting.\n', color='yellow')
        return

    starttex(outparams=outparams)

    i, ip, err, dzgerr = 0, 0, 0, 0
    errf = os.path.join(outparams['dir'], outparams['figdir'], 'errors.txt')
    for p in projects:
        texput('section', out=outparams, projects=projects, p=p)
        ip += 1
        for fn in projects[p]["flist"]:
            printM('project "%s" (%s of %s)' % (p, ip, np), color='blue')

            # process file
            ifn, ofn = assemble(projects, p, fn, outparams)
            try:
                printM('Processing %s with readgssi...' % (os.path.join(p,
                                                            projects[p]['subdir'],
                                                            os.path.basename(ifn))),
                                                            color='blue')
                process(ifn=ifn, ofn=ofn, gain=projects[p]["gain"],
                        dpi=outparams['dpi'], method='function')
            except UnicodeDecodeError as e:
                printM('%s from readgssi:\n%s' % (type(e).__name__, e), color='red')
                printM('(this probably occurred due to garbled bytes at the beginning of the DZG file)', color='red')
                printM('DZG file will be noted in %s/errors.txt' % (outparams['figdir']), color='red')
                dzg = os.path.splitext(ifn)[0] + '.DZG'
                printM(dzg, color='red')
                note_err(dzg, outparams, err)
                dzgerr += 1
                err += 1
            except Exception as e:
                printM('%s from readgssi:\n%s' % (type(e).__name__, e), color='red')
                printM('DZT file will be noted in %s/errors.txt' % (outparams['figdir']), color='red')
                printM(ifn, color='red')
                note_err(ifn, outparams, err)
                err += 1
            ffn = os.path.splitext(os.path.basename(ofn))[0]
            printM('Drawing map for %s' % (ifn), color='blue')
            mfn = drawmap(ifn=ifn, ffn=ffn, out=outparams, projects=projects, p=p)

            # write subsection title, profile, and map figure sections
            printM('Writing tex subsection and figure environments...', color='blue')
            texput('subsection', out=outparams, fn=ffn, projects=projects, p=p)
            texput('profile', out=outparams, fn=ffn, projects=projects, p=p)
            texput('map', out=outparams, fn=ffn, mfn=mfn, projects=projects, p=p)

            i += 1
            printM("%s/%s files processed (project %s of %s)" % (i, nf, ip, np))

        texput('clear', out=outparams)
        printM('%s/%s projects done (finished with "%s")' % (ip, np, p), color='purple')
    
    texput('end', out=outparams)
    if err > 0:
        printM('Errors on %s/%s files (%s due to DZG errors).' % (err, nf, dzgerr), color='red')
        printM('Errored files are noted in %s' % (errf), color='red')
    printM('Done processing %s files.' % (nf))



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
