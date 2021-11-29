import os, glob
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd

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
    fig, ax = plt.subplots(ncols=2, figsize=(10,5), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    return fig, ax


def init_overview(ax, res):
    '''
    Make overview map.
    '''
    m = Basemap(llcrnrlon=OBD['ll_lon'], llcrnrlat=OBD['ll_lat'],
                urcrnrlon=OBD["ur_lon"], urcrnrlat=OBD["ur_lat"],
                lat_0=OBD['cn_lat'], lon_0=OBD['cn_lon'],
                projection='merc', resolution=res, ax=ax)
    m.drawmapboundary(fill_color='none')
    m.drawstates(zorder=1, linewidth=0.5)
    m.drawcountries(zorder=1, linewidth=0.75)
    m.drawparallels(np.arange(int(OBD['ll_lat']),int(OBD["ur_lat"]+1),1),labels=[1,0,0,0], linewidth=0.0)
    m.drawmeridians(np.arange(int(OBD['ll_lon']-1),int(OBD["ur_lon"]),1),labels=[0,0,0,1], linewidth=0.0)
    return m


def init_detail(ax, region=[], res=1000, service='World_Imagery', # also 'World_Topo_Map'
                epsg=4326,resolution='h',projection='mill'):
    '''
    Make detail map.
    '''
    m = Basemap(projection=projection, epsg=epsg,
                resolution=resolution,
                llcrnrlon=region['ll_lon'], llcrnrlat=region['ll_lat'],
                urcrnrlon=region['ur_lon'], urcrnrlat=region['ur_lat'],
                lat_0=region['cn_lat'], lon_0=region['cn_lon'],)
    m.arcgisimage(server='http://server.arcgisonline.com/ArcGIS', service=service,
                  xpixels=res, verbose=True)
    return m


def linedata(fn):
    lines = {}
    i = 0
    for dzg_csv in glob.glob(fn + '*-gps.csv'):
        df = pd.read_csv(dzg_csv)
        if i == 0:
            bigdf = df.copy()
        else:
            bigdf.append(df)
        lats = df['latitude'].tolist()
        lons = df['longitude'].tolist()
        short_name = os.path.basename(dzg_csv).split('-gps')[0]
        lines[short_name] = {"lats":lats, "lons":lons}
        i += 1
    return lines


def get_lines(ifn, all=True):
    bigdf = pd.DataFrame()
    iname = os.path.splitext(ifn) # filename
    gname = os.path.dirname(ifn)  # glob-friendly name (all csvs)

    line, bigdf = linedata(iname)
    lines, bigdf = linedata(gname)

    dbd = {}
    dbd['ll_lat'] = bigdf.latitude.min()
    dbd['ll_lon'] = bigdf.longitude.max()
    dbd['ur_lat'] = bigdf.latitude.max()
    dbd['ur_lon'] = bigdf.longitude.min()
    dbd['cn_lat'] = (dbd['ll_lat'] + dbd['ur_lat']) / 2.
    dbd['cn_lon'] = (dbd['ll_lon'] + dbd['ur_lon']) / 2.

    return lines, line, dbd


def plot_lines(lines, m, color='k'):
    for line in lines:
        x, y = m(line['lons'], line['lats'])
        m.plot(x, y, linewidth=1.5, color=color)


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

    fig, ax = initfig()
    m0 = init_overview(ax[0])

    lines, extents = get_lines(ifn)
    line = get_lines(ifn, all=False)
    m1 = init_detail(ax[1], region=extents)
    plot_lines(lines, m1, color='silver')
    plot_lines(line, m1, color='firebrick')

    plt.savefig(os.path.join(figdir, figname))

    return mfn
