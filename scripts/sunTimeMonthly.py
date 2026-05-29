#! /scripts/goes/anaconda/env-radiacao/bin/python
# coding: utf-8



##------ MAIN PROGRAM Sunshine Time Monthly Average-----------##


__author__ = "Marcio Britto"

#modules python-anaconda
from datetime import datetime, timedelta, date
import os
import numpy as np
import sys
import time as t
import commands

#modules DSA
import LibSUN
import RegularFunc



##-------------Start TIME
start = t.time()

##-----check if date was passed as argument if not use current date-----##
today = ""

today = sys.argv[1]


if (today == "xx"):
    
    today = datetime.now()
    
    deltaDay = timedelta(5)
    prevDay = today - deltaDay 
   
    month = '%02d' % prevDay.month
    year = prevDay.year

else:
    year = today[0:4]
    month = today[4:6]

inputdate = str(year)+str(month)
    
print "Executing for date: " +inputdate


##---------paths and files---------##

##-------Paths--------##
outPath = '/'.join(['/dados','goes','goes19_produtos','rad_solar'])
mainPath = '/'.join(['/scripts','goes','goes19','rad_solar','sunshineTime'])
folderBin = outPath+'/insol_diaria_bin/'+str(year)+"/"+str(month)
folderLOG = "/dados/bdi/"

###----CREATE YEAR AND MONTH FOLDERS---##
os.system("mkdir -p " +outPath +"/insol_mensal_bin/"+str(year))
os.system("mkdir -p " +outPath +"/insol_mensal_bin/"+str(year)+"/"+str(month))
os.system("mkdir -p " +outPath +"/insol_mensal/"+str(year))
os.system("mkdir -p " +outPath +"/insol_mensal/"+str(year)+"/"+str(month))


#--------outputs----------##
titleIMG = "Insolacao Media Mensal GOES 19 Horas/Dia - " + inputdate
outputIMG = outPath +"/insol_mensal/"+str(year)+"/"+str(month)+"/S11167059_"+inputdate+"010000.png"
pathBin = outPath +"/insol_mensal_bin/"+str(year)+"/"+str(month)+"/S11167055_"+inputdate+"010000.bin"
pathPGW = outPath +"/insol_mensal/"+str(year)+"/"+str(month)+"/S11167059_"+inputdate+"010000.pgw"


##-----Create list of files for the date------------##
listSun = commands.getoutput("ls " +folderBin+ "/S11167051_"+inputdate+"??0000.bin")


##------verify if output file exists-------##
if (os.path.isfile(pathBin)):
   print "File alredy exist for date: " +inputdate
   sys.exit()    


contentList = listSun.split("\n")
ttfiles = len(contentList)

print "Was found " +str(ttfiles)+ " files! \n"


if (ttfiles < 10):
   print "Total of files is insufficient for date " +inputdate
   sys.exit() 


##------Number Rows x Cols---------##
rows=1800
cols=1800


##----------Create Matrix-----------##
matMonth=np.zeros((rows, cols), float)
matQtd=np.zeros((rows, cols), float)
matVar=np.zeros((rows, cols), float)
matDP=np.zeros((rows, cols), float)

##-------Loop to open the Files anda Calculate the monthly average----------##
for i in range(0,ttfiles,1):
    
    pathFile = contentList[i]
    
    fileX = os.path.basename(pathFile)
    
    dataX = np.fromfile(pathFile, np.uint16)
    dataX = dataX.reshape(rows,cols)
    dataX = np.array(dataX,float)/10

    matMonth = matMonth + dataX
    matQtd[dataX > 0] = matQtd[dataX > 0]+1

matMonth = matMonth/matQtd

NotNumber = np.isnan(matMonth)

matMonth[NotNumber == True] = 0.


# \\\ COMMENTED BC IMAGES ARE REPROJECTED WITHOU GAPS 11/2019 //

##----interpolation 3x3 --- ##
#data = matMonth*1
#dataAux = matMonth*1

#numberCol = data.shape[1]
    
#dataAux = np.vstack((dataAux,np.zeros(numberCol)))
#dataAux = np.vstack((np.zeros(numberCol),dataAux))
    
#numberRol = dataAux.shape[0]

#zerosMatrix = np.zeros(numberRol)
#zerosMatrix = zerosMatrix.reshape(numberRol,1) 

#dataAux = np.hstack((dataAux,zerosMatrix))
#dataAux = np.hstack((zerosMatrix,dataAux))


#for i in range(10):
#    data = RegularFunc.getCompleted(data, dataAux)
    
## --------------------------------------------- ## 
#matMonth = data


#print "Interpolation finished!"


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
RegularFunc.doDataPlot(xx, yy, matMonth, beginLatReg, endLatReg,beginLonReg, endLonReg, outputIMG, titleIMG)
print 'Created image!'


RegularFunc.createBin(matMonth, pathBin)
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

logBIN = open(folderLOG +"7055_"+inputdate+"010000_"+str(tamBIN), 'w')
logBIN.close()
logIMG = open(folderLOG +"7059_"+inputdate+"010000_"+str(tamIMG), 'w')
logIMG.close()

## Convert binary to netcdf
os.system(mainPath+ "/scripts/conv_bin2nc.sh "+inputdate+"010000"+" 7055")


print '- finished! Time:', t.time() - start, 'seconds'

