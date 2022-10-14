import matplotlib.pyplot as plt
import matplotlib.axes
import mne
import numpy as np
from scipy.stats import ttest_rel
import os

# Load raw data
data_path = os.getcwd() +'/data/'

for x in os.walk(data_path):
    subjects = x[1]
    break

for subject in subjects:
    
    subject_idx = subject[7:]
    
    all_ch_data = []
    go_event_start_frames,go_event_end_frames,nogo_event_start_frames,nogo_event_end_frames=[],[],[],[]
    
    for j in range(2):
        bids_fname = (data_path +subject+'/sst/sst_'+subject_idx+'_'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        
        # Set montage
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        
        # Set common average reference
        raw.set_eeg_reference('average', projection=False, verbose=False)
        
        # Apply bandpass filter
        raw.filter(l_freq=0.1, h_freq=None, fir_design='firwin', verbose=False)
        
        events, _ = mne.events_from_annotations(raw, verbose=False)
        
        sfreq = raw.info['sfreq']
        
        go_event_start_frames.append([])
        for event in events:
            if event[2]==10006 or event[2]==10008  :
                go_event_start_frames[j].append(event[0])
                
        go_event_end_frames.append([])
        for event in events:
            if event[2]==10002 or event[2]==10004  :
                go_event_end_frames[j].append(event[0])
                
        nogo_event_start_frames.append([])
        for event in events:
            if event[2]==10007 or event[2]==10009  :
               nogo_event_start_frames[j].append(event[0])
               
        nogo_event_end_frames.append([])
        for event in events:
            if event[2]==10005 or event[2]==10003  :
               nogo_event_end_frames[j].append(event[0])
                
        all_ch_data.append(raw.get_data())
        
    
    save_path = subject+'/start/'
    for path in [save_path+'go',save_path+'nogo',save_path+'both']:
        if not os.path.exists(path):
            curr = 'plots'
            for directory in path.split('/'):
                curr=curr+'/'+ directory
                print(curr)
                if not os.path.exists(curr): os.mkdir(curr)
    
    ch_names = raw.ch_names
    
    for i in range(0,len(ch_names)):
        ch_data = [all_ch_data[j][i] for j in range(2)]
        ch_name = ch_names[i]
        
        time = np.linspace(
            -250*1000/sfreq,
            500*1000/sfreq,
            num =750)
        
        plt.figure(1000*int(subject_idx)+i)
        plt.title('Subject' + subject_idx + ' '+ ch_name + ' (Event Onset)')
        plt.xlabel("Time (ms)")
        plt.ylabel("EEG Signal (V)")
        
        ch_go_events_data = []
        
        for j in range(2):
            start_frame_indices = go_event_start_frames[j]
            end_frame_indices = go_event_end_frames[j]
            for idx in range(len(start_frame_indices)):
                start_frame = start_frame_indices[idx]
                end_frame = end_frame_indices[idx]
                ch_go_events_data.append(ch_data[j][start_frame-250:start_frame+500])
                plt.axvline(x = (-start_frame+end_frame)*1000/sfreq, color = 'b', alpha=0.05)
    
        ch_go_events_data_per_frame = np.array(ch_go_events_data).T
            
        ch_mean_data = []
        max_error = []
        min_error = []
        for frame_data in ch_go_events_data_per_frame:
            mean = np.mean(frame_data)
            std = np.std(frame_data)
            ch_mean_data.append(mean)
            max_error.append(mean+std)
            min_error.append(mean-std)
        
        plt.plot(time,ch_mean_data, color='b')
        plt.fill_between(time, max_error, min_error, color='b', alpha=.1)
        plt.savefig('plots/'+save_path+"go/"+ch_name+".png")
        
        ch_nogo_events_data = []
        for j in range(2):
            start_frame_indices = nogo_event_start_frames[j]
            end_frame_indices = nogo_event_end_frames[j]
            for idx in range(len(start_frame_indices)):
                start_frame = start_frame_indices[idx]
                end_frame = end_frame_indices[idx]
                ch_nogo_events_data.append(ch_data[j][start_frame-250:start_frame+500])
                # plt.axvline(x = (-start_frame+end_frame)*1000/sfreq, color = 'r', alpha=0.05)
            
        ch_nogo_events_data_per_frame = np.array(ch_nogo_events_data).T
            
        ch_mean_data = []
        max_error = []
        min_error = []
        for frame_data in ch_nogo_events_data_per_frame:
            mean = np.mean(frame_data)
            std = np.std(frame_data)
            ch_mean_data.append(mean)
            max_error.append(mean+std)
            min_error.append(mean-std)
       
        # plt.plot(time,ch_mean_data, color='r')
        # plt.fill_between(time, max_error, min_error, color='r', alpha=.1)
        # plt.savefig('plots/'+save_path+"nogo/"+ch_name+".png")
        
        
        # plt.savefig('plots/'+save_path+"both/"+ch_name+".png")
