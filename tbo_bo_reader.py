import time, os, sys
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
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

# ----- import path from configuration file -----
config = configparser.ConfigParser()
config_file = '/home/gpaggi/dtupy/scripts/config.txt'                  #/home/gpaggi/dtupy/scripts/
if os.path.exists(config_file): 
    config.read(config_file)     
else : 
    print( 'Select the configuration file', flush=True)
    Tk().withdraw()
    config_file = askopenfilename()
    config.read(config_file)


data_path = config.get('path', 'DataFolderPath')
plot_path = config.get('path', 'PlotFolderPath')
display_path = config.get('path', 'LiveFolderPath')
logfile_path = config.get('file', 'LogFile')
show_plt = config.getboolean('option', 'ShowPlots')
# ----- run number can be passed as an argument from the terminal command line -----

if len(sys.argv)>1:
    n_run = int(sys.argv[1])
    run_name = "Run_" + str(n_run)
# if run number is not given, read runs log files to find the current one 
else :
    if os.path.exists(logfile_path):
        log_file = open(logfile_path, 'r')
        n_run = int(log_file.readlines()[-1].split(' ')[0]) + 1
        run_name = "Run_" + str(n_run)
    else :
        n_run = -1
        run_name = "FakeRun"
    
# ----- to use the file generated with the simulator use r_number = -1 -----
if n_run == -1: 
    filename = "FakeRun.txt"
    data_path = ''
    plot_path = ''
    dir_path = run_name+'/'
    display_path = dir_path+'Event_display/'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    if not os.path.exists(display_path):
        os.mkdir(display_path)

else : 
    filename =  run_name + ".txt"  
    dir_path = plot_path+run_name+'/' 
    #display_path = dir_path+'Event_display/'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)          
    if not os.path.exists(display_path):
        os.mkdir(display_path)


# ----- check if the file exists, close the program if it does not -----
if os.path.exists(data_path+filename):
    f = open(data_path+filename, 'r')
    print(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+ ' Reading ' + filename )

else:
    print("Error, output data file "+filename+" does not exists! Press CTRL-C to exit")
    st.write("Error, output data file does not exists! Exiting...")
    st.stop()
    sys.exit()


# ------ assign channel to pin -------
obdt_connectors = {
  'o':[234,36,50,48,44,46,41,204,220,217,219,233,214,237,15,169],
  'a':[222,45,49,52,43,209,53,51,215,235,238,28,30,31,20,17],
  'b':[14,16,108,13,221,89,90,57,88,198,42,38,37,39,186,0],
  'i':[6,47,207,54,208,205,206,212,225,18,101,12,110,111,126,125],
  'j':[112,188,187,154,170,179,180,182,183,199,195,193,189,191,203,190],
  'g':[4,211,210,228,230,224,236,25,21,106,103,127,131,172,85,151],
  'h':[218,150,158,160,56,86,75,87,173,174,178,200,202,201,5,26],
  'e':[33,27,10,231,232,109,213,239,226,223,7,227,2,8,114,113],
  'f':[229,139,141,143,161,59,63,65,58,60,175,171,177,181,185,184],
  'k':[104,35,98,11,1,3,24,9,121,102,123,107,138,128,129,130],
  'l':[216,55,91,93,66,72,79,76,81,78,74,64,70,176,162,69],
  'c':[119,115,96,29,32,19,34,22,142,105,137,120,124,152,149,165],
  'd':[40,62,73,153,148,155,156,157,159,166,61,82,77,68,146,147],
  'm':[122,117,23,99,100,116,118,134,132,136,135,144,145,163,164,167],
  'n':[140,92,94,95,97,67,71,80,83,168,196,192,194,84,133,197],
  }

layer=[4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1]
wire=[1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16]


channel = range(128)
pins = obdt_connectors['a'] + obdt_connectors['b'] + obdt_connectors['c'] + obdt_connectors['d'] + obdt_connectors['e'] + obdt_connectors['f'] + obdt_connectors['k'] +obdt_connectors['l']

