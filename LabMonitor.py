import time, os, sys
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import streamlit as st
import numpy as np

# ------ define drawing function ------
def labMonitor(placeholder, ch, figs, axes,  planes_list, titles, av_rate, rate_, planes_count, list_rate, event_number, elaps_time):
    """
    This function draws the plots and arrange the monitor webpage layout

    Parameters
    ----------
    placeholder : streamlit container
        a container that holds a single element, used to replace same element
        
    ch : list
         X bins of the bar plot
         
    figs: lis of figure
        list of figures in which the subplots are drawn, format [ p0, p1, p2, rate]
        
    ax : AxesSubplot
        list of axes of the subplot in which the function draws, format [ p0, p1, p2, rate]
        
    planes_list : list
        list of histo with the planes entries, format [ p0, p1, p2]
    
    titles : list
        list of titles of the histos, format [ p0, p1, p2]
        
    av_rate : string
        average rate 
        
    rate_ : string
        istantaneous rate
        
    planes_count : list
        list of strings with the total number of entries
        
    list_rate : list
        list with istantaneous rate of 100 previous refresh
        
    event_number : string
        string of the event number

    Returns
    -------
    None.

    """

    xlabel = 'TDC count'
    ylabel = 'Entries'
    xticks = [ i for i in range(0, len(ch)) if i%32 == 0]
    xticks.append( len(ch) )
    xtickslabel = [ str(i*8) for i in range(0, len(ch)) if i%32 == 0 ]
    xtickslabel.append(4095)
        
    axes[0].cla()
    axes[0].set_xlabel(xlabel)
    axes[0].set_xticks(xticks)
    axes[0].set_xticklabels(xtickslabel)
    axes[0].set_ylabel(ylabel)
    axes[0].bar(ch, planes_list[0], width =1, color = '#1f77b4', align ='center')
    axes[0].set_title(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+' ' +titles[0])
    
    axes[1].cla()
    axes[1].set_xlabel(xlabel)
    axes[1].set_xticks(xticks)
    axes[1].set_xticklabels(xtickslabel)
    axes[1].set_ylabel(ylabel)
    axes[1].bar(ch, planes_list[1], width =1, color = '#1f77b4', align ='center')
    axes[1].set_title(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+' ' +titles[1])
    
    axes[2].cla()
    axes[2].set_xlabel(xlabel)
    axes[2].set_xticks(xticks)
    axes[2].set_xticklabels(xtickslabel)
    axes[2].set_ylabel(ylabel)
    axes[2].bar(ch, planes_list[2], width =1, color = '#1f77b4', align ='center')
    axes[2].set_title(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+' ' +titles[2])
    
    axes[3].set_xlabel('# of refresh')
    axes[3].set_ylabel('Rate')
    axes[3].plot( range(0, len(list_rate)), list_rate, color = '#1f77b4')
    
    axes[4].cla()
    axes[4].set_xlabel(xlabel)
    axes[4].set_xticks(xticks)
    axes[4].set_xticklabels(xtickslabel)
    axes[4].set_ylabel(ylabel)
    axes[4].set_yscale('log')
    axes[4].bar(ch, planes_list[0], width =1, color = '#1f77b4', align ='center')
    axes[4].set_title(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+' ' +titles[0])
    
    axes[5].cla()
    axes[5].set_xlabel(xlabel)
    axes[5].set_xticks(xticks)
    axes[5].set_xticklabels(xtickslabel)
    axes[5].set_ylabel(ylabel)
    axes[5].set_yscale('log')
    axes[5].bar(ch, planes_list[1], width =1, color = '#1f77b4', align ='center')
    axes[5].set_title(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+' ' +titles[1])
    
    axes[6].cla()
    axes[6].set_xlabel(xlabel)
    axes[6].set_xticks(xticks)
    axes[6].set_xticklabels(xtickslabel)
    axes[6].set_ylabel(ylabel)
    axes[6].set_yscale('log')
    axes[6].bar(ch, planes_list[2], width =1, color = '#1f77b4', align ='center')
    axes[6].set_title(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+' ' +titles[2])
    
    with placeholder.container():
        #st.title('Laboratory N&SN Physics 2 ')
        rate_col, planes_col0, planes_col1, planes_col2 = st.columns([1, 1, 1, 1])
        with rate_col:
            st.markdown('#### Rate over time ')
            st.pyplot(figs[3])
            st.markdown("### Total n of triggers: " + event_number)
            st.markdown("### Average Rate: "+av_rate+" Hz")
            st.markdown("### Latest "+elaps_time+" s Rate: "+rate_+" Hz")
        with planes_col0:
                st.markdown("#### P1   -   Total count: "+ planes_count[0])
                st.pyplot(figs[0])
                st.markdown("#### P1   -   Log scale")
                st.pyplot(figs[4])
        with planes_col1:
                st.markdown("#### P2   -   Total count: "+ planes_count[1])
                st.pyplot(figs[1])
                st.markdown("#### P2   -   Log scale")
                st.pyplot(figs[5])
        with planes_col2:
                st.markdown("#### P3   -   Total count: "+ planes_count[2])
                st.pyplot(figs[2])
                st.markdown("#### P3   -   Log scale")
                st.pyplot(figs[6])
                
    plt.close('all')


