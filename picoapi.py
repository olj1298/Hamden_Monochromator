
import time
import pyvisa as visa
import datetime
import os
import sys
import codecs
import serial
import codecs
import time
import serial

def picgetdata(aslr,Ch1ON,Ch2ON,interval,nsamples,filename):
        '''
        Creates csv file from readings taken by 6482 Picoammeter. The file is located in a "PicoData" sub-directory of the 
        current working directory from where this script executes.
        Inputs:
            :Ch1ON(integer): 1 or 0 corresponding to On, Off respectively
            :Ch2ON(integer): 1 or 0 corresponding to On, Off respectively
            :interval(float): Time between writing data and reading data
            :nsamples(integer): Total readings written to csv log file
            :filename: file name for the data with full path 
        Returns:
            ::Current reading taken by instrument
            ::Error message if exception occurs
        '''
        try:
                runtime = interval * nsamples
                print(f"samples will be taken in a {runtime} second exposure")
                Ch1ON = Ch1ON
                Ch1ULimit = .01  # current upper auto range limit 
                Ch1LLimit = 1e-7  # current lower auto range limit
                Ch1NPLC = 1 # Measurement Speed in NPLC
                Ch1SrcV = 0  # Source Voltage
                Ch2ON = Ch2ON
                Ch2ULimit = .01  # current upper auto range limit 
                Ch2LLimit = 1e-7  # current lower auto range limit 
                Ch2NPLC = 1 # Measurement Speed in NPLC
                Ch2SrcV = 0  # Source Voltage
                if Ch1ON + Ch2ON < 1:
                        print( "This program requires at least one measurement channel:  "+str(Ch1ON+Ch2ON)+" selected" )
                        sys.exit()
                rm = visa.ResourceManager() #create PyVISA instrument session with 6482
                picoa = rm.open_resource(aslr) #asrl# could change depending on the serial port used COM3 goes to asrl3::instr
                picoa.write_termination='\r'
                picoa.read_termination='\r'
                picoa.baud_rate = 9600
                picoa.data_bits = 8
                picoa.parity = visa.constants.Parity.none
                picoa.flow_control = visa.constants.VI_ASRL_FLOW_NONE
                # csvpath = os.getcwd( )+'\\' #we should change this to a user defined path. 
                '''
                Set up 6482 communications from the 6482 front panel: RS-232, 9600 Baud, 8 data bits, No parity, No Flow Control, CR terminator
                USE < and > Edit keys and Enter key to select values.
                Menu -> Communication -> RS-232 (if not already RS-232, you'll hear the instrument click, then repeat above)
                                        -> BAUD -> 9600
                                        -> BITS -> 8
                                        -> PARITY -> NONE
                                        -> TERMINATOR -> <CR>
                                        -> FLOW-CTRL -> NONE
                '''
                # other globals
                outputqueue=[]
                debug=1
                def KISend(cmd):
                        picoa.write(cmd)
                        if debug:
                                print( 'Sent '+cmd)
                def KIRequest(cmd):
                        response = picoa.query( cmd )
                        if debug:
                                print( 'Sent '+cmd)
                                print( 'Received '+response.strip())
                        return(response)
                #create unique file name based on GMT (std) and .csv extension
                dtstmp = filename+datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f")  #datetimestamp file name
                # if not os.path.isdir(csvpath+'PicoData'): #check if ..\Data subdir exists, create it if not, then prepend to dtstmp
                #         os.mkdir(csvpath+'PicoData')
                # dtstmp = 'Dat\\'+dtstmp
                #identify instrument & add response to outputa queue
                outputqueue.append(KIRequest('*IDN?')+'\n')
                print( outputqueue[0]+'added to output queue')
                KISend('*RST') #reset instrument
                #wait for instrument to complete reset
                val = 0
                while val != 1:
                        val = int( KIRequest('*OPC?'))
                # set channel parameters, data format, etc.
                if Ch1ON:
                        KISend(':SENS1:CURR:RANG:AUTO ON')
                        KISend(':SENS1:CURR:RANG:AUTO:ULIM '+str(Ch1ULimit))
                        KISend(':SENS1:CURR:RANG:AUTO:LLIM '+str(Ch1LLimit))
                        KISend(':SENS1:CURR:NPLC '+str(Ch1NPLC))
                        KISend(':SOUR1:VOLT:RANGE:AUTO 1 ')
                        KISend(':SOUR1:VOLT '+str(Ch1SrcV))
                        KISend('OUTP1 ON')
                if Ch2ON:
                        KISend(':SENS2:CURR:RANG:AUTO ON')
                        KISend(':SENS2:CURR:RANG:AUTO:ULIM '+str(Ch2ULimit))
                        KISend(':SENS2:CURR:RANG:AUTO:LLIM '+str(Ch2LLimit))
                        KISend(':SENS2:CURR:NPLC '+str(Ch2NPLC))
                        KISend(':SOUR2:VOLT:RANGE:AUTO 1 ')
                        KISend(':SOUR2:VOLT '+str(Ch2SrcV))
                        KISend('OUTP2 ON')
                formatelements = ''
                if Ch1ON:
                        formatelements = formatelements+'CURR1'
                if Ch1ON and Ch2ON:
                        formatelements = formatelements+','
                if Ch2ON:
                        formatelements = formatelements+'CURR2'
                KISend(':FORM:ELEM '+formatelements)




                # # create CSV file handle
                # csvfile = open(filename+dtstmp+".csv",'w+')
                # # mark last line in output queue
                # queuelastline = len(outputqueue)-1
                # #outputqueue and data header
                # outputqueue.append('Chan 1, TimeStamp\n')
                # print( outputqueue[queuelastline]+'added to output queue')
                # # mark last line in output queue
                # queuelastline = len(outputqueue)-1
                # # add output queue so far to CSV file
                # for csvline in outputqueue:
                #         csvfile.write(csvline)
                #         csvfile.flush()
                # #loop to log measured data to the file
                # StartTime = time.time()
                # SampTime = 0
                # for i in range(1 ,nsamples):
                #         # mark this measurement's time
                #         MeasTime = (i-1) * interval
                #         SampTime = time.time()-StartTime
                #         # Make a measurement, append MeasTime to outputqueue line
                #         MeasLine = KIRequest(':READ?').strip()+', '+str(SampTime)
                #         if debug:
                #                 print( MeasLine+'added to output queue')
                #         outputqueue.append(MeasLine+'\n')
                # # append the latest output queue line to the csv file
                # queuelastline = len(outputqueue)-1 
                # csvline = outputqueue[queuelastline]
                # csvfile.write(csvline)
                # csvfile.flush()
                # DeltaTime = 0
                # while DeltaTime < interval:
                #         DeltaTime = time.time()-StartTime-MeasTime
                # csvfile.close() # close CSV file
                picoa.close() # close PyVISA instrument session
        except Exception as ex:
                msg =f"Could not read using picoammeter. Error: {ex}"
                print(msg)
                return