if show_plt:
    # ----- set interactive mode so that pyplot.show() displays the figures and immediately returns ----
    plt.ion() 
    fig, ax = plt.subplots(4, 2, figsize = (15, 10))
    fig_timebox, ax_timebox = plt.subplots(4, 3, figsize = (15, 10))

x_axis = range(64)

# ----- set up 1d channel occupancy -----
entries_CH7 = [0] *64 
entries_CH8 = [0] *64 

# ----- set up 2d chamber occupancy -----
entries_2d_CH7 = np.array([[0]*16]*4)
entries_2d_CH8 = np.array([[0]*16]*4)

# ------ set up rate ------
rate_entries_CH7 = [0] *64 
rate_entries_CH8 = [0] *64 

# ----- set up 2d rate -----
rate_2d_CH7 = np.array([[0]*16]*4, dtype = float)
rate_2d_CH8 = np.array([[0]*16]*4, dtype = float)

# ----- set up timebox cumulative and instantaneous -----
offset_timebox = 500
length_timebox = 200
timebox_xaxis = range(length_timebox)
timebox_ticks = [0, 25, 50, 75, 100, 125, 150, 175, 200]

timebox_entries_CH7 = [0] *length_timebox
inst_timebox_CH7 = []
inst_timebox_entries_CH7 = [0] *length_timebox

timebox_entries_CH8 = [0] *length_timebox
inst_timebox_CH8 = []
inst_timebox_entries_CH8 = [0] *length_timebox

# ----- set up occupancy of scintillators events -----
scint_entries_CH7 = [0]*64
scint_entries_2d_CH7 = np.array([[0]*16]*4)
scint_rate_CH7 = [0]*64
scint_rate_2d_CH7 = np.array([[0]*16]*4, dtype = float)

scint_entries_CH8 = [0]*64
scint_entries_2d_CH8 = np.array([[0]*16]*4)
scint_rate_CH8 = [0]*64
scint_rate_2d_CH8 = np.array([[0]*16]*4, dtype = float)


# ------ read file ------

# find the size of the file and set pointer to the end
st_results = os.stat(data_path+filename)
st_size = st_results[6]
f.seek(st_size)

#total number of scintillator+ 4 hits per chamber events
event_number = 0
#total number of scintillator events
scint_event = 0
scint_rate_vs_time = []
#number of CH7 hit
CH7_event = 0
CH7_rate_vs_time = []
#number of CH8 hit
CH8_event = 0
CH8_rate_vs_time = []

event_orbit_number = -1
double_scint_counter = 0

