#! /scripts/goes/anaconda/env-radiacao/bin/python
# coding: utf-8


##------PACKAGE WITH FUNCTIONS TO SUNSHINE TIME -----------##

__author__ = "Marcio Britto"


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

os.environ['PROJ_LIB'] = "/home/maria.gava/anaconda3/envs/sun_py3/share/proj/"
from mpl_toolkits.basemap import Basemap
plt.switch_backend('agg')


#-----------Function Calculates Julian Day
def calcDayJul(yearI, monthI, dayI):
    
    yearJul = [0,31,59,90,120,151,181,212,243,273,304,334,365]

    if ((yearI % 4) == 0 ) and (monthI > 2):
        dayJ=yearJul[monthI-1]+ dayI +1
    else:
        dayJ=yearJul[monthI-1]+ dayI

    
    return dayJ

##---------Funtion to plot image - regular grid-------##
def doDataPlot(lonMatrix, latMatrix, data, beginLatReg, endLatReg, 
               beginLonReg, endLonReg, outputIMG, titleIMG):

    beginLatFig = beginLatReg
    endLatFig = endLatReg
    beginLonFig = beginLonReg
    endLonFig = endLonReg

    plt.figure(figsize=(15,15))

    m=Basemap(projection='cyl',resolution='l',llcrnrlat=beginLatFig,
      urcrnrlat=endLatFig,llcrnrlon=beginLonFig,urcrnrlon=endLonFig)

  
    #data = np.ma.masked_where(data < 0.01, data)

    cmap = mpl.colors.ListedColormap([
       [ 0.   ,  0.   ,  0.545],
       [ 0.255,  0.412,  0.882],
       [ 0.   ,  0.749,  1.   ],
       [ 0.251,  0.878,  0.816],
       [ 0.   ,  1.   ,  0.   ],
       [ 0.678,  1.   ,  0.184],
       [ 0.941,  0.902,  0.549],
       [ 1.   ,  0.843,  0.   ],
       [ 1.   ,  0.647,  0.   ],
       [ 0.914,  0.588,  0.478],
       [ 1.   ,  0.388,  0.278],
       [ 1.   ,  0.   ,  0.   ],
       [ 0.545,  0.   ,  0.   ]])

    cmap.set_under((1, 1, 1))
    cmap.set_over((0.545,  0.   ,  0.))
    m.pcolormesh(lonMatrix, latMatrix, data, cmap=cmap, vmin=0., vmax=13.)

    #parallels = np.arange(beginLatFig,endLatFig,5.)
    #m.drawparallels(parallels,labels=[1,0,0,1],fontsize="15")
    #meridians = np.arange(beginLonFig,endLonFig,10.)
    #m.drawmeridians(meridians,labels=[1,0,0,1], fontsize="15")
    
    
    #m.drawcountries(linewidth=1.5)
    #m.drawcoastlines(linewidth=1.5)
    #m.drawstates(linewidth=1.5)
    
    #cb = m.colorbar(ticks=[1,2,3,4,5,6,7,8,9,10,11,12,13])
    #cb.ax.tick_params(labelsize=16)
    #plt.colorbar()
    
    plt.savefig(outputIMG,format='png',bbox_inches="tight", pad_inches=-0.1, dpi=158)
    #plt.title(titleIMG, fontsize="30")
    #plt.savefig(outputIMG,format='png',bbox_inches='tight', dpi=100)
    #plt.show()
    
    
def createBin(matrix, pathBin):
    
   fill_value = 65535

   output = np.where(
        np.isnan(matrix),
        fill_value,
        np.round(matrix * 10.0)
   )

   output = output.astype(np.uint16)

   with open(pathBin, "wb") as f:
       output.tofile(f)

   return output
    


# In[ ]:

# metodo para preencher as lacunas nos dados 
def getCompleted(data,dataAux):
    
    numberCol = data.shape[1]
    
    data = np.vstack((data,np.zeros(numberCol)))
    data = np.vstack((np.zeros(numberCol),data))
    
    numberRol = data.shape[0]

    zerosMatrix = np.zeros(numberRol)
    zerosMatrix = zerosMatrix.reshape(numberRol,1) 

    data = np.hstack((data,zerosMatrix))

    dataOriginal = np.hstack((zerosMatrix,data))


    a1 = np.array([-1] + list(range(dataOriginal.shape[1]))[0:-1])
    a1 = dataOriginal[:, a1]

    a2 = np.array(list(range(dataOriginal.shape[1]))[1:] + [0])
    a2 = dataOriginal[:, a2]

    a3 = np.array(list(range(dataOriginal.shape[0]))[1:] + [0])
    a3 = dataOriginal[a3]

    a4 = np.array([-1] + list(range(dataOriginal.shape[0]))[0:-1])
    a4 = dataOriginal[a4]

    a5 = np.array(list(range(dataOriginal.shape[0]))[1:] + [0])
    a5 = a2[a5]

    a6 = np.array(list(range(dataOriginal.shape[0]))[1:] + [0])
    a6 = a1[a6]

    a7 = np.array(list(range(dataOriginal.shape[1]))[1:] + [0])
    a7 = a4[:, a7]

    a8 = np.array([-1] + list(range(dataOriginal.shape[1]))[0:-1])
    a8 = a4[:, a8]

    aSumation = a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8

    dataAverage = aSumation/8

    dataOriginal[dataAux == 0.] = dataAverage[dataAux == 0.]
    dataOriginal = dataOriginal[1:-1,1:-1]
    
    return dataOriginal