# #edit directory csv file is placed so user can find it near Lightfield data
# def picrun(aslr,Ch1ON,Ch2ON,interval,nsamples,filename):
#         '''
#         Creates csv file from readings taken by 6482 Picoammeter. The file is located in a "PicoData" sub-directory of the 
#         current working directory from where this script executes.
#         Inputs:
#             :Ch1ON(integer): 1 or 0 corresponding to On, Off respectively
#             :Ch2ON(integer): 1 or 0 corresponding to On, Off respectively
#             :interval(float): Time between writing data and reading data
#             :nsamples(integer): Total readings written to csv log file
#             :filename: file name for the data with full path 
#         Returns:
#             ::Current reading taken by instrument
#             ::Error message if exception occurs
#         '''
#         try:
#                 runtime = interval * nsamples
#                 print(f"samples will be taken in a {runtime} second exposure")
#                 Ch1ON = Ch1ON
#                 Ch1ULimit = .01  # current upper auto range limit 
#                 Ch1LLimit = 1e-7  # current lower auto range limit
#                 Ch1NPLC = 1 # Measurement Speed in NPLC
#                 Ch1SrcV = 0  # Source Voltage
#                 Ch2ON = Ch2ON
#                 Ch2ULimit = .01  # current upper auto range limit 
#                 Ch2LLimit = 1e-7  # current lower auto range limit 
#                 Ch2NPLC = 1 # Measurement Speed in NPLC
#                 Ch2SrcV = 0  # Source Voltage
#                 if Ch1ON + Ch2ON < 1:
#                         print( "This program requires at least one measurement channel:  "+str(Ch1ON+Ch2ON)+" selected" )
#                         sys.exit()
#                 rm = visa.ResourceManager() #create PyVISA instrument session with 6482
#                 picoa = rm.open_resource(aslr) #asrl# could change depending on the serial port used COM3 goes to asrl3::instr
#                 picoa.write_termination='\r'
#                 picoa.read_termination='\r'
#                 picoa.baud_rate = 9600
#                 picoa.data_bits = 8
#                 picoa.parity = visa.constants.Parity.none
#                 picoa.flow_control = visa.constants.VI_ASRL_FLOW_NONE
#                 # csvpath = os.getcwd( )+'\\' #we should change this to a user defined path. 
#                 '''
#                 Set up 6482 communications from the 6482 front panel: RS-232, 9600 Baud, 8 data bits, No parity, No Flow Control, CR terminator
#                 USE < and > Edit keys and Enter key to select values.
#                 Menu -> Communication -> RS-232 (if not already RS-232, you'll hear the instrument click, then repeat above)
#                                         -> BAUD -> 9600
#                                         -> BITS -> 8
#                                         -> PARITY -> NONE
#                                         -> TERMINATOR -> <CR>
#                                         -> FLOW-CTRL -> NONE
#                 '''
#                 # other globals
#                 outputqueue=[]
#                 debug=1
#                 def KISend(cmd):
#                         picoa.write(cmd)
#                         if debug:
#                                 print( 'Sent '+cmd)
#                 def KIRequest(cmd):
#                         response = picoa.query( cmd )
#                         if debug:
#                                 print( 'Sent '+cmd)
#                                 print( 'Received '+response.strip())
#                         return(response)
#                 #create unique file name based on GMT (std) and .csv extension
#                 dtstmp = filename+datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f")  #datetimestamp file name
#                 # if not os.path.isdir(csvpath+'PicoData'): #check if ..\Data subdir exists, create it if not, then prepend to dtstmp
#                 #         os.mkdir(csvpath+'PicoData')
#                 # dtstmp = 'Dat\\'+dtstmp
#                 #identify instrument & add response to outputa queue
#                 outputqueue.append(KIRequest('*IDN?')+'\n')
#                 print( outputqueue[0]+'added to output queue')
#                 KISend('*RST') #reset instrument
#                 #wait for instrument to complete reset
#                 val = 0
#                 while val != 1:
#                         val = int( KIRequest('*OPC?'))
#                 # set channel parameters, data format, etc.
#                 if Ch1ON:
#                         KISend(':SENS1:CURR:RANG:AUTO ON')
#                         KISend(':SENS1:CURR:RANG:AUTO:ULIM '+str(Ch1ULimit))
#                         KISend(':SENS1:CURR:RANG:AUTO:LLIM '+str(Ch1LLimit))
#                         KISend(':SENS1:CURR:NPLC '+str(Ch1NPLC))
#                         KISend(':SOUR1:VOLT:RANGE:AUTO 1 ')
#                         KISend(':SOUR1:VOLT '+str(Ch1SrcV))
#                         KISend('OUTP1 ON')
#                 if Ch2ON:
#                         KISend(':SENS2:CURR:RANG:AUTO ON')
#                         KISend(':SENS2:CURR:RANG:AUTO:ULIM '+str(Ch2ULimit))
#                         KISend(':SENS2:CURR:RANG:AUTO:LLIM '+str(Ch2LLimit))
#                         KISend(':SENS2:CURR:NPLC '+str(Ch2NPLC))
#                         KISend(':SOUR2:VOLT:RANGE:AUTO 1 ')
#                         KISend(':SOUR2:VOLT '+str(Ch2SrcV))
#                         KISend('OUTP2 ON')
#                 formatelements = ''
#                 if Ch1ON:
#                         formatelements = formatelements+'CURR1'
#                 if Ch1ON and Ch2ON:
#                         formatelements = formatelements+','
#                 if Ch2ON:
#                         formatelements = formatelements+'CURR2'
#                 KISend(':FORM:ELEM '+formatelements)