try:
    
    while( True ):
        
        # try to read a line
        where = f.tell()
        time.sleep(30)
        line = f.readlines()

        # if reading fails, sleep 0.1s and set pointer back before the failed reading
        if not line:
            print('No new lines to be read.')
            # print(time.time() - os.path.getmtime(filename))
            if time.time() - os.path.getmtime(filename) > 120 :
                print ('\nReading stopped.\n') 
                f.close()
                os._exit(0)
                st.stop()
                #sys.exit()
            f.seek(where)
            
        # if the reading is successfull process the string
        else:    
            #number of event display file, in range 0-12
            display_event = 0
            
            scint_event = 0
            double_scint_counter = 0
            CH7_event = 0
            CH8_event = 0
            
            #reset rate histo chamber 7
            rate_entries_CH7 = [0] *64 
            rate_2d_CH7 [rate_2d_CH7>0] = 0
            inst_timebox_entries_CH7 = [0] *length_timebox
            scint_rate_CH7 = [0] *64
            scint_rate_2d_CH7 [scint_rate_2d_CH7>0] = 0
            
            #reset rate histo chamber 7
            rate_entries_CH8 = [0] *64 
            rate_2d_CH8 [rate_2d_CH8>0] = 0
            inst_timebox_entries_CH8 = [0] *length_timebox
            scint_rate_CH8 = [0] *64
            scint_rate_2d_CH8 [scint_rate_2d_CH8>0] = 0
            
            scint = False
            #check line integrity
            if not line[0].startswith('_'):
                line.pop(0)
        
            if not line[len(line)-1].endswith('\n'):
                line.pop(len(line)-1)

            delta_t = float( line[len(line)-1].split(' ')[1] )- float(line[0].split(' ')[1] )
            rate =round (len(line)/delta_t)
            
            for i in range(0, len(line)):
                try: 
                    data_pin = int( line[i].split(' ')[3])
                    data_channel = pins.index( data_pin )
                    
                    # CHAMBER 7
                    if data_channel < 64:
                        CH7_event+=1
                        # ---- fill 1d occupancy ----
                        entries_CH7[data_channel] +=1
                        rate_entries_CH7[data_channel] += 1/delta_t
                        
                        
                        data_wires = wire[data_channel]
                        data_layers = layer[data_channel]
                        # ---- fill 2d occupancy ----
                        entries_2d_CH7[data_layers -1][data_wires -1] +=1
                        rate_2d_CH7[data_layers -1][data_wires -1] += 1/delta_t
                        
                    #CHAMBER 8
                    else: 
                        CH8_event+=1
                        data_channel = data_channel-64
                        # ---- fill 1d occupancy ----
                        entries_CH8[data_channel] +=1
                        rate_entries_CH8[data_channel] += 1/delta_t
                        
                        
                        data_wires = wire[data_channel]
                        data_layers = layer[data_channel]
                        # ---- fill 2d occupancy ----
                        entries_2d_CH8[data_layers -1][data_wires -1] +=1
                        rate_2d_CH8[data_layers -1][data_wires -1] += 1/delta_t
                    
                    
                    
                except ValueError:
                    if (data_pin!=228): 
                        pin_error = "\n\n ----- Unexpected pin at pin: "+str(data_pin)+ "----- \n\n"
                        print(pin_error)
                    data_pin = 228
                    
                    scint = True
                    #recover trigger hit info
                    
                    tr_orbit = int(line[ i ].split(' ')[2])  
                    if tr_orbit == event_orbit_number: 
                        #print(tr_orbit == event_orbit_number)
                        double_scint_counter += 1
                        continue
                    
                    scint_event +=1
                    event_orbit_number = tr_orbit
                    tr_systime = float(line[ i ].split(' ')[1])
                    tr_bx =  int( line[ i ].split(' ')[4] )
                    tr_tdc = int( line[ i ].split(' ')[5].strip('\n') )
                    tr_time = tr_bx*25.0 + tr_tdc*25/30
                    j=1
                    l=1
                    event_ch_CH7 = []
                    event_info_CH7 = "Chamber 7:\n"
                    event_ch_CH8 = []
                    event_info_CH8 = "Chamber 8:\n"
                    
                    while( line[ i ].split(' ')[2] == line[ i-j ].split(' ')[2]) :
                        #fill scintillator channel occupancy
                        hit_pin = int(line[ i-j ].split(' ')[3]  )
                    
                        if hit_pin != data_pin:
                            hit_channel = pins.index(hit_pin)
                            #compute hits time
                            hit_bx =  int( line[ i-j ].split(' ')[4] )
                            hit_tdc = int( line[ i-j ].split(' ')[5].strip('\n') )
                            hit_time = hit_bx*25.0 + hit_tdc*25/30
                            #compute time diff and fill a histo with bin width = tdc resolution for cumulative timebox
                            time_diff= hit_time - tr_time + offset_timebox
                            index=round(time_diff * 30/25 *.125) 
                            hit_orbit = int( line[ i-j ].split(' ')[2] )
                            
                            if hit_channel <64:
                                event_ch_CH7.append(hit_channel)
                                hit_info = "Ch: "+str(hit_channel)+" Orbit: " +str(hit_orbit)+" BX: "+ str(hit_bx)+"\n"
                                event_ch_CH7.append(hit_channel)
                                event_info_CH7+=hit_info
                                #fill scintillator 1d occupancy
                                scint_entries_CH7[hit_channel] += 1
                                scint_rate_CH7[hit_channel] += 1/delta_t
                                
                                #fill scintillator 2d occupancy
                                hit_wire = wire[hit_channel]
                                hit_layer = layer[hit_channel]
                                scint_entries_2d_CH7[hit_layer-1][hit_wire -1] +=1
                                scint_rate_2d_CH7[hit_layer-1][hit_wire -1] += 1/delta_t
    
                                try: 
                                    timebox_entries_CH7[index] +=1
                                    inst_timebox_entries_CH7[index] +=1
                                except IndexError: 
                                    pass
                                    #print(time_diff, index)
                            else:
                                hit_channel = hit_channel - 64
                                hit_info = "Ch: "+str(hit_channel)+" Orbit: " +str(hit_orbit)+" BX: "+ str(hit_bx)+"\n"
                                event_ch_CH8.append(hit_channel)
                                event_info_CH8+=hit_info
                                #fill scintillator 1d occupancy
                                scint_entries_CH8[hit_channel] += 1
                                scint_rate_CH8[hit_channel] += 1/delta_t
                                
                                #fill scintillator 2d occupancy
                                hit_wire = wire[hit_channel]
                                hit_layer = layer[hit_channel]
                                scint_entries_2d_CH8[hit_layer-1][hit_wire -1] +=1
                                scint_rate_2d_CH8[hit_layer-1][hit_wire -1] += 1/delta_t
    
                                try: 
                                    timebox_entries_CH8[index] +=1
                                    inst_timebox_entries_CH8[index] +=1
                                except IndexError: 
                                    pass
                                    #print(time_diff, index )

                        
                        j +=1
                        
                        
                    while( i+l < len(line) and  line[ i ].split(' ')[2] == line[ i+l ].split(' ')[2]) :
                        #fill scintillator channel occupancy
                        hit_pin = int(line[ i+l ].split(' ')[3]  )
                    
                        if hit_pin != data_pin:
                            hit_channel = pins.index(hit_pin)
                            #compute hits time
                            hit_bx =  int( line[ i+l ].split(' ')[4] )
                            hit_tdc = int( line[ i+l ].split(' ')[5].strip('\n') )
                            hit_time = hit_bx*25.0 + hit_tdc*25/30
                            #compute time diff and fill a histo with bin width = tdc resolution for cumulative timebox
                            time_diff= hit_time - tr_time + offset_timebox
                            index=round(time_diff * 30/25 *.125) 
                            hit_orbit = int( line[ i+l ].split(' ')[2] )
                            
                            if hit_channel <64:
                                event_ch_CH7.append(hit_channel)
                                hit_info = "Ch: "+str(hit_channel)+" Orbit: " +str(hit_orbit)+" BX: "+ str(hit_bx)+"\n"
                                event_ch_CH7.append(hit_channel)
                                event_info_CH7+=hit_info
                                #fill scintillator 1d occupancy
                                scint_entries_CH7[hit_channel] += 1
                                scint_rate_CH7[hit_channel] += 1/delta_t
                                
                                #fill scintillator 2d occupancy
                                hit_wire = wire[hit_channel]
                                hit_layer = layer[hit_channel]
                                scint_entries_2d_CH7[hit_layer-1][hit_wire -1] +=1
                                scint_rate_2d_CH7[hit_layer-1][hit_wire -1] += 1/delta_t
    
                                try: 
                                    timebox_entries_CH7[index] +=1
                                    inst_timebox_entries_CH7[index] +=1
                                except IndexError: 
                                    pass
                                    #print(time_diff, index)
                            else:
                                hit_channel = hit_channel - 64
                                hit_info = "Ch: "+str(hit_channel)+" Orbit: " +str(hit_orbit)+" BX: "+ str(hit_bx)+"\n"
                                event_ch_CH8.append(hit_channel)
                                event_info_CH8+=hit_info
                                #fill scintillator 1d occupancy
                                scint_entries_CH8[hit_channel] += 1
                                scint_rate_CH8[hit_channel] += 1/delta_t
                                
                                #fill scintillator 2d occupancy
                                hit_wire = wire[hit_channel]
                                hit_layer = layer[hit_channel]
                                scint_entries_2d_CH8[hit_layer-1][hit_wire -1] +=1
                                scint_rate_2d_CH8[hit_layer-1][hit_wire -1] += 1/delta_t
    
                                try: 
                                    timebox_entries_CH8[index] +=1
                                    inst_timebox_entries_CH8[index] +=1
                                except IndexError: 
                                    pass
                                    #print(time_diff, index )

                        
                        l +=1

                    if len(event_ch_CH7) > 3 and len(event_ch_CH8) > 3 :
                        event_number+=1 
                        # if len(event_ch_CH7) > 10 or len(event_ch_CH8) >10: 
                        #     pass
                        # else:
                        if event_number%37 == 0:

                            PLOTS.event_display(display_path, display_event, event_ch_CH7, event_info_CH7, event_ch_CH8, event_info_CH8, run_name, event_number)
                            display_event+=1
            
            #compute rate
            scint_rate = round( scint_event/delta_t)
            if len(scint_rate_vs_time) > 25 : 
                scint_rate_vs_time.pop(0)
                scint_rate_vs_time.append(scint_rate)
            else: 
                scint_rate_vs_time.append(scint_rate)
                
            #print(double_scint_counter)
            if scint_event == 0:
                double_scint_perc = -1
            else:
                double_scint_perc = round(double_scint_counter/scint_event, 2)
            
            CH7_rate = round( CH7_event/delta_t)
            if len(CH7_rate_vs_time) > 25 : 
                CH7_rate_vs_time.pop(0)
                CH7_rate_vs_time.append(CH7_rate)
            else: 
                CH7_rate_vs_time.append(CH7_rate)
            #print(CH7_rate_vs_time, flush = True)

            CH8_rate = round( CH8_event/delta_t)
            if len(CH8_rate_vs_time) > 25 : 
                CH8_rate_vs_time.pop(0)
                CH8_rate_vs_time.append(CH8_rate)
            else: 
                CH8_rate_vs_time.append(CH8_rate)
            #Sprint(CH8_rate_vs_time, flush = True)
            
            # display plots with matplotlib
            if show_plt:
                #plot CHAMBER 7
                PLOTS.plot_1D(fig, ax[0][0], x_axis, entries_CH7, "Entries", n_run, "Channel", "Entries", 'Chamber-7')
                PLOTS.plot_2D(fig, ax[1][0], entries_2d_CH7, "Entries_2D", n_run, "Wire", "Layer", 'Chamber-7' )
                PLOTS.plot_1D(fig, ax[0][1], x_axis, rate_entries_CH7, "Rate", n_run, "Channel", "Rate (Hz)", 'Chamber-7')
                PLOTS.plot_2D(fig, ax[1][1], rate_2d_CH7, "Rate_2D", n_run, "Wire", "Layer", 'Chamber-7')   
                #plot CHAMBER 8
                PLOTS.plot_1D(fig, ax[2][0], x_axis, entries_CH8, "Entries", n_run, "Channel", "Entries", 'Chamber-8')
                PLOTS.plot_2D(fig, ax[3][0], entries_2d_CH8, "Entries_2D", n_run, "Wire", "Layer", 'Chamber-8' )
                PLOTS.plot_1D(fig, ax[2][1], x_axis, rate_entries_CH8, "Rate", n_run, "Channel", "Rate (Hz)", 'Chamber-8')
                PLOTS.plot_2D(fig, ax[3][1], rate_2d_CH8, "Rate_2D", n_run, "Wire", "Layer", 'Chamber-8')   
                if scint:
                    #plot scint CHAMBER 7
                    PLOTS.plot_1D(fig_timebox, ax_timebox[0][0], timebox_xaxis , timebox_entries_CH7, "Cumulative_Timebox", n_run, "TDC units", "Entries" , 'Chamber-7',  xticks= timebox_ticks)
                    PLOTS.plot_1D(fig_timebox, ax_timebox[1][0], timebox_xaxis , inst_timebox_entries_CH7, "Inst_Timebox", n_run, "TDC units", "Entries", 'Chamber-7' ,  xticks= timebox_ticks )
                    PLOTS.plot_1D(fig_timebox, ax_timebox[0][1], channel, scint_entries_CH7, "Scintillator_event_entries", run_name, "Channel", "Entries", 'Chamber-7')
                    PLOTS.plot_2D(fig_timebox, ax_timebox[0][2], scint_entries_2d_CH7, "Scintillator_event_entries_2D", run_name, "Wire", "Layer", 'Chamber-7')
                    PLOTS.plot_1D(fig_timebox, ax_timebox[1][1], channel, scint_rate_CH7, "Scintillator_event_rate", run_name, "Channel", "Rate", 'Chamber-7')
                    PLOTS.plot_2D(fig_timebox, ax_timebox[1][2], scint_rate_2d_CH7, "Scintillator_event_rate_2D", run_name, "Wire", "Layer", 'Chamber-7')
                    #plot scint CHAMBER 8
                    PLOTS.plot_1D(fig_timebox, ax_timebox[2][0], timebox_xaxis , timebox_entries_CH8, "Cumulative_Timebox", n_run, "TDC units", "Entries" , 'Chamber-8',  xticks= timebox_ticks)
                    PLOTS.plot_1D(fig_timebox, ax_timebox[3][0], timebox_xaxis , inst_timebox_entries_CH8, "Inst_Timebox", n_run, "TDC units", "Entries", 'Chamber-8' ,  xticks= timebox_ticks )
                    PLOTS.plot_1D(fig_timebox, ax_timebox[2][1], channel, scint_entries_CH8, "Scintillator_event_entries", run_name, "Channel", "Entries", 'Chamber-8')
                    PLOTS.plot_2D(fig_timebox, ax_timebox[2][2], scint_entries_2d_CH8, "Scintillator_event_entries_2D", run_name, "Wire", "Layer", 'Chamber-8')
                    PLOTS.plot_1D(fig_timebox, ax_timebox[3][1], channel, scint_rate_CH8, "Scintillator_event_rate", run_name, "Channel", "Rate", 'Chamber-8')
                    PLOTS.plot_2D(fig_timebox, ax_timebox[3][2], scint_rate_2d_CH8, "Scintillator_event_rate_2D", run_name, "Wire", "Layer", 'Chamber-8')
 
            # save plots in folder and update monitor web page 
            #save CHAMBER 7
            PLOTS.save_1D(dir_path, x_axis, entries_CH7, "Entries", run_name, "Channel", "Entries", 'Chamber-7')
            PLOTS.save_2D(dir_path, entries_2d_CH7, "Entries_2D", run_name, "Wire", "Layer", 'Chamber-7')
            PLOTS.save_1D(dir_path, x_axis, rate_entries_CH7, "Rate", run_name, "Channel", "Rate (Hz)", 'Chamber-7')
            PLOTS.save_2D(dir_path, rate_2d_CH7, "Rate_2D", run_name, "Wire", "Layer", 'Chamber-7')
            images_list = ['Chamber-7_Entries.PNG', 'Chamber-7_Entries_2D.PNG', 'Chamber-7_Rate.PNG', 'Chamber-7_Rate_2D.PNG']
            PLOTS.make_monitor(dir_path, images_list, 'occupancy', 'Chamber-7')
            #save CHAMBER 8
            PLOTS.save_1D(dir_path, x_axis, entries_CH8, "Entries", run_name, "Channel", "Entries", 'Chamber-8')
            PLOTS.save_2D(dir_path, entries_2d_CH8, "Entries_2D", run_name, "Wire", "Layer", 'Chamber-8')
            PLOTS.save_1D(dir_path, x_axis, rate_entries_CH8, "Rate", run_name, "Channel", "Rate (Hz)", 'Chamber-8')
            PLOTS.save_2D(dir_path, rate_2d_CH8, "Rate_2D", run_name, "Wire", "Layer", 'Chamber-8')
            images_list = ['Chamber-8_Entries.PNG', 'Chamber-8_Entries_2D.PNG', 'Chamber-8_Rate.PNG', 'Chamber-8_Rate_2D.PNG']
            PLOTS.make_monitor(dir_path, images_list, 'occupancy', 'Chamber-8')
            print(double_scint_perc)
        
            if scint:
                #save scint CHAMBER 7
                PLOTS.save_1D(dir_path, timebox_xaxis, timebox_entries_CH7, "Cumulative_Timebox", run_name, "TDC units", "Entries", 'Chamber-7', xticks= timebox_ticks)
                PLOTS.save_1D(dir_path, timebox_xaxis, inst_timebox_entries_CH7, "Inst_Timebox",run_name, "TDC units", "Entries", 'Chamber-7', xticks= timebox_ticks)
                PLOTS.save_1D(dir_path, x_axis, scint_entries_CH7, "Scintillator_event_entries", run_name, "Channel", "Entries", 'Chamber-7')
                PLOTS.save_2D(dir_path, scint_entries_2d_CH7, "Scintillator_event_entries_2D", run_name, "Wire", "Layer", 'Chamber-7')
                PLOTS.save_1D(dir_path, x_axis, scint_rate_CH7, "Scintillator_event_rate", run_name, "Channel", "Rate", 'Chamber-7')
                PLOTS.save_2D(dir_path, scint_rate_2d_CH7, "Scintillator_event_rate_2D", run_name, "Wire", "Layer", 'Chamber-7')
                scint_list = ['Chamber-7_Cumulative_Timebox.PNG', "Chamber-7_Scintillator_event_entries.PNG", "Chamber-7_Scintillator_event_entries_2D.PNG",
                                'Chamber-7_Inst_Timebox.PNG', "Chamber-7_Scintillator_event_rate.PNG", "Chamber-7_Scintillator_event_rate_2D.PNG"]
                PLOTS.make_monitor(dir_path, scint_list, 'scintillator', 'Chamber-7')
                #save scint CHAMBER 8
                PLOTS.save_1D(dir_path, timebox_xaxis, timebox_entries_CH8, "Cumulative_Timebox", run_name, "TDC units", "Entries", 'Chamber-8', xticks= timebox_ticks)
                PLOTS.save_1D(dir_path, timebox_xaxis, inst_timebox_entries_CH8, "Inst_Timebox",run_name, "TDC units", "Entries", 'Chamber-8', xticks= timebox_ticks)
                PLOTS.save_1D(dir_path, x_axis, scint_entries_CH8, "Scintillator_event_entries", run_name, "Channel", "Entries", 'Chamber-8')
                PLOTS.save_2D(dir_path, scint_entries_2d_CH8, "Scintillator_event_entries_2D", run_name, "Wire", "Layer", 'Chamber-8')
                PLOTS.save_1D(dir_path, x_axis, scint_rate_CH8, "Scintillator_event_rate", run_name, "Channel", "Rate", 'Chamber-8')
                PLOTS.save_2D(dir_path, scint_rate_2d_CH8, "Scintillator_event_rate_2D", run_name, "Wire", "Layer", 'Chamber-8')
                scint_list = ['Chamber-8_Cumulative_Timebox.PNG', "Chamber-8_Scintillator_event_entries.PNG", "Chamber-8_Scintillator_event_entries_2D.PNG",
                                'Chamber-8_Inst_Timebox.PNG', "Chamber-8_Scintillator_event_rate.PNG", "Chamber-8_Scintillator_event_rate_2D.PNG"]
                PLOTS.make_monitor(dir_path, scint_list, 'scintillator', 'Chamber-8')
                PLOTS.update_monitor(dir_path, monitor, ['Chamber-7_occupancy_monitor.PNG', 'Chamber-8_occupancy_monitor.PNG',  'Chamber-7_scintillator_monitor.PNG', 'Chamber-8_scintillator_monitor.PNG'],
                                     str(rate), str(scint_rate), str(CH7_rate), str(CH8_rate), scint_rate_vs_time, CH7_rate_vs_time, CH8_rate_vs_time, str(double_scint_perc))
            else:
                PLOTS.update_monitor(dir_path, monitor, ['Chamber-7_occupancy_monitor.PNG', 'Chamber-8_occupancy_monitor.PNG'], str(rate), str(scint_rate), str(CH7_rate), str(CH8_rate), scint_rate_vs_time, CH7_rate_vs_time, CH8_rate_vs_time, str(double_scint_perc))
                     
                
except KeyboardInterrupt:
    print ('\nReading stopped.\n') 
    sys.exit()
    f.close()