# ------ set up webpage ------
st.set_page_config(
    page_title="Monitor",
    page_icon='	:stars:',
    layout="wide",
)
monitor = st.empty()

refresh_time = 5       # seconds

# ------ find valid file to read ------
if len(sys.argv) > 1:
    file_name = './'+sys.argv[1]
    if not os.path.exists(file_name):
        print('This file does not exist! Select the data file', flush=True)
        Tk().withdraw()
        file_name = askopenfilename()
else:
    print('Select the data file', flush=True)
    Tk().withdraw()
    file_name = askopenfilename()    
        
f = open(file_name, 'r')
print(datetime.now().strftime("%Y/%m/%d - %H:%M:%S")+ ' Reading ' + file_name )


fig0, ax0 = plt.subplots(1, 1, figsize = (15, 10))
fig1, ax1 = plt.subplots(1, 1, figsize = (15, 10))
fig2, ax2 = plt.subplots(1, 1, figsize = (15, 10))
fig0_log, ax0_log = plt.subplots(1, 1, figsize = (15, 10))
fig1_log, ax1_log = plt.subplots(1, 1, figsize = (15, 10))
fig2_log, ax2_log = plt.subplots(1, 1, figsize = (15, 10))
fig3, ax3 = plt.subplots(1, 1, figsize = (15, 10))

figures = np.array([fig0, fig1, fig2, fig3, fig0_log, fig1_log, fig2_log])
axis = np.array([ax0, ax1, ax2, ax3, ax0_log, ax1_log, ax2_log])

# ------ number of event per plane ------
planes_events = np.zeros(3)#[0]*3

bins = 256
# ------ time histograms ------
hist_p0 = np.zeros(bins)#[0]*bins
hist_p1 = np.zeros(bins)#[0]*bins
hist_p2 = np.zeros(bins)#[0]*bins

x_axis = range(bins)

# ------ rate ------
average_rate = 0
inst_rate = 0
rate_info = [[.0, .0, .0]]          # [n evento, tempo, rate]
rate_over_time = [0]
add_point = [.0, .0, .0]

try:
    
    while( True ):        
        # try to read a line
        where = f.tell()
        time.sleep(refresh_time)
        line = f.readlines()

        # if reading fails, sleep 5s and set pointer back before the failed reading
        if not line:
            print('No new lines to be read.')
            # print(time.time() - os.path.getmtime(filename))
            if time.time() - os.path.getmtime(file_name) > 120 :
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
                        
            for i in range(0, len(line)): 
                #convert to decimal
                p0_value = int ( line[i].split(' ')[3] , 16) 
                p1_value = int ( line[i].split(' ')[4] , 16)
                p2_value = int ( line[i].split(' ')[5] , 16)
                
                #fill the histos - istogramma con sottomultiplo di 4096-> uso il valore/ n come indice
                if p0_value != 4095:
                    hist_p0[int(np.floor(p0_value/16))] +=1
                if p1_value != 4095:    
                    hist_p1[int(np.floor(p1_value/16))] +=1
                if p2_value != 4095:    
                    hist_p2[int(np.floor(p2_value/16))] +=1


            #compute rate           
            average_rate = round ( int(line[len(line)-1].split(' ')[1]) / float(line[len(line)-1].split(' ')[2]) , 2)
            elapsed_time = round ( float(line[len(line)-1].split(' ')[2]) - rate_info[0][1] , 2)
            
            if  len(rate_info)>1 and ( len(rate_info) > 19 or elapsed_time > 110 ):
                rate_info.pop(0)
                rate_info.append( [int(line[len(line)-1].split(' ')[1]),  float(line[len(line)-1].split(' ')[2]), elapsed_time  ] )
            else: 
                rate_info.append( [int(line[len(line)-1].split(' ')[1]),  float(line[len(line)-1].split(' ')[2]), elapsed_time  ] )
            
            elapsed_time = round ( float(line[len(line)-1].split(' ')[2]) - rate_info[0][1] , 2)
            inst_rate = round ( ( int(line[len(line)-1].split(' ')[1]) - rate_info[0][0] )/ elapsed_time , 2)                    
            if not (add_point in rate_info):
                rate_over_time.append(inst_rate)
                add_point = rate_info[(len(rate_info) -1)]
 
            labMonitor(monitor, x_axis, figures, axis, [hist_p0, hist_p1, hist_p2], ['P1', 'P2', 'P3'], str(average_rate), str(inst_rate), [str(int(sum(hist_p0))), str(int(sum(hist_p1))), str(int(sum(hist_p2)))], rate_over_time, line[len(line)-1].split(' ')[1], str(rate_info[len(rate_info)-1][2]))        
                
except KeyboardInterrupt:
    print ('\nReading stopped.\n') 
    sys.exit()
    f.close()