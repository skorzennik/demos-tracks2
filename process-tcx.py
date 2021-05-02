#!/usr/bin/env python
#
# plot ride properties and overplot route on a map,
#   put them in a two separate figure
#   handle missing cadence and missing HR 
#   gmap: get apikey from $APIKEY
#
# <- Last updated: Sat May  1 20:39:24 2021 -> SGK
#
# this allows matplotlib to plot to file when there is no display 
import os, matplotlib
if (os.environ.get('DISPLAY','') == '') and (os.environ.get('OS') != 'Windows_NT'):
    matplotlib.use('PDF')
#
# load needed functions from other .py files
from argslib   import initOpts, parseArgs
from tracklib  import readTrack, processTrack
from mkgmap    import mkGMap
from plottrack import doPlot
#
# ------------------------------------------------------------------------
#
if __name__ == '__main__':
    #
    # check that we're running v3.7 or later
    import sys
    MIN_PYTHON = (3, 7)
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required." % MIN_PYTHON)
    #
    # initialize the options
    opts = initOpts()
    #
    # parse the args and update the options
    err = parseArgs(opts)
    if err:
        exit()
    #
    # read the TCX file and store it in a pandas data frame
    trackDF = readTrack(opts['fileName'])
    #
    # process the track, returns a numpy data array
    # and infos (which col is what) and stats 
    (data, infos, stats) = processTrack(trackDF,
                                        useTable = opts['useTable'],
                                        velMin   = opts['velMin'],
                                        velMax   = opts['velMax'],
                                        grdMax   = opts['grdMax'],
                                        cadMin   = opts['cadMin'],
                                        hrMin    = opts['hrMin'] )
    #
    # overlay on a Google map
    if (opts['plotType'] == 'gmap'):
        mkGMap(data, infos, stats, velMin = opts['velMin'])
    #
    # or generate plots
    elif (opts['plotType'] != '-'):
        doPlot(data, infos, stats,
               plotType = opts['plotType'],
               useRoad = opts['useRoad'],   noRoute = opts['noRoute'],
               plotSize = opts['plotSize'], plotVS  = opts['plotVS'],
               velMin   = opts['velMin'],   velMax  = opts['velMax'],
               cadMin   = opts['cadMin'])
