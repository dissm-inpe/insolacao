#! /scripts/goes/anaconda/env-radiacao/bin/python
# coding: utf-8


##------PACKAGE WITH FUNCTIONS TO SUNSHINE TIME -----------##

__author__ = "Marcio Britto"


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

os.environ['PROJ_LIB'] = "/home/maria.gava/anaconda3/envs/sun_py2/share/proj/"
from mpl_toolkits.basemap import Basemap

##-----Function to Calculate clear sky (1-c)% in 0.5 hour----##
def clearSky(ref):
    
    Rmin=0.093000002
    Rmax=0.465
    
    cols = ref.shape[1]
    lins = ref.shape[0]

    cloud = np.zeros((lins, cols), float)
    
    cloud[ref<=0] = 99
                 
    cloud[ref>0] = (ref[ref>0] - Rmin) / (Rmax - Rmin)
    
    cloud[cloud<0] = 0.
    cloud[cloud>1] = 1.
    
    MatHourSun = (1. - cloud) 
           
    return MatHourSun

#-------------Parametros 

def Parametros():
    
    PI = 3.14159
    convgr = PI/180.
    xlosat = -75.0 
    
    #      Inicio e Fim Canal VIS
    xgoesini =    0.55
    xgoesfin =    0.75
    goeslamda =   0.65
    
    #      Inicio e Fim do Intervalo Ultravioleta
    xuvini  =     0.3
    xuvfin   =    0.4     

    #      Inicio e Fim do Intervalo Visivel
    xvisini =     0.4
    xvisfin =     0.75

    #      Inicio e Fim do Intervalo Infravermelho
    xivini =      0.75
    xivfin =      2.8

    #      Constante Solar na Distancia Media Terra-Sol em w/m2
    Csolar0 =     1357.
    Sgoes0 =      320.
    Suvb0  =      102.
    Svisivel0 =   604.
    Sinfra0 =     643.
    
    #      Fracoes da constante solar
    fuva =        0.0121
    fuvb =        0.0752     
    
    #      Parametros geometricos
    RaioTerra =   6370.
    AltitudeSat = 35790.
    
    return PI,convgr, Csolar0, Suvb0, Svisivel0, Sinfra0

  
#-------------Funcao para calcular parametros Astronomicos, Geometricos e Irradiancias solar corrigida.
def paramAstron(diaj, PI, Csolar0, Suvb0, Svisivel0, Sinfra0):

    
    #Calculo da declinacao (Paltridge e Platt 1976, baseado em Spencer 1971).

    teta = 2. * PI * diaj / 365.
    
    delta = (.006918 - .399912 * np.cos(teta) + .070257 * np.sin(teta) - .006758 * np.cos(2. * teta) +
            .000907 * np.sin(2. * teta) - .002697 * np.cos(3. * teta) + .00148 * np.sin(3. * teta))
    
    #Equacao do tempo (Spencer 1971 in Paltridge e Platt 1976).
    dtempo = (.000075 + .001868 * np.cos(teta) - .032077 * np.sin(teta) - .014615 * 
              np.cos(2. * teta) - .040849 * np.sin(2. * teta))
    
    #Correcao distancia Terra-Sol (Paltridge e Platt 1976)
    r2sun = 1.00011 + .034221 * np.cos(teta) + .000128 * np.sin(teta) + .000719
    
    #Irradiâncias corrigidas pela distância terra-sol.
    Csolar   = Csolar0 * r2sun
    Suvb     = Suvb0 * r2sun
    Svisivel = Svisivel0 * r2sun
    Sinfra   = Sinfra0 * r2sun
    
    return delta, dtempo
    

#------Calculate time of sunset and sunrise---##
def StartEndSun(lon, lat, PI, convgr, delta, dtempo):


    ylat = lat * convgr
    ylon = lon * convgr

    dlon = lon / 15.
    dt = dtempo * 180. / (PI * 15.)

    h = np.arccos(-(np.tan(delta) * np.tan(ylat)))
       
    horsol = 12. - (h / (15. * convgr))
    horaini = horsol - dt - dlon
       
    horsol = 12. + (h / (15. * convgr))
    horafin = horsol - dt - dlon

    return horaini, horafin
