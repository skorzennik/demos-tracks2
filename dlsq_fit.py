#
# dLSQ fit: simple least squares fit to data
#
#   y = fcn(x, c)
#
# uses numpy arrays for all computations, expect numpy arrays a input
# to dlsq_fit
#
# <- Last updated: Sat May  1 16:49:35 2021 -> SGK
#
import math
import numpy as np
#
# ------------------------------------------------------------------------
# function being fitted
def fcn(x, c):
    """
    function fitted y = f(x), using params/coefs c[:]
      this one fits is a straight line 
    """
    y = c[0] + c[1]*x
    return y
#
# ------------------------------------------------------------------------
# fit the data
def fit(x, y, c, eps, niterx):
    """
    fit the data y[:] = fcn(x[:], c[:])
       c[:] can be of any lenght, as needed by fcn()
       eps[:]: precision needed to be reached - same size as c[:]
               coef c[i] is not fitted when eps[i] == 0
       niterx: max no of iteration

       perform a non-linear LSQR fit
       computes numerically the needed derivatives
         d fcn
         -----
         d c
       using relative increments delta[:] = eps[:]/2.
    """
    #
    name = __name__+'.fit():'
    #
    nx    = x.size
    nc    = c.size
    delta = eps/2.
    niter = 0
    #
    idz = np.zeros(nc, dtype = np.int)
    nz  = 0
    for i in range(nc):
        if eps[i] != 0:
            idz[nz] = nz
            nz += 1
    #
    # print(name, nc, 'coefs, fitting ', nz)
    #
    converged = 0
    # loop until converged
    while (converged == 0):
        niter = niter +1
        # reach max iteration?
        if (niter > niterx):
            print(name, 'max no of iterations reached (',niterx,')')
            return -niterx
        #
        b = np.empty(nz)
        a = np.empty((nz,nz))
        #
        # compute error function efz[] = y[]-yfit[]
        yfit = fcn(x, c)
        efz  = y - yfit
        #
        # compute vector B
        dfz  = np.empty((nx, nz))
        for i in range(nz):
            k  = idz[i]
            #  cc[] is c[] perturbed for coef k to compute derivative of fcn() wrt coefs k
            cc = c.copy()
            # if coef is 0, can't perturbe it by multiplying
            if (cc[k] == 0.0):
                cc[k] = delta[k]
            else:
                cc[k] = cc[k]*(1.+delta[k])
            #
            yft2 = fcn(x, cc)
            dck = cc[k]-c[k]
            dfz[:, i] = (yft2[:] - yfit[:])/dck
            # now evaluate b[i]
            b[i] = np.sum(efz[:]*dfz[:, i])
        #
        #print('b ', b)
        #
        # compute diag sq matrix A
        for j in range(nz):
            for i in range(j, nz):
                a[i, j] = np.sum(dfz[:,i] * dfz[:,j])
                if (i != j):
                    a[j,i] = a[i,j]
        #
        #print(' a', a)
        #
        # invert matrix A
        ainv = np.linalg.inv(a)
        dc   = np.dot(ainv, b)
        #
        #  check which coefs have converged: relative change < eps[]
        hasConverged = np.zeros(nz, dtype=np.int)
        for i in range(nz):
            k = idz[i]
            c[k] = c[k] + dc[i]
            if ( np.abs(dc[i]) < eps[k]*np.abs(c[k]) ):
                hasConverged[i] = 1
        #
        # how many have converged?
        nsum = np.sum(hasConverged)
        if (nsum == nz):
            converged = 1
        # stop iterating/loop if all have converged
    ## print(name, 'converged in ', niter,' iteration(s)')
    return niter
#
# ------------------------------------------------------------------------
# execute the fitting
#   nx = max no if iterations allowed
def dlsq_fit(x, y, nx = 1000):
    """
    execute the dLSQR fitting
      set an initial guess for c[:]
      set eps[:]
      run the fitting, up to nx iterations
      return no of iters and coefs c[:]
        neg no of iters if not converged
    """
    # initial guess
    c   = np.array([0.1, -1.0])
    # convergence precision
    eps = np.array([1.0, 1.0])*1E-6
    n   = fit(x, y, c, eps, nx)
    return (n, c)
