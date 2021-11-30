import os, glob
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from numpy.core.fromnumeric import size
import pandas as pd
import math
from urllib.error import HTTPError
from . import printM

OBD = {     # overview map boundaries (centered on Maine state lines)
    "ll_lon": -71.249710,
    "ll_lat": 42.982858,
    "ur_lon": -66.7,
    "ur_lat": 47.5,
    "cn_lat": -69,
    "cn_lon": 45.5,
}

def initfig():
    '''
    Return the figure and axes instances.
    '''
    fig, ax = plt.subplots(ncols=2, figsize=(10,5.6), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    return fig, ax


def init_overview(ax, resolution='h', res=1000, service='World_Shaded_Relief',
                  epsg=3857, projection='merc'):
    '''
    Make overview map.
    '''
    m0 = Basemap(projection=projection, epsg=epsg,
                resolution=resolution, ax=ax,
                llcrnrlon=OBD['ll_lon'], llcrnrlat=OBD['ll_lat'],
                urcrnrlon=OBD['ur_lon'], urcrnrlat=OBD['ur_lat'],
                lat_0=OBD['cn_lat'], lon_0=OBD['cn_lon'])
    m0.drawmapboundary(fill_color='none')
    m0.drawstates(zorder=1, linewidth=0.5)
    m0.drawcountries(zorder=1, linewidth=0.75)
    m0.drawparallels(np.arange(int(OBD['ll_lat']),int(OBD['ur_lat']+1),1),labels=[1,0,0,0], linewidth=0.0)
    m0.drawmeridians(np.arange(int(OBD['ll_lon']),int(OBD['ur_lon']),1),labels=[0,0,0,1], linewidth=0.0)
    try:
        m0.arcgisimage(service=service, xpixels=res, verbose=True)
    except HTTPError as e:
        printM('HTTP Error:\n%s' % e, color='red')
        m0.fillcontinents(zorder=0)

    return m0


def init_detail(ax, region=[], res=1000, service='World_Imagery', # also 'World_Topo_Map'
                epsg=4326, resolution='h', projection='merc'):
    '''
    Make detail map.
    '''
    m1 = Basemap(projection=projection, epsg=epsg,
                resolution=resolution, ax=ax,
                llcrnrlon=region['ll_lon'], llcrnrlat=region['ll_lat'],
                urcrnrlon=region['ur_lon'], urcrnrlat=region['ur_lat'],
                lat_0=region['cn_lat'], lon_0=region['cn_lon'],)
    try:
        m1.arcgisimage(service=service, xpixels=res, verbose=True)
    except HTTPError as e:
        printM('HTTP Error:\n%s' % e, color='red')
    return m1


def linedata(fn):
    lines = {}
    bigdf = pd.DataFrame()
    printM('Searching for location file(s) %s*-gps.csv' % (fn), color='blue')
    for dzg_csv in glob.glob(fn + '*-gps.csv'):
        df = pd.read_csv(dzg_csv)
        bigdf = bigdf.append(df)
        lats = df['latitude'].values
        lons = df['longitude'].values
        short_name = os.path.basename(dzg_csv).split('-gps')[0]
        lines[short_name] = {"lats":lats, "lons":lons}
    return lines, bigdf


def get_lines(ifn):
    bigdf = pd.DataFrame()
    iname = os.path.splitext(ifn)[0] # filename
    gname = os.path.dirname(ifn)     # glob-friendly name (all csvs)

    line, smalldf = linedata(iname)
    lines, bigdf = linedata(gname + '/') # need to add slash to make glob

    dbd = {}
    dbd['cn_lat'] = (bigdf.latitude.min() + bigdf.latitude.max()) / 2.
    dbd['cn_lon'] = (bigdf.longitude.min() + bigdf.longitude.max()) / 2.
    dbd['ll_lat'] = bigdf.latitude.min() - 0.002    # latitude-specific! hacky
    dbd['ll_lon'] = bigdf.longitude.min() - 0.012   # latitude-specific! hacky
    dbd['ur_lat'] = bigdf.latitude.max() + 0.002    # latitude-specific! hacky
    dbd['ur_lon'] = bigdf.longitude.max() + 0.012   # latitude-specific! hacky

    return lines, line, dbd


def add_arrow(line, position=None, direction='right', size=15, color=None):
    """
    add an arrow to a line.

    line:       Line2D object
    position:   x-position of the arrow. If None, mean of xdata is taken
    direction:  'left' or 'right'
    size:       size of the arrow in fontsize points
    color:      if None, line color is taken.
    """
    if color is None:
        color = line.get_color()

    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if position is None:
        position = xdata.mean()
    # find closest index
    start_ind = np.argmin(np.absolute(xdata - position))
    if direction == 'right':
        end_ind = start_ind + 1
    else:
        end_ind = start_ind - 1

    line.axes.annotate('',
        xytext=(xdata[start_ind], ydata[start_ind]),
        xy=(xdata[end_ind], ydata[end_ind]),
        arrowprops=dict(arrowstyle="->", color=color),
        size=size
    )


def plot_mark(extents, m):
    x, y = m(extents['cn_lon'], extents['cn_lat'])
    m.plot(x, y, 'ro')


def plot_lines(lines, m, color='k'):
    for line in lines:
        x, y = m(lines[line]['lons'], lines[line]['lats'])
        l = m.plot(x, y, color=color)[0]
        if color == 'firebrick':
            # the highlighted line
            add_arrow(line=l, size=20)


def drawmap(ifn, ffn, out, projects, p):
    '''
    Draw map using matplotlib/Basemap.
    '''
    figdir = os.path.join(out['dir'], out['figdir'])
    figname = '%s-map.png' % (ffn)
    mfn = os.path.join(out['figdir'], figname)
    lines, line, extents = get_lines(ifn)

    fig, ax = initfig()
    m0 = init_overview(ax[0], service='World_Shaded_Relief',
                       epsg=3857, projection='lcc')
    plot_mark(extents=extents, m=m0)

    m1 = init_detail(ax[1], region=extents,
                     epsg=5070, projection='aea')
    plot_lines(lines, m1, color='silver')
    plot_lines(line, m1, color='firebrick') # the hightlighted line

    figpath = os.path.join(figdir, figname)
    printM('Saving figure as %s' % figpath, color='blue')
    plt.tight_layout()
    plt.savefig(figpath)

    return mfn
