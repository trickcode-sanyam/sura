import matplotlib.pyplot as plt
import matplotlib.axes
import mne
import numpy as np
from scipy.stats import sem
import os

# Load raw data
data_path = os.getcwd() +'/data_with_ica/'

for x in os.walk(data_path):
    subjects = x[1]
    print('Sub List', subjects)
    break

epochs_list =[[],[]]

for subject in subjects:
    
    subject_idx = subject[7:]
    
    print(subject)
    all_ch_data= []
    event_start_frames=[]
    
    for j in range(2):
        bids_fname = (data_path +subject+'/sub'+subject_idx+'_sst'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        # raw.set_eeg_reference('average', projection=False, verbose=False)
        # raw.filter(l_freq=0.1, h_freq=30, fir_design='firwin', verbose=False)
        # psd_plot = raw.plot_psd(fmax=100)
        psd_fig = mne.viz.plot_raw_psd(raw,fmax=100,show=False)
        plt.title(subject)
        plt.show()
        # raw.compute_psd().plot()
        
        sfreq = raw.info['sfreq']
        if sfreq!=250:
            raw_new = raw.copy()
            raw_new.resample(250)
            raw = raw_new
        
        
        events, event_dict = mne.events_from_annotations(raw, verbose=False)
        
        event_start_frames.append([event for event in events if event[2]-10000 in [6,7,8,9]])

        epochs = mne.Epochs(raw,
                    event_start_frames[j], None,
                    -0.5, 1,
                    baseline=(None,0), 
                    preload=True
                   )

        epochs_list[j].append(epochs)

for j in range (2):
    epochs_list[j] = mne.concatenate_epochs(epochs_list[j])

evoked = {'first':epochs_list[0].average(),'second':epochs_list[1].average()}
evoked['first'].comment = 'First'
evoked['second'].comment = 'Second'
    
    
ch_names = evoked['first'].ch_names
    

f = mne.viz.plot_compare_evokeds(evoked,picks = ['F7','F8','O1','O2','Pz','FC5','FC6','CP1','CP2','Cz','Fz'],axes='topo',show=False)
f[0].suptitle('First Half vs Second Half',fontsize = 40)
f[0].savefig('plots/halves/topo.png',dpi=200)


for ch in ch_names:
    
    first_sem = sem(epochs_list[0].get_data(picks=[ch])[0:,0])
    ch_first_data = evoked['first'].get_data(picks=[ch])[0]
    second_sem = sem(epochs_list[1].get_data(picks=[ch])[0:,0])
    ch_second_data = evoked['second'].get_data(picks=[ch])[0]

    
    
    figs = mne.viz.plot_compare_evokeds(evoked,picks=[ch],show=False,title=ch+ ' Event Onset',time_unit='ms',show_sensors='lower left',truncate_xaxis=False,truncate_yaxis=False)
    # mne.viz.plot_compare_evokeds(go_nogo_evoked,picks=[ch],show=False,title='Subject' + subject_idx + ' '+ ch + ' (Event Onset)',time_unit='ms',show_sensors='lower left',truncate_xaxis=False)
    axs = figs[0].axes
    
    time = np.linspace(-0.5*1000,1*1000,num =376)
    
    max_first_error = np.add(ch_first_data,first_sem)*1e6
    min_first_error=np.subtract(ch_first_data,first_sem)*1e6
    axs[0].fill_between(time,max_first_error, min_first_error, color='b', alpha=.1)
    
    max_second_error = np.add(ch_second_data,second_sem)*1e6
    min_second_error=np.subtract(ch_second_data,second_sem)*1e6
    axs[0].fill_between(time,max_second_error, min_second_error, color='r', alpha=.1)
    
        
    plt.savefig('plots/halves/'+ch+".png",dpi=200)
    
plt.show()
        
        
        

