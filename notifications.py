import matplotlib.pyplot as plt
import mne
import numpy as np
from scipy.stats import sem
import os

# Load raw data
data_path = os.getcwd() +'/data/'

for x in os.walk(data_path):
    subjects = x[1]
    break

for subject in subjects:
    
    subject_idx = subject[7:]
    
    all_ch_data,epochs_list= [],[[],[]]
    
    events_dict = {
    "subject1": {
        "sst1": [229066, 358533, 483000],
        "reading1": [109033],
        "sst2": [237200, 242000, 508800, 669666],
        "reading2": [48600]
    },
    "subject2": {
        "sst1": [185980, 322090, 335900, 438270, 642730],
        "reading1": [65770, 165690],
        "sst2": [220760, 347410, 473550],
        "reading2": [113570, 269540]
    },
    "subject3": {
        "sst1": [194270, 321930, 441670, 585470],
        "reading1": [96930, 171880],
        "sst2": [182280, 207030, 214040, 396620, 549290, 670670],
        "reading2": [65730, 169370, 215580]
    }
}

    
    for j in range(2):
        bids_fname = (data_path +subject+'/sst/sst_'+subject_idx+'_'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        raw.set_eeg_reference('average', projection=False, verbose=False)
        raw.filter(l_freq=0.1, h_freq=30, fir_design='firwin', verbose=False)
        sfreq = raw.info['sfreq']
        
        events_ann, event_dict = mne.events_from_annotations(raw, verbose=False)
        
        # event_start_frames.append([event for event in events if event[2]-10000 in [6,7,8,9]])
        # event_end_frames.append([event for event in events if event[2]-10000 in [2,3,4,5]])
        
        m1 = events_ann[3][0]
        
        events = np.array([np.array([int(event*sfreq/1000+m1),0,10015]) for event in events_dict['subject'+subject_idx]['sst'+str(j+1)]])

        epochs_list[j].append(mne.Epochs(raw,
                    events, None,
                    -1, 1,
                    baseline=(None,0), 
                    preload=True
                   ))
        
    for j in range(2):
        bids_fname = (data_path +subject+'/reading/reading_'+subject_idx+'_'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        raw.set_eeg_reference('average', projection=False, verbose=False)
        raw.filter(l_freq=0.1, h_freq=30, fir_design='firwin', verbose=False)
        sfreq = raw.info['sfreq']
        
        # events, event_dict = mne.events_from_annotations(raw, verbose=False)
        
        # event_start_frames.append([event for event in events if event[2]-10000 in [6,7,8,9]])
        # event_end_frames.append([event for event in events if event[2]-10000 in [2,3,4,5]])

        epochs_list[j].append(mne.Epochs(raw,
                    events, None,
                    -1, 1,
                    baseline=(None,0), 
                    preload=True
                   ))
    for j in range(2):
        epochs_list[j] = mne.concatenate_epochs(epochs_list[j])
        
    evoked = {'first':epochs_list[0].average(),'second':epochs_list[1].average()}
    evoked['first'].comment = 'First'
    evoked['second'].comment = 'Second'
    
    
    ch_names = evoked['first'].ch_names
    
    save_path = 'notifs/'+subject+'/'
    for path in [save_path+'first',save_path+'second',save_path+'both']:
        if not os.path.exists(path):
            curr = 'plots'
            for directory in path.split('/'):
                curr=curr+'/'+ directory
                if not os.path.exists(curr):
                    os.mkdir(curr)
                    print('Created path ' + curr)
    

    
    # f = mne.viz.plot_compare_evokeds(evoked,picks = ['F7','Fz','F8','T8','P8','P7','Pz','O1','Cz','T7'],axes='topo',show=False)
    # f[0].suptitle('Subject' + subject_idx + ' (First Half vs Second Half)',fontsize = 40)
    # f[0].savefig('plots/'+save_path+"both/topo.png",dpi=1000)
    
    f= evoked['first'].plot(spatial_colors=True)
    f.suptitle('Subject' + subject_idx + ' (31 Channels)')
    f.savefig('plots/'+save_path+"first.png",dpi=50)
    f= evoked['second'].plot(spatial_colors=True) 
    f.suptitle('Subject' + subject_idx + ' (31 Channels)')
    f.savefig('plots/'+save_path+"second.png",dpi=50)
    
    for ch in ch_names:
        
        first_sem = sem(epochs_list[0].get_data(picks=[ch])[0:,0])
        ch_first_data = evoked['first'].get_data(picks=[ch])[0]
        second_sem = sem(epochs_list[0].get_data(picks=[ch])[0:,0])
        ch_second_data = evoked['second'].get_data(picks=[ch])[0]
        
        f= evoked['first'].plot(picks=[ch],show=False,time_unit='ms',window_title='Subject' + subject_idx + ' '+ ch + ' (Event Onset)')
        plt.title('Subject' + subject_idx + ' '+ ch)
        plt.axvline(x=0,color='k',linestyle='dashed',linewidth='0.75')
        f.tight_layout()
        f.savefig('plots/'+save_path+"first/"+ch+".png",dpi=50)
        
        f=evoked['second'].plot(picks=[ch],show=False,time_unit='ms',window_title='Subject' + subject_idx + ' '+ ch + ' (Event Onset)')
        plt.title('Subject' + subject_idx + ' '+ ch)
        plt.axvline(x=0,color='k',linestyle='dashed',linewidth='0.75')
        f.tight_layout()
        f.savefig('plots/'+save_path+"second/"+ch+".png",dpi=50)
        
        figs = mne.viz.plot_compare_evokeds(evoked,picks=[ch],show=False,title='Subject' + subject_idx + ' '+ ch + ' (Event Onset)',time_unit='ms',show_sensors='lower left',truncate_xaxis=False,truncate_yaxis=False)
        # mne.viz.plot_compare_evokeds(go_nogo_evoked,picks=[ch],show=False,title='Subject' + subject_idx + ' '+ ch + ' (Event Onset)',time_unit='ms',show_sensors='lower left',truncate_xaxis=False)
        axs = figs[0].axes
        
        time = np.linspace(-500*1000/sfreq,500*1000/sfreq,num =1001)
        
        max_first_error = np.add(ch_first_data,first_sem)*1e6
        min_first_error=np.subtract(ch_first_data,first_sem)*1e6
        axs[0].fill_between(time,max_first_error, min_first_error, color='b', alpha=.1)
        
        max_second_error = np.add(ch_second_data,second_sem)*1e6
        min_second_error=np.subtract(ch_second_data,second_sem)*1e6
        axs[0].fill_between(time,max_second_error, min_second_error, color='r', alpha=.1)
      
        plt.savefig('plots/'+save_path+"both/"+ch+".png",dpi=50)
        
