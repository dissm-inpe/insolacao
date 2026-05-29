#! /scripts/goes/anaconda/env-radiacao/bin/python
# coding: utf-8



##------ MAIN PROGRAM Sunshine Time -----------##


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


##-------Paths--------##
outPath = '/'.join(['/dados','goes','goes19_produtos','rad_solar'])
mainPath = '/'.join(['/scripts','goes','goes19','rad_solar','sunshineTime'])
folderRef = outPath+ '/refletancia_vis_bin'
folderLOG = '/dados/bdi/'
                                           
##----CREATE YEAR AND MONTH FOLDERS---##
os.system("mkdir -p " +outPath +"/insol_diaria_bin/"+str(year))
os.system("mkdir -p " +outPath +"/insol_diaria_bin/"+str(year)+"/"+str(month))
os.system("mkdir -p " +outPath +"/insol_diaria/"+str(year))
os.system("mkdir -p " +outPath +"/insol_diaria/"+str(year)+"/"+str(month))


#--------outputs----------##
titleIMG = "Insolacao Media Diaria GOES 19 Horas/Dia - " + inputdate
outputIMG = outPath +"/insol_diaria/"+str(year)+"/"+str(month)+"/S11167057_"+inputdate+"0000.png"
pathBin = outPath +"/insol_diaria_bin/"+str(year)+"/"+str(month)+"/S11167051_"+inputdate+"0000.bin"
pathPGW = outPath +"/insol_diaria/"+str(year)+"/"+str(month)+"/S11167057_"+inputdate+"0000.pgw"

##-----Create list of files for the date------------##
listRef = commands.getoutput("ls " +folderRef +"/"+ str(year)+"/"+str(month)+ "/S11167029_" +inputdate+ "????.ref")

filesRef = listRef.split("\n")


##------verify if output file exists-------##
if (os.path.isfile(pathBin)):
   print "File alredy exist for date: " +inputdate
   sys.exit()  

##----number of files------##
ttfiles = len(filesRef)
print "Was found " +str(ttfiles)+ " files! \n"

if (ttfiles < 5):
   print "Total of files is insufficient for date " +inputdate
   sys.exit() 

##-------Generate matrix lat and lon-------#

beginLatReg = -50.0
endLatReg = 22.0
beginLonReg = -100.0
endLonReg = -28.0


# Grid resolution (degrees)
degree = 0.04

#Create lat and lon matrix
y = np.arange(endLatReg-0.04, beginLatReg-0.04, -(degree))
x = np.arange(beginLonReg, endLonReg, degree)
xx, yy = np.meshgrid(x, y)


##-----------Execute Functions part 1----------##

##------Calculate Julian Day-----------##
yearI = int(inputdate[0:4])
monthI = int(inputdate[4:6])
dayI = int(inputdate[6:8])

dayJ = RegularFunc.calcDayJul(yearI, monthI, dayI)

##------Function to return global parameters----##
PI,convgr, Csolar0, Suvb0, Svisivel0, Sinfra0 = LibSUN.Parametros()

##------Function to calculate astronomic parameters----##
delta, dtempo = LibSUN.paramAstron(dayJ, PI, Csolar0, Suvb0, Svisivel0, Sinfra0)

##----Return time of sunrise and sunset-----------##
horaini, horafin = LibSUN.StartEndSun(xx, yy, PI, convgr, delta, dtempo)

print "Functions OK!"



##----------Create Matrix-----------##
cols = 1800
rows = 1800

matSunTime=np.zeros((rows, cols), float)
matDeltaT=np.zeros((rows, cols), float)
matRmPix=np.zeros((rows, cols), float)
matT1=np.zeros((rows, cols), float)
matTI=np.zeros((rows, cols), float)
matTAux=np.zeros((rows, cols), float)
AreaTr=np.zeros((rows, cols), float)
dataAux=np.zeros((rows, cols), float)


##----Open file 1--------##
pathFileX1 = filesRef[0]
baseNameX1 = os.path.basename(pathFileX1)

refX1 = np.fromfile(pathFileX1, np.int16)
refX1 = refX1.reshape(1800, 1800)
refX1 = np.array(refX1, float)/10.

dataX1= LibSUN.clearSky(refX1)


hourX1 = baseNameX1[18:20]
minX1 = baseNameX1[20:22]
TX1 = float(hourX1) + (float(minX1)/60)
matT1 = matT1 + TX1

