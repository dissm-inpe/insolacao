#! /scripts/goes/anaconda/env-radiacao/bin/python
# coding: utf-8


##------ MAIN PROGRAM SUNSHINE TIME - AVERAGE EVERY 15 DAYS (BIWEEKLY)-----------##


__author__ = "Marcio Britto"


#modules python-anaconda
from datetime import datetime, timedelta, date
import sys
import numpy as np
import os
import time as t
import commands

#from remap import buildLatLonGrid
import RegularFunc
import LibSUN


##-------------Start TIME
start = t.time()

##-----check if date was passed as argument if not use current date-----##
today = ""

today = sys.argv[1]

if (today == "xx"):
    
    today = datetime.now()
    
    deltaDay = timedelta(1)
    prevDay = today - deltaDay 
   
    day = '%02d' % prevDay.day
    month = '%02d' % prevDay.month
    year = prevDay.year

else:
    year = today[0:4]
    month = today[4:6]
    day = today[6:8]

inputdate = str(year)+str(month)+str(day)
    
print "Executing for date: " +inputdate

##---------paths and files---------##
outPath = '/'.join(['/dados','goes','goes19_produtos','rad_solar'])
mainPath = '/'.join(['/scripts','goes','goes19','rad_solar','sunshineTime'])
folderBin = '/'.join([outPath, 'insol_diaria_bin'])
folderLOG = '/dados/bdi/'

##----calculates last 15 days of the date---------##
prevDate = date(int(year), int(month), int(day))
deltaDay15 = timedelta(14)
firstDay = prevDate - deltaDay15
ttfiles = 0

currYear = firstDay.year
currMonth = firstDay.month
currDay = firstDay.day
  
dateFile = str(currYear)+str(currMonth)+str(currDay)

##----CREATE YEAR AND MONTH FOLDERS---##
os.system("mkdir -p " +outPath +"/insol_quinzenal_bin/"+str(year))
os.system("mkdir -p " +outPath +"/insol_quinzenal_bin/"+str(year)+"/"+str(month))
os.system("mkdir -p " +outPath +"/insol_quinzenal/"+str(year))
os.system("mkdir -p " +outPath +"/insol_quinzenal/"+str(year)+"/"+str(month))


#--------outputs----------##
titleIMG="Insolacao Media Quinzenal GOES 19 Horas/Dia \n " +dateFile+ " - " +inputdate
outputIMG = outPath +"/insol_quinzenal/"+str(year)+"/"+str(month)+"/S11167058_"+inputdate+"0000.png"
pathBin = outPath +"/insol_quinzenal_bin/"+str(year)+"/"+str(month)+"/S11167053_"+inputdate+"0000.bin"
pathPGW = outPath +"/insol_quinzenal/"+str(year)+"/"+str(month)+"/S11167058_"+inputdate+"0000.pgw"


##------verify if output file exists-------##
if (os.path.isfile(pathBin)):
   print "File alredy exist for date: " +inputdate
   sys.exit()   


##------Number Rows x Cols---------##
rows=1800
cols=1800


##----------Create Matrix-----------##
matQuin=np.zeros((rows, cols), float)
matQtd=np.zeros((rows, cols), float)

for day in range(0,15,1):
  
    deltaDayAux = timedelta(day)    
    currDate = firstDay + deltaDayAux

    currYear = currDate.year
    currMonth = '%02d' % currDate.month
    currDay = '%02d' % currDate.day
  
    dateFile = str(currYear)+str(currMonth)+str(currDay)

    fileX = folderBin+"/"+str(currYear)+"/"+str(currMonth)+"/S11167051_"+dateFile+"0000.bin"
    print fileX

    if (os.path.isfile(fileX)):

	 dataX = np.fromfile(fileX, np.uint16)
   	 dataX = dataX.reshape(rows,cols)
  	 dataX = np.array(dataX,float)/10

         matQtd[dataX > 0] = matQtd[dataX > 0]+1
   	 matQuin = matQuin + dataX

	 ttfiles = ttfiles +1 
 
         
if (ttfiles < 3):
   print "Total of files is insufficient for date " +inputdate
   sys.exit() 


matQuin = matQuin/matQtd

NotNumber = np.isnan(matQuin)

matQuin[NotNumber == True] = 0.


# \\\ COMMENTED BC IMAGES ARE REPROJECTED WITHOU GAPS 11/2019 //

##----interpolation 3x3 --- ##
data = matQuin*1
dataAux = matQuin*1

numberCol = data.shape[1]
    
dataAux = np.vstack((dataAux,np.zeros(numberCol)))
dataAux = np.vstack((np.zeros(numberCol),dataAux))
    
numberRol = dataAux.shape[0]

zerosMatrix = np.zeros(numberRol)
zerosMatrix = zerosMatrix.reshape(numberRol,1) 

dataAux = np.hstack((dataAux,zerosMatrix))
dataAux = np.hstack((zerosMatrix,dataAux))


for i in range(10):
    data = RegularFunc.getCompleted(data, dataAux)
    
## --------------------------------------------- ## 
matQuin	 = data

print "Interpolation finished!"

##-------Generate matrix lat and lon-------#

beginLatReg = -50.0
endLatReg = 22.0
beginLonReg = -100.0
endLonReg = -28.0

# Geographic area of regular grid (extent[lower-left-x, lly, upper-right-x, ury])
extent = [beginLonReg, beginLatReg, endLonReg, endLatReg]

# Grid resolution (degrees)
degree = 0.04

#Create lat and lon matrix
#lon, lat = buildLatLonGrid(extent, resolution)
y = np.arange(endLatReg-0.04, beginLatReg-0.04, -(degree))
x = np.arange(beginLonReg, endLonReg, degree)
xx, yy = np.meshgrid(x, y)

#---------Functions to plot final results ---------##
RegularFunc.doDataPlot(xx, yy, matQuin, beginLatReg, endLatReg,beginLonReg, endLonReg, outputIMG, titleIMG)
print 'Created image!'

RegularFunc.createBin(matQuin, pathBin)
print 'Created file!'


##------Create navigation file-----##
txtPGW = "0.04000000000000 \n0.00000000000000 \n0.00000000000000 \n-0.0400000000000 \n-100.000000000000 \n21.96000000000" 
filePGW = open(pathPGW, 'w')
filePGW.writelines(txtPGW)
filePGW.close()

##---------------Create LOG-BDI
tamBIN = os.path.getsize(pathBin)
tamBIN = tamBIN/1024

tamIMG = os.path.getsize(outputIMG)
tamIMG = tamIMG/1024

logBIN = open(folderLOG +"7053_"+inputdate+"0000_"+str(tamBIN), 'w')
logBIN.close()
logIMG = open(folderLOG +"7058_"+inputdate+"0000_"+str(tamIMG), 'w')
logIMG.close()

## Convert binary to netcdf
os.system(mainPath+ "/scripts/conv_bin2nc.sh "+inputdate+"0000"+" 7053")

print '- finished! Time:', t.time() - start, 'seconds'

