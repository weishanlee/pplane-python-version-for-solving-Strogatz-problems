# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 2023

@author: Wei Shan Lee
weishan_lee@yahoo.com

python codes mimicking pplane to plot phase portrait for solving Strogatz's problems.

Reference:
https://scicomp.stackexchange.com/questions/40239/is-there-a-python-version-of-the-ode-tool-pplane
https://scipy-user.scipy.narkive.com/RU19ShQ4/nullclines-for-nonlinear-odes
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html
https://stackoverflow.com/questions/43150872/number-of-arrowheads-on-matplotlib-streamplot
Strogatz, Nonlinear Dynamics and Chaos, 2nd Ed.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy.optimize import fsolve
from numpy import linalg as LA
from matplotlib.markers import MarkerStyle
import sys

# Grid of x, y points
nx, ny = 50, 50
minX, maxX = -5, 5
minY, maxY = -5, 5

# Plot nullclines or not?
plotNullclines = True

# Find fixed Points?
findFixedPoints = True

# Plot multiples of pi in x and y axes?
mulPiXAxis = True
mulPiYAxis = False

def eqnXDotYDot(x, y): 
    """
    Modify equations here
    For polar systems (rDot,thetaDot), convert it to np.array([xDot, yDot]) by
    xDot = rDot * x / sqrt(x**2+y**2) - thetaDot * y 
    yDot = rDot * y / sqrt(x**2+y**2) - thetaDot * x
    """
    #r = np.sqrt(x**2+y**2)
    dx = x + np.exp(-y)
    dy = -y
    return  np.array([dx,dy])

def func(variables):
    x, y = variables
    dx, dy = eqnXDotYDot(x, y)
    return np.array([dx,dy])
    
def fixedPoints(X, Y):
    fPt = ()
    for i in range(nx):
        for j in range(ny):
            xFixedPoint, yFixedPoint = fsolve(func,(X[i,j],Y[i,j]))
            if all(np.isclose(eqnXDotYDot(xFixedPoint, yFixedPoint), [0.0, 0.0])) == True:
               xFixedPoint = round(xFixedPoint,3)
               yFixedPoint = round(yFixedPoint,3)
               fPt += ((xFixedPoint, yFixedPoint),)
    fPt = tuple( set(fPt) )
    return fPt


def jacobian(fs, xs, h=1e-8):
    """
    Reference: Gezerlis, Numerical Methods in Phyisics with Python, p.284
    """
    n = xs.size
    iden = np.identity(n)
    Jf = np.zeros((n,n))
    fs0 = fs(xs)
    for j in range(n):  # through columns to allow for vector addition
        fs1 = fs(xs+iden[:,j]*h)
        Jf[:,j] = ( fs1 - fs0 )/h
    return Jf

# find stability of a single fixed point
def sFPt(fPt):
    tolerance = 1e-8
    fPtX = fPt[0]
    fPtY = fPt[1]
    w= LA.eigvals( jacobian( func,np.array([fPtX,fPtY]) ) )
    tau = w[0] + w[1]
    Delta = w[0] * w[1]
    print("tau = {}".format(tau))
    print("Delta = {}".format(Delta))
    if abs(tau)<tolerance and Delta>0:
       print("({:.3f},{:.3f}): center, linearization could fail.".format(fPtX,fPtY)) 
       typeStability = "BC" # borderline case       
    elif abs(Delta)<tolerance:
       print("({:.3f},{:.3f}): line of fixed points, linearization could fail.".format(fPtX,fPtY))  
       typeStability = "BC" # borderline case        
    elif tau>0 and Delta>0 and (tau**2-4*Delta)<tolerance:
       if w[0]!=w[1]:
          print("({:.3f},{:.3f}): unstable star nodes.".format(fPtX,fPtY))
          typeStability = "unstable"  
       if abs(w[0]-w[1])<tolerance:
          print("({:.3f},{:.3f}): unstable degenerate nodes.".format(fPtX,fPtY))
          typeStability = "unstable" 
    elif tau<0 and Delta>0 and (tau**2-4*Delta)<tolerance:
       if w[0]!=w[1]:
          print("({:.3f},{:.3f}): stable star nodes.".format(fPtX,fPtY))
          typeStability = "stable"  
       if abs(w[0]-w[1])<tolerance:
          print("({:.3f},{:.3f}): stable degenerate nodes.".format(fPtX,fPtY))     
          typeStability = "stable"
    elif tau>0 and Delta>0 and (tau**2-4*Delta>0):
        print("({:.3f},{:.3f}): unstable nodes".format(fPtX,fPtY))
        typeStability = "unstable"
    elif tau>0 and Delta>0 and (tau**2-4*Delta<0):
        print("({:.3f},{:.3f}): unstable spiral".format(fPtX,fPtY))
        typeStability = "unstable" 
    elif tau<0 and Delta>0 and (tau**2-4*Delta>0):
        print("({:.3f},{:.3f}): stable nodes".format(fPtX,fPtY))
        typeStability = "stable"
    elif tau<0 and Delta>0 and (tau**2-4*Delta<0):
        print("({:.3f},{:.3f}): stable spiral".format(fPtX,fPtY))
        typeStability = "stable"                
    elif Delta<0:
        print("({:.3f},{:.3f}): saddle".format(fPtX,fPtY))
        typeStability = "saddle"
    else:
        print("({:.3f},{:.3f}): other cases. Check line 120".format(fPtX,fPtY))
        typeStability = "None"
        sys.exit()
    return typeStability