matTAux = horaini
TAux = TX1


##-----Compares if first timestep is after 3 hours of sunrise-----## 
deltaT = TX1 - 8.

if(deltaT > 3.):
    print "Rejected day: There is an interval greater than 3 hours!"
    sys.exit()


matDeltaT = matT1 - horaini
matRmPix[matDeltaT > 3.] = 1


indM1 = ((matT1 > horaini) & (matT1 < horafin) & (dataX1 > 0))
indM1 = np.argwhere(indM1==True)

matTAux[indM1[:,0],indM1[:,1]] = matT1[indM1[:,0],indM1[:,1]] 
dataAux[indM1[:,0],indM1[:,1]] = dataX1[indM1[:,0],indM1[:,1]]

##-------Loop to open the Files anda Calculate the daily average----------##
for i in range(1,ttfiles,1):
    
    pathFileXI = filesRef[i]   
    baseNameXI = os.path.basename(pathFileXI)
    
    refXI = np.fromfile(pathFileXI, np.uint16)
    refXI = refXI.reshape(rows,cols)
    refXI = np.array(refXI,float)/10

    dataXI= LibSUN.clearSky(refXI)
    
    hourXI = baseNameXI[18:20]
    minXI = baseNameXI[20:22]
    TXI = float(hourXI) + (float(minXI)/60)
    matTI[:] = 0 + TXI

    deltaT = TXI-TAux
     
    if(deltaT > 3.):
        print "Rejected day: There is an interval greater than 3 hours!"
        sys.exit()
 
    else:

##-------Trapezoid method------##

        sumX=np.zeros((rows, cols), float)
        AreaTr=np.zeros((rows, cols), float)

        indDelta = ((matTI > matTAux) & (matTI < horafin))
        indDelta = np.argwhere(indDelta==True)

        matDeltaT[indDelta[:,0],indDelta[:,1]] = matTI[indDelta[:,0],indDelta[:,1]] - matTAux[indDelta[:,0],indDelta[:,1]]
        matRmPix[matDeltaT > 3.] = 1

        indMI = ((matTI > matTAux) & (matTI < horafin) & (dataXI > 0) & (dataAux > 0))
        indMI = np.argwhere(indMI==True)

        sumX[indMI[:,0],indMI[:,1]] = dataXI[indMI[:,0],indMI[:,1]] + dataAux[indMI[:,0],indMI[:,1]] 
        AreaTr[indMI[:,0],indMI[:,1]] = sumX[indMI[:,0],indMI[:,1]] * (matDeltaT[indMI[:,0],indMI[:,1]])

        matSunTime = matSunTime + (0.5 * AreaTr)
    

##------Replace Matrix Aux to Matrix nº I ---------------##

        TAux = TXI

        indRep = ((matTI > horaini) & (matTI < horafin) & (dataXI > 0))
        indRep = np.argwhere(indRep==True)

        matTAux[indRep[:,0],indRep[:,1]] = matTI[indRep[:,0],indRep[:,1]] 
        dataAux[indRep[:,0],indRep[:,1]] = dataXI[indRep[:,0],indRep[:,1]]


print "Calculation finished!"

##-----Compares if last timestep is earlier than 3 hours of sunset-----## 
deltaT = 23. - TXI

if(deltaT > 3.):
   print "Rejected day: There is an interval greater than 3 hours!"
   sys.exit()


# \\\ COMMENTED BC IMAGES ARE REPROJECTED WITHOUT GAPS 11/2019 //

##----interpolation 3x3 --- ##
#data = matSunTime*1
#dataAux = matSunTime*1

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
#matSunTimeInt = data

#print "Interpolation finished!"


RegularFunc.doDataPlot(xx, yy, matSunTime, beginLatReg, endLatReg,beginLonReg, endLonReg, outputIMG, titleIMG)
print 'Created image!'

RegularFunc.createBin(matSunTime, pathBin)
print 'Created bin file!'

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

logBIN = open(folderLOG +"7051_"+inputdate+"0000_"+str(tamBIN), 'w')
logBIN.close()
logIMG = open(folderLOG +"7057_"+inputdate+"0000_"+str(tamIMG), 'w')
logIMG.close()

## Convert binary to netcdf
os.system(mainPath+ "/scripts/conv_bin2nc.sh "+inputdate+"0000"+" 7051")

print '- finished! Time:', t.time() - start, 'seconds'


