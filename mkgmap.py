#
# simple routine using gmplot to create an html to overplot on google map
#   mkGMap()
# <- Last updated: Sat May  1 16:51:29 2021 -> SGK
#
import os
import numpy as np
import gmplot
from utilslib import formatTime
#
# ------------------------------------------------------------------------
# create an html to overplot on google map, using gmplot
def mkGMap(data, infos, stats,
           color = 'red', velMin = 6.0):
    """
    create an hmlt file to overplot route on a Google Map
      using gmplot module
    """
    #
    # decode infos -> index[] and units[]
    nCols, nLines = data.shape
    index = {}
    units = {}
    i = 0
    for wx in infos.split():
        w = wx.split(':')
        index[w[0]] = i
        units[w[0]] = w[1]
        i += 1
    #
    # lon index -> values
    ix = index['Longitude']
    mLon = np.isfinite(data[ix, :])
    lonList = data[ix, mLon]
    #
    # lat index -> values
    ix = index['Latitude']
    mLat = np.isfinite(data[ix, :])
    latList = data[ix, mLat]
    #
    # get center and borders
    latCntr = sum(latList)/sum(mLat)
    lonCntr = sum(lonList)/sum(mLon)
    #
    (north, south) = (max(latList),  min(latList))
    (east,  west)  = (max(lonList),  min(lonList))
    #
    # widens and shift east by 20%
    dlon = (east-west)*.2
    east -= dlon*2
    # west -= dlon-dlon
    #
    # map bounding box
    bb = {'north': north, 'south': south,
          'east':  east,  'west':  west}
    mapStyle = [ {'featureType': 'all', 'stylers': [
        {'saturation': -80},
        {'lightness': 30}, ] } ]
    # 
    zoom = 12
    gmap = gmplot.GoogleMapPlotter(latCntr, lonCntr, zoom,
                                   map_style = mapStyle,
                                   fit_bounds = bb)
    #
    # API KEY from $APIKEY
    apiKey = os.environ.get('APIKEY','none')
    if (apiKey != 'none'):
        gmap.apikey = apiKey
    else:
        print('no APIKEY found, will show a "For development purpose only" watermark')
    #
    # put markers at beg/end
    gmap.scatter( latList[0:1], lonList[0:1], '#00FF00',
                  size = 10, marker = True )
    gmap.scatter( latList[-2:-1], lonList[-2:-1], '#FF0000',
                  size = 10, marker = True )
    # draw the route
    gmap.plot(latList, lonList, 'cornflowerblue', edge_width = 2.5)
    #
    # add some text
    fmtStr = 'Started {}\n' + \
        'Time total:{}, moving:{}, paused:{}\n' + \
        'Distance traveled total:{:.1f}, moving:{:.1f} mi\n' + \
        'Minimun moving velocity {:.1f} mph'
    str = fmtStr.format(stats['startTime'],
                        formatTime(stats['totalTime']),
                        formatTime(stats['movingTime']),
                        formatTime(stats['totalTime']- stats['movingTime']),
                        stats['distance'],  stats['mvgDistance'], velMin)
    #
    fmtStr = '\nVelocity average:{:6.2f} max:{:6.2f} mph\n' + \
        'Cadence average:{:6.2f} max:{:6.2f} rpm\n' + \
        'HR average:{:6.2f} max:{:6.2f} bpm'
    str += fmtStr.format(stats['avgMVel'],      stats['maxMVel'],
                         stats['avgCadence'],   stats['maxCadence'],
                         stats['avgHeartRate'], stats['maxHeartRate'])
    #
    # location of text
    lat = max(latList)
    lon = max(lonList)+0.075
    #
    # must write one string at a time, \n not allowed
    for s in str.split('\n'):
        #
        # the text is center justify, this is a hack to approx left justify
        lx = len(s)*.0019
        gmap.text(lat, lon, s, color = color)
        # move down
        lat -= .009
    #
    # Pass the file path of the html
    gmap.draw( "gmap.html" )
    #
    print('Load \'gmap.html\' in a browser, ' + \
          'map is centered on {:.4f},{:.4f}'.format(latCntr, lonCntr))
