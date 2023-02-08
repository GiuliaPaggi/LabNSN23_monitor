import time, os, sys
import matplotlib.pyplot as plt
from datetime import datetime
import configparser
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import streamlit as st
import PLOTS


#plt.switch_backend('TkAgg')

# ------ set up webpage ------
st.set_page_config(
    page_title="Monitor",
    page_icon=':flag-bo:',
    layout="wide",
)
monitor = st.empty()

refresh_time = 5       # seconds

# ----- import path from configuration file -----
config = configparser.ConfigParser()
config_file = './config.txt'                  
if os.path.exists(config_file): 
    config.read(config_file)     
else : 
    print( 'Select the configuration file', flush=True)
    Tk().withdraw()
    config_file = askopenfilename()
    config.read(config_file)


data_path = config.get('path', 'DataFilePath')
plot_path = config.get('path', 'PlotFolderPath')

if not os.path.exists(plot_path):
    os.mkdir(plot_path)          




# ----- check if the file exists, close the program if it does not -----
if os.path.exists(data_path):
    f = open(data_path, 'r')
    print(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+ ' Reading ' + data_path )

else:
    print("Error, output data file "+data_path+" does not exists! Press CTRL-C to exit")
    st.write("Error, output data file does not exists! Exiting...")
    st.stop()
    sys.exit()


#if show_plt:
    # ----- set interactive mode so that pyplot.show() displays the figures and immediately returns ----
#    plt.ion() 
    # fig, ax = plt.subplots(4, 2, figsize = (15, 10))
    # fig_timebox, ax_timebox = plt.subplots(4, 3, figsize = (15, 10))

# ------ number of event per plane ------
planes_events = [0]*3

bins = 512 #4096
# ------ time histograms ------
hist_p0 =[0]*bins
hist_p1 =[0]*bins
hist_p2 =[0]*bins

x_axis = range(bins)

# ------ rate ------
average_rate = 0
inst_rate = 0
rate_info = [0, 0]          # [n evento, tempo]
rate_over_time = [0]


# ------ read file ------

# find the size of the file and set pointer to the end
#st_results = os.stat(data_path)
#st_size = st_results[6]
#f.seek(st_size)



try:
    
    while( True ):        
        # try to read a line
        where = f.tell()
        time.sleep(refresh_time)
        line = f.readlines()

        # if reading fails, sleep 0.1s and set pointer back before the failed reading
        if not line:
            print('No new lines to be read.')
            # print(time.time() - os.path.getmtime(filename))
            if time.time() - os.path.getmtime(data_path) > 120 :
                print ('\nReading stopped.\n') 
                f.close()
                os._exit(0)
                st.stop()
                #sys.exit()
            f.seek(where)
            
        # if the reading is successfull process the string
        else:    
 
            #check line integrity
            if not line[0].startswith('_'):
                line.pop(0)
        
            if not line[len(line)-1].endswith('\n'):
                line.pop(len(line)-1)
            
            delta_t = float( line[len(line)-1].split(' ')[1] ) - float(line[0].split(' ')[1] )
            rate = round (len(line)/delta_t)
            
            
            for i in range(0, len(line)): 

                #convert to decimal
                p0_value = int ( line[i].split(' ')[3] , 16) 
                p1_value = int ( line[i].split(' ')[4] , 16)
                p2_value = int ( line[i].split(' ')[5] , 16)
                
                #fill the histos
                if p0_value != 4095:
                # istogramma con sottomultiplo di 4096-> uso il valore/ n come indice
                    #print('p0', p0_value)
                    hist_p0[round(p0_value*.125)] +=1
                    #print(hist_p0)
                if p1_value != 4095:    
                    hist_p1[round(p1_value*.125)] +=1
                    #print('p1', p1_value)
                if p2_value != 4095:    
                    hist_p2[round(p2_value*.125)] +=1
                    #print('p2', p2_value)


            #compute rate            
            average_rate = round ( int(line[len(line)-1].split(' ')[1]) / float(line[len(line)-1].split(' ')[2]) , 2)
            
            elapsed_time =  ( float(line[len(line)-1].split(' ')[2]) - rate_info[1])
            #print('elapsed time:', elapsed_time)
            if  elapsed_time > refresh_time*2:
                inst_rate = round ( ( int(line[len(line)-1].split(' ')[1]) - rate_info[0])/ elapsed_time , 2)
                #print(inst_rate)
                if len(rate_over_time) > 99:
                    rate_over_time.pop(0)
                    rate_over_time.append(inst_rate)
                    #print('più di 100 eventi')
                    #print(inst_rate)
                else:
                    rate_over_time.append(inst_rate)
                    #print(inst_rate)
                rate_info[1] = float(line[len(line)-1].split(' ')[2])
                rate_info[0] = int(line[len(line)-1].split(' ')[1])
            
            
            # display plots with matplotlib
            #if show_plt:
            #    PLOTS.plot_1D(fig, ax[0][0], x_axis, hist_p0, "P0 Entries", "Channel", "Entries", 'P0')
            #    PLOTS.plot_1D(fig, ax[0][0], x_axis, hist_p1, "P1 Entries", "Channel", "Entries", 'P1')
            #    PLOTS.plot_1D(fig, ax[0][0], x_axis, hist_p2, "P2 Entries", "Channel", "Entries", 'P2')
            # save plots in folder and update monitor web page 
            PLOTS.save_1D(plot_path, x_axis, hist_p0, "P0", "Channel", "Entries", 'P0')
            PLOTS.save_1D(plot_path, x_axis, hist_p1, "P1", "Channel", "Entries", 'P1')
            PLOTS.save_1D(plot_path, x_axis, hist_p2, "P2", "Channel", "Entries", 'P2')
                        
            PLOTS.update_monitor(plot_path, monitor, ['P0.PNG', 'P1.PNG', 'P2.PNG'], str(average_rate), str(inst_rate), str(sum(hist_p0)), str(sum(hist_p1)), str(sum(hist_p2)), rate_over_time, line[len(line)-1].split(' ')[1])
                     
                
except KeyboardInterrupt:
    print ('\nReading stopped.\n') 
    sys.exit()
    f.close()