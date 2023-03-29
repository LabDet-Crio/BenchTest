#!/usr/bin/env python3.9 
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:45:33 2019  @author: Mauricio
updated on Tue May 17 13:11:00 2022  @author: Mauricio

def setSensors/def setCurves
OK->def Read configuration file/def get data V1.0/
OK->main()->read config_file and get data from Model218 and 335 every cycle and print
in the same line



"""

import serial
import time
import argparse

#get configuration from file
def getDictFromConfigFile(configFileName):
    ConfigDict={}
    for line in open(configFileName):
        if line[0] == "#" :
            #print("skipping comment")
            continue
        if line[0] == "\n" :
            #print("skipping comment")
            continue
        List=line.split(":")
        ConfigDict.setdefault(List[0],List[1].strip()) #strip() quita espacios 
    return ConfigDict

#Simple data acquisition rutine, ask for all the channels and print the result
def getData(Ch,port):
    str2port='KRDG? '+str(Ch)+'\r\n'
    try: 
        port.write(str2port.encode())
        datos=port.read(79)
        #print(datos )
        datos=datos.decode().strip('\r\n')
        okFlag=True
    except:
        port.close()
        okFlag=False
        datos='Failed Connection'
        print(datos+' '+LocalTime())
        _,okFlag = RestoredConnection335(port)

    return datos,okFlag

#Define channel sensor status On/Off
def setSensOn(Config): 
    Ch=1
    out={}
    for key in Config:
        if key[0]=='S':  #Sensor 
            if key[7]=='S':  #Status On/Off
                #set On/Off
                str2port='INPUT '+str(Ch)+','+str(Config.get(key))+'\r\n'
                port.write(str2port.encode())
                time.sleep(.1)
                #read status 
                str2port='INPUT? '+str(Ch)+'\r\n'
                port.write(str2port.encode())
                out.setdefault('Sens '+str(Ch),port.read(79).decode().strip())
                time.sleep(.1)
                Ch=Ch+1
            continue
        continue
    print('Status\r')  #Print On/Iff Settings       
    print(out)
    return 'Done\r\n'


#Set type of curve (from user or standar) in Ch channel
def setCurves(Config): 
    Ch=1
    out={}
    for key in Config:
        if key[0]=='C':   #Curve
            if key[1]=='P':  #Parameter
                #Set curve in Ch channel
                str2port='INCRV '+str(Ch)+','+ str(Config.get(key))+'\r\n'
                port.write(str2port.encode())
                time.sleep(.2)
                #read curve value
                str2port='INCRV? '+str(Ch)+'\r\n'
                port.write(str2port.encode())
                out.setdefault(key,port.read(79).decode().strip())
                time.sleep(.2)
                Ch=Ch+1
            continue
        continue
    print('Curves\r') #Print Curve Settings
    print(out)
    return   'Done\r\n'

#Define type of sensors for Group A (ch 1-4) and B (ch 5-8)
def setSensType(Config): 
    Grupos=['A','B']
    Ch=0
    out={}
    for key in Config:
        if key[0]=='S':#Sensor 
            if key[7]=='T':#Type
                #Set Sensor Type
                str2port='INTYPE '+str(Grupos[Ch])+ ','+ str(Config.get(key))+'\r\n'
                port.write(str2port.encode())
                time.sleep(.1)
                #Read Type Value
                str2port='INTYPE? '+str(Grupos[Ch])+'\r\n'
                port.write(str2port.encode())
                out.setdefault(Grupos[Ch],port.read(79).decode().strip())
                time.sleep(.1)
                Ch=Ch+1
            continue
        continue
    print('Type Gpoups\r') #Print Sensor Type
    print(out)
    return   'Done\r\n'

#get Curve points from sensor file curve .dat
def getDictFromCurveFile(file):
    ConfigDict={} 
    for line in open(file): 
        if line[0] == "S" : 
            if line[7] == "M" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],List[1].strip())
                continue
            if line[7] == "N" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],List[1].strip())
                continue
            if line[9] == "L" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],'{:.5}'.format(List[1].strip()))
                continue
            continue    
        
        if line[0] == "D" : 
            if line[5] == "F" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],'{:.1}'.format(List[1].strip()))
                continue
            continue
            
        if line[0] == "T" :
            if line[12] == "c" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],'{:.1}'.format(List[1].strip()))
                continue
            continue      
                        
        if line[0] == "\n" : 
            continue
        
        if line[0] == "N" :
            continue
        
        else: 
            List=line.split("       ") 
            #print(List)
            List[0]=List[0].split("  ")
            ConfigDict.setdefault(List[0][-1],List[1].strip()) #strip() quita espacios  
        #list 0=kelvin, list 1=ohms
    return ConfigDict

#send curve data to Model 218
def addCurve(CurveDict,Ch,index=1):
             #CRVHDR <Ch 21-28>, <sensName>, <SN>, <format>, <limit value>, <coefficient>
    str2port='CRVHDR '+str(Ch)+','+str(CurveDict['Sensor Model'])+','\
    +str(CurveDict['Serial Number'])+','+str(CurveDict['Data Format'])+','\
    +str(CurveDict['SetPoint Limit'])+','+str(CurveDict['Temperature coefficient'])+'\r\n'
    port.write(str2port.encode())
    time.sleep(.1)
    
    for key in CurveDict:
        
        if key.replace('.','').isdigit() == True :
            #CRVPT <Ch 21-28>, <index>, <units value>, <temp value>
            str2port='CRVPT '+str(Ch)+','+str(index)+','+str(key)+','\
            +str(CurveDict.get(key))+'\r\n'
            index=index+1 
            port.write(str2port.encode())
            time.sleep(.1)
            continue
        
        
    
    return 'Done'

#Get Heater Power Value
def HeaterPowerVal(Output,port):
     #HTR? <output> [term]
    try:
        str2port='HTR? '+str(Output)+'\r\n'
        port.write(str2port.encode())
        HeaterPower=port.read(79)
        HeaterPower=HeaterPower.decode().strip('\r\n')

        # Get Range Value 
        #RANGE? <output> [term]
        str2port='RANGE? '+str(Output)+'\r\n'
        port.write(str2port.encode())
        Range=port.read(79)
        Range=Range.decode().strip('\r\n')
    
        if Range == '1':
            RangeVal='Low'
        elif Range == '2':
            RangeVal='Medium'
        elif Range == '3':
            RangeVal='High'
        else:
            RangeVal='Off'
        
        okFlag=True 
    except:
        okFlag=False
        HeaterPower='Bad port Heater Power val'
        RangeVal='Bad port Heater Range val'
        print(HeaterPower+' '+LocalTime()+ '\r')
        print(RangeVal+' '+LocalTime()+'\r')
        RestoredConnection335(port)        

    return HeaterPower, RangeVal, okFlag 
#HP_Val,Rg_Val = HeaterPowerVal(Output,port)
#_,Rg_Val = HeaterPowerVal(Output,port)
#HP_Val,_ = HeaterPowerVal(Output,port)

def LocalTime():
    LocalTime = time.strftime("%H:%M:%S  %Y-%m-%d", time.localtime())
    return LocalTime

# NUEVA PARTE AGREGADA 
def readSetPoint(port_335):
    str1port='SETP? 1'+'\r\n'
    port_335.write(str1port.encode())
    Temp=str(port_335.read(79).decode())
    CurrentTemp="Current Temperature: "+Temp[:7]+' K'
    print(CurrentTemp)

def changeSetPoint(NewSetPoint,port_335):
    str1port='SETP? 1'+'\r\n'
    port_335.write(str1port.encode())
    TempCur=str(port_335.read(79).decode())
    CurrentTemp="Current Temperature: "+TempCur[:7]+' K'
    print(CurrentTemp)

    str1port='SETP 1,'+str(NewSetPoint)+'\r\n'
    port_335.write(str1port.encode())
    time.sleep(2)

    str1port='SETP? 1'+'\r\n'
    port_335.write(str1port.encode())
    TempNew=str(port_335.read(79).decode())
 
    NewTemp='New Temperature: '+TempNew[:7]+' K'
    print(NewTemp)
    return 'SP ok' 

def readRamp(port_335):
    str1port='RAMP? 1'+'\r\n'
    port_335.write(str1port.encode())
    read = port_335.read(79).decode()

    if read[0] == '1':
     print("Current Ramp. \n ") 

     print( ' State: ON')
     print( ' Value: ' + str(read[2:8]) + ' K/minute \n')

    else: 
     print("Current Ramp. \n ") 

     print( ' State: OFF')
     print( ' Value: ' + str(read[2:8]) + ' K/minute \n')
    return 'Ramp OK'

def changeRamp(NewRamp,port_335):
    str1port='RAMP 1,1,'+str(NewRamp)+'\r\n'
    port_335.write(str1port.encode())
    time.sleep(0.5)

    str1port='RAMP? 1'+'\r\n'
    port_335.write(str1port.encode())
    read = port_335.read(79).decode()

    if read[0] == '1': 
     print("New Ramp. \n ") 

     print( ' State: ON')
     print( ' Value: ' + str(read[2:8]) + ' K/minute \n')

    else: 
     print("New Ramp. \n ") 

     print( ' State: OFF')
     print( ' Value: ' + str(read[2:8]) + ' K/minute \n')


def parser():
    parser = argparse.ArgumentParser(prog='Temp Control',description='Programa de vizualizacion y control de temperatura para el banco de pruebas ICN-UNAM')
    
    parser.add_argument('--sp',type= str , nargs = 1,help = "If a '?' is entered then it displays the current temperature. Enter the new temperature in K to change it.")
    parser.add_argument('--ramp',type = str, nargs = 1, help = "If a '?' is entered then it displays the state and the current ramp. Enter the new ramp in  K/minute to change it")

    argObj = parser.parse_args()
    return argObj


def Port_335(File):
    try: 
        ConfigDict_335=getDictFromConfigFile(File)
        fileFlag=True
    except: 
        print('no config for 335 detected')
        fileFlag=False

    if fileFlag:
        try: 
            port_335= serial.Serial(ConfigDict_335['Port'], ConfigDict_335['BaudRate'], serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE, float(ConfigDict_335['TimeOut']))
            ok335Flag=True
            return port_335, ok335Flag
        except:
            print('no model 335 detected')
            ok335Flag=False
            port_335= False
            return port_335,ok335Flag
    else: 
        port_335=False
        ok335Flag=False
        return port_335,ok335Flag 

def RestoredConnection335(port):
    connectionTest = True
    while connetionTest:
        try:
            port.open() 
            ok335Flag = True
            connectionTest = False

        except Exception as Error:
            code_error = type(Error).__name__
            descr_error = type(Error).__doc__
            errorhistory_file(code_error,descr_error)
            print('Error: No model 335 conected ' + LocalTime(), end= '\r')
            time.sleep(30)

    return port,ok335Flag 

def errorhistory_file(code_error,descr_error):
    if str(code_error)=='SerialException':  #Error: Device not  Connected
        error_file=open('Error_fileMauS.log', 'a')
        error_file.write(LocalTime()[10:]+', '+LocalTime()[:8]+', '+str(code_error)+', '+descr_error+'\n')
        error_file.close()




        #okFlag==True 
        #print(ok335Flag.t[0]+'\r') 

#-----------------------
#       main
#-----------------------
#Read Conifig File

def main(argObj):
    if argObj.sp is not None:
     port_335,ok335Flag = Port_335('ConfigFile_M335')
     if ok335Flag:
         if argObj.sp[0]=='?':
                 readSetPoint(port_335)
         else:
                 try: 
                     NewSPValue = float(argObj.sp[0])
                     changeSetPoint(argObj.sp[0],port_335)

                 except:
                     print('Error. Enter a correct command. ')

    elif argObj.ramp is not None:
     port_335,ok335Flag = Port_335('ConfigFile_M335')
     if ok335Flag:
         if argObj.ramp[0]=='?':
                 readRamp(port_335)
         else:
                 try: 
                     NewRampValue = float(argObj.ramp[0])
                     changeRamp(NewRampValue,port_335)

                 except:
                     print('Error. Enter a correct command. ')

    else:
     print('####Temp monitor lite####\n\nWatch the sensor control live.\nNOTE:To stop monitoring "Ctrl+C"\n')
     try:
         ConfigDict_218=getDictFromConfigFile('config_file')
         ok218Flag=True
     except:
         print('no config for 218 detected')
         ok218Flag=False
     try:
         ConfigDict_335=getDictFromConfigFile('ConfigFile_M335')
         ok335Flag=True
     except:
         print('no config for 335 detected')
         ok335Flag=False

     #print(ConfigDict) #Check If all parameters are in the Dictionary
     ConfigDict={}





     #config Serial Port with config_file settings
     try:
         port_218= serial.Serial(ConfigDict_218['Port'], ConfigDict_218['BaudRate'], serial.SEVENBITS,\
                    serial.PARITY_ODD, serial.STOPBITS_ONE, float(ConfigDict_218['TimeOut']))
         ok218Flag=True
     except:
         print('no model 218 detected') #else
         ok218Flag=False

     try:
         port_335= serial.Serial(ConfigDict_335['Port'], ConfigDict_335['BaudRate'], serial.SEVENBITS,\
                    serial.PARITY_ODD, serial.STOPBITS_ONE, float(ConfigDict_335['TimeOut']))
         ok335Flag=True

     except Exception as Error:
         code_error = type(Error).__name__
         descr_error = type(Error).__doc__
         errorhistory_file(code_error,descr_error)

         print('no model 335 detected')    #else
         ok335Flag=False

     #Run Configuration Functions.
     # print a list with settings and "Done" at the end of each one

     #print(setSensType(ConfigDict))
     #print(setCurves(ConfigDict))
     #print(setSensOn(ConfigDict))
     #CurveDict=getDictFromCurveFile('X133491\X133491.340')
     #print(addCurve(CurveDict,26))
     #CurveDict=getDictFromCurveFile('X133492\X133492.340')
     #print(addCurve(CurveDict,25))

     ##
     date=time.strftime("%Y%b%d", time.localtime())

     file=open('history_'+date+'.txt', 'a')
     file.close()

    
     while ok218Flag or ok335Flag:    
         with open('history_'+date+'.txt', 'a', encoding="utf-8") as file:

             try:
                 if ok218Flag:
                     ConfigDict=ConfigDict_218
                     string_218 , ok218Flag = getData(ConfigDict['Channels'],port_218)
                 if ok335Flag:
                     ConfigDict = ConfigDict_335
                     string_A , ok335Flag = getData(ConfigDict['Channel 1'],port_335)
                     string_B , ok335Flag = getData(ConfigDict['Channel 2'],port_335)
                     HP,Range,ok335Flag = HeaterPowerVal(1,port_335)  #This new line add an update for the HP and Range  
                     string_335 = string_A+', '+string_B+', '+ 'HP '+ HP + '% ' + Range
                 if ok218Flag and ok335Flag:
                     print(LocalTime()+','+string_218+','+string_335, end='\r')
                 elif ok218Flag:
                     print(LocalTime()+','+string_218, end='\r')
                 elif ok335Flag:
                     data2print=LocalTime()+', '+string_335 
                     print(data2print, end ='\r')
                     file.write(data2print+'\n')
                 else:
                     print('no sensors are conected')
             except KeyboardInterrupt:
                 print('proceso interrumpido')
                 break
     print('Todo ok')

#error_file=open('Error_fileMauS.log', 'w')
#error_file.write('Date(Y/M/D), Time, Error Code, Error Description \n')
#error_file.close()

if __name__ == "__main__":
   argObj=parser()
   exitcode=main(argObj)
   exit(code=exitcode)

# HP,Range=HeaterPowerVal(1,port_335)
#