#                 # # create CSV file handle
#                 # csvfile = open(filename+dtstmp+".csv",'w+')
#                 # # mark last line in output queue
#                 # queuelastline = len(outputqueue)-1
#                 # #outputqueue and data header
#                 # outputqueue.append('Chan 1, TimeStamp\n')
#                 # print( outputqueue[queuelastline]+'added to output queue')
#                 # # mark last line in output queue
#                 # queuelastline = len(outputqueue)-1
#                 # # add output queue so far to CSV file
#                 # for csvline in outputqueue:
#                 #         csvfile.write(csvline)
#                 #         csvfile.flush()
#                 # #loop to log measured data to the file
#                 # StartTime = time.time()
#                 # SampTime = 0
#                 # for i in range(1 ,nsamples):
#                 #         # mark this measurement's time
#                 #         MeasTime = (i-1) * interval
#                 #         SampTime = time.time()-StartTime
#                 #         # Make a measurement, append MeasTime to outputqueue line
#                 #         MeasLine = KIRequest(':READ?').strip()+', '+str(SampTime)
#                 #         if debug:
#                 #                 print( MeasLine+'added to output queue')
#                 #         outputqueue.append(MeasLine+'\n')
#                 # # append the latest output queue line to the csv file
#                 # queuelastline = len(outputqueue)-1 
#                 # csvline = outputqueue[queuelastline]
#                 # csvfile.write(csvline)
#                 # csvfile.flush()
#                 # DeltaTime = 0
#                 # while DeltaTime < interval:
#                 #         DeltaTime = time.time()-StartTime-MeasTime
#                 # csvfile.close() # close CSV file
#                 picoa.close() # close PyVISA instrument session
#         except Exception as ex:
#                 msg =f"Could not read using picoammeter. Error: {ex}"
#                 print(msg)
#                 return