# function to plot multiples of pi in x axis
# source:
# https://stackoverflow.com/questions/40642061/how-to-set-axis-ticks-in-multiples-of-pi-python-matplotlib
def multiple_formatter(denominator=2, number=np.pi, latex='\pi'):
    def gcd(a, b):
        while b:
            a, b = b, a%b
        return a
    def _multiple_formatter(x, pos):
        den = denominator
        num = np.int(np.rint(den*x/number))
        com = gcd(num,den)
        (num,den) = (int(num/com),int(den/com))
        if den==1:
            if num==0:
                return r'$0$'
            if num==1:
                return r'$%s$'%latex
            elif num==-1:
                return r'$-%s$'%latex
            else:
                return r'$%s%s$'%(num,latex)
        else:
            if num==1:
                return r'$\frac{%s}{%s}$'%(latex,den)
            elif num==-1:
                return r'$\frac{-%s}{%s}$'%(latex,den)
            else:
                return r'$\frac{%s%s}{%s}$'%(num,latex,den)
    return _multiple_formatter
    
x = np.linspace(minX, maxX, nx)
y = np.linspace(minY, maxY, ny)
X, Y = np.meshgrid(x, y)    

# field vector
dx, dy = eqnXDotYDot(X,Y)
# plot phase portrait with vector field
plt.figure()
plt.title("Phase Portrait")
ax = plt.gca()
#fig, ax = plt.subplots()
plt.minorticks_on()
minorLocatorX = AutoMinorLocator(3) # number of minor intervals per major # inteval
minorLocatorY = AutoMinorLocator(2)
ax.xaxis.set_minor_locator(minorLocatorX) # add minor ticks on x axis
ax.yaxis.set_minor_locator(minorLocatorY) # add minor ticks on y axis

speed = np.sqrt(dx**2 + dy**2) # the coefficient may need to modify for 
                                 # different cases
lw = 5 * speed  / speed.max()

ax.streamplot(X, Y, dx, dy, linewidth=1, density=1,color='b', arrowstyle='->')#,
              #broken_streamlines=False) # valid for matplolib version  > 3.6.0

if plotNullclines:
   cs = ax.contour(X,Y,dx,levels=[0], linewidths=1, colors='r')
   ax.clabel(cs,cs.levels,fmt=r'$\dot{x}=0$',font=32)
   
   cs = ax.contour(X,Y,dy,levels=[0], linewidths=1, colors='k')
   ax.clabel(cs,cs.levels,fmt=r'$\dot{y}=0$',font=32)
   
   #ax.legend()

if findFixedPoints:
    fPt = fixedPoints(X, Y)

    for i in range(len(fPt)):
        typeStability = sFPt(fPt[i])
        if typeStability == "stable":
            ax.scatter(fPt[i][0],fPt[i][1],s = 80, facecolors='k',edgecolors='k')
        elif typeStability == "unstable":
            ax.scatter(fPt[i][0],fPt[i][1],s = 80, facecolors='none',edgecolors='k')
        elif typeStability == "saddle":    
            ax.scatter(fPt[i][0],fPt[i][1],s = 80, marker=MarkerStyle("o", fillstyle="right"),facecolors='k',edgecolors='k')
            ax.scatter(fPt[i][0],fPt[i][1],s = 80, marker=MarkerStyle("o", fillstyle="left"),facecolors='none',edgecolors='k')
        elif typeStability == "BC":
            ax.scatter(fPt[i][0],fPt[i][1],s = 80, marker=r'$?$',facecolors='none',edgecolors='k')
        else:
            print("({:.3f},{:.3f}): other cases. Check line 198".format(fPt[i][0],fPt[i][1]))

# Grid for placing quivers
nx, ny = 15, 15
x = np.linspace(minX, maxX, nx)
y = np.linspace(minY, maxY, ny)
X, Y = np.meshgrid(x, y)  
dx, dy = eqnXDotYDot(X,Y) 
ax.quiver(X, Y, dx, dy,color='g',width=0.001,scale=500,scale_units='height')#,angles='xy', scale_units='xy', scale=1)#,scale=5)

ax.set_xlabel('$x$')
ax.set_ylabel('$y$')

if mulPiXAxis:
   ax.xaxis.set_major_locator(plt.MultipleLocator(np.pi))
   ax.xaxis.set_minor_locator(plt.MultipleLocator(1/2*np.pi))
   ax.xaxis.set_major_formatter(plt.FuncFormatter(multiple_formatter()))

if mulPiYAxis:
   ax.yaxis.set_major_locator(plt.MultipleLocator(np.pi))
   ax.yaxis.set_minor_locator(plt.MultipleLocator(1/2*np.pi))
   ax.yaxis.set_major_formatter(plt.FuncFormatter(multiple_formatter()))

ax.set_xlim(1.05*minX, 1.05*maxX)
ax.set_ylim(1.05*minY, 1.05*maxY)
#ax.set_aspect('equal')
plt.grid(True)
plt.tight_layout()
plt.savefig("pplane.png")
plt.show()