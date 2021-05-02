#
# initialize options and parse the arguments
#  initOpts()
#  parseArgs()
# <- Last updated: Sat May  1 17:28:17 2021 -> SGK
#
import sys
#
# ------------------------------------------------------------------------
# initialize all the options to default values
def initOpts(plotType =   '-',    # -|x|w|pdf|png|gmap
             velMin   =   6.0,    # 10.0
             velMax   = 100.0,    # 50.0
             grdMax   =  15.0,    # reject when abs(grade) > grdMax
             cadMin   =  10,      # ignore when cadence < cadMin
             hrMin    =  50,      #        when HR < hrMin
             plotVS   = 'Time',   # 'Distance',
             noRoute  = False,    # don't show route figure
             useTable = False,    # print stats as table
             useRoad  = True,     # False
             plotSize = (12, 8)):
    """
    Initialize the options:
      velMin: velocity minimum for moving (mph)
      velMax: max velocity   - to reject any spurious GPS data
      grdMax: max abs(grade) - to reject any spurious GPS data
      cadMin: cadence minumum to include in stats
      hrMin:  heart rate minimum - to reject spurious values
      plotVS: show plots vs 'Time' or 'Distance'
      noRoute: won't plot route on map if True
      useTable: print stats in a tabular form if True
      useRoad: plot route on map of road (True) or satello=ite (False)
      plotSize: size of the plotting window
    """
    #
    opts = {}
    opts['plotType'] = plotType
    opts['velMin']   =   velMin  
    opts['velMax']   =   velMax  
    opts['grdMax']   =   grdMax  
    opts['cadMin']   =   cadMin  
    opts['hrMin']    =    hrMin   
    opts['plotVS']   =   plotVS      
    opts['noRoute']  =  noRoute
    opts['useRoad']  =  useRoad 
    opts['useTable'] =  useTable
    opts['plotSize'] = plotSize
    #
    return opts
#
# ------------------------------------------------------------------------
# parse the arguments and update the options
# if no args passed, read from stdin
#
def parseArgs(o):
    """
    parse the arguments or read them from stdin
    usage
       python process-tcx.py [opts] filename
    opts: 
      -useTable                format of stats
      -vsTime|-vsDistance      type of plot
      -useSatellite|-useRoad   type of route bgd map
      -noRoute                 no route figure
      -vmin v                  set velMin to v
      -vmax v                  set velMax to v
      -hrmin h                 set hrMin to h
      -cmin                    c set cadMin to c
      -|gmap|-pdf|-png|-x|-w   type of plot (none, gmap, pdf, png, X, or Windows
    or
      python process-tcx.py
    and answer prompts
    """
    #
    nargs = len(sys.argv)
    #
    # no args, read from stdin
    if (nargs == 1):
        a = input('Enter filename? ');
        o['fileName'] = a
        a = input('Type of plot x, w, pdf, or png or - for none?  ');
        if a == 'x'   or a == 'w'   or \
           a == 'pdf' or a == 'png' or \
           a == '-':
            o['plotType'] = a
        else:
            print('Invalid option')
            return 1
        #
        loop = 1
        while (loop == 1):
            a = input('any other option (or CR)?  ')
            if a == '':
                loop = 0
            elif a == 'vsTime':
                o['plotVS'] = 'Time'
            elif a == 'vsDistance':
                o['plotVS'] = 'Distance'
            elif a == 'useSatellite':
                o['useRoad'] = False
            elif a == 'useTable':
                o['useTable'] = True
            elif a == 'useRoad':
                o['useRoad'] = True
            elif a == 'noRoute':
                o['noRoute'] = True
            else:
                print('Invalid, use\n '+\
                      'vsTime vsDistance useTable noRoute useSatellite useRoad')
    #
    # pass the args
    else:
        i = 1       
        loop = 1
        # loop on args
        while (loop == 1):
            a = sys.argv[i]
            if a == '-vsTime':
                o['plotVS'] = 'Time'
            #
            elif a == '-vsDistance':
                o['plotVS'] = 'Distance'
            elif a == '-useSatellite':
                o['useRoad'] = False
            elif a == '-useRoad':
                o['useRoad'] = True
            elif a == '-useTable':
                o['useTable'] = True
            elif a == '-noRoute':
                o['noRoute'] = True
            #
            elif a == '-gmap':
                o['plotType'] = 'gmap'
            elif a == '-x' or a == 'w':
                o['plotType'] = 'x'
            elif a == '-pdf':
                o['plotType'] = 'pdf'
            elif a == '-png':
                o['plotType'] = 'png'
            elif a == '-':
                o['plotType'] = '-'
            #
            elif a == '-vmin':
                i += 1
                o['velMin'] = float(sys.argv[i])
            elif a == '-vmax':
                i += 1
                o['velMax'] = float(sys.argv[i])
            #
            elif a == '-hrmin':
                i += 1
                o['hrMin'] = int(sys.argv[i])
            #
            elif a == '-cmin':
                i += 1
                o['cadMin'] = int(sys.argv[i])
            #
            else:
                #
                # last arg must be the TCX file name
                if i == nargs-1 and a[0] != '-':
                    o['fileName'] = a
                    loop = 0
                else:
                    if a[0] == '-':
                        print('Invalid option','"'+a+'",', 'usage\n' + \
                              ' process-tcx.py [opts] filename\n\n'  + \
                              ' options:\n'                          + \
                              ' [-useTable]'           + \
                              ' [-vsTime|-vsDistance]' + \
                              ' [-useSatellite|-useRoad] [-noRoute]\n'      + \
                              ' [-vmin v] [-vmax v] [-hrmin h] [-cmin c]\n' + \
                              ' [-|gmap|-pdf|-png|-x|-w]')
                    else:
                        print('Invalid or too many arguments')
                    return 1
            #
            # next arg
            i += 1
            #
            # missing file name if ran out of args
            if i == nargs and loop == 1:
                 print('filename missing')
                 return 1
    #
    # normal exit         
    return 0
