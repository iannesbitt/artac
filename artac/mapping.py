import os, glob
import matplotlib.pyplot as plt


def drawmap(ifn, ffn, out, projects, p):
    '''
    Draw map using matplotlib/Basemap.
    '''
    figdir = os.path.join(out['dir'], out['figdir'])
    figname = '%s.png' % (ffn)
    mfn = os.path.join(out['figdir'], figname)
    datadir = os.path.join(projects[p]['path'],
                           p,
                           projects[p]['subdir'])
    dzg = glob.glob('%s/%s*.DZG' % (datadir, ffn))[0]
    dzgs = glob.glob('%s/*.DZG' % (datadir))

    return mfn
