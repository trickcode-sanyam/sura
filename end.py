import matplotlib.pyplot as plt
import matplotlib.axes
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
    
    all_ch_data,go_epochs_list,nogo_epochs_list= [],[],[]
    go_event_start_frames,go_event_end_frames,nogo_event_start_frames,nogo_event_end_frames=[],[],[],[]
    
    for j in range(2):
        bids_fname = (data_path +subject+'/sst/sst_'+subject_idx+'_'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        raw.set_eeg_reference('average', projection=False, verbose=False)
        raw.filter(l_freq=0.1, h_freq=30, fir_design='firwin', verbose=False)
        sfreq = raw.info['sfreq']
        
        events, event_dict = mne.events_from_annotations(raw, verbose=False)
        
        go_event_start_frames.append([event for event in events if event[2]==10006 or event[2]==10008])
        go_event_end_frames.append([event for event in events if event[2]==10002 or event[2]==10004])

        nogo_event_start_frames.append([event for event in events if event[2]==10009 or event[2]==10007])
        nogo_event_end_frames.append([event for event in events if event[2]==10005 or event[2]==10003])


        go_epochs_list.append(mne.Epochs(raw,
                    go_event_end_frames[j], None,
                    -1, 0.5,
                    baseline=(None,0), 
                    preload=True
                   ))
        
        nogo_epochs_list.append(mne.Epochs(raw,
                    nogo_event_end_frames[j], None,
                    -1, 0.5,
                    baseline=(None,0), 
                    preload=True
                   ))
        
    go_epochs=mne.concatenate_epochs(go_epochs_list)
    nogo_epochs=mne.concatenate_epochs(nogo_epochs_list)
    
    go_evoked = go_epochs.average()
    nogo_evoked=nogo_epochs.average()
    
    go_response_frame_diff = np.subtract(go_event_end_frames,go_event_start_frames)
    nogo_response_frame_diff = np.subtract(nogo_event_end_frames,nogo_event_start_frames)
    
    ch_names = go_evoked.ch_names
    
    save_path = subject+'/end/'
    for path in [save_path+'go',save_path+'nogo',save_path+'both']:
        if not os.path.exists(path):
            curr = 'plots'
            for directory in path.split('/'):
                curr=curr+'/'+ directory
                if not os.path.exists(curr):
                    os.mkdir(curr)
                    print('Created path ' + curr)
    
    go_evoked.comment = "Go"
    nogo_evoked.comment="NoGo"
    go_nogo_evoked = [go_evoked,nogo_evoked]
    
    f = mne.viz.plot_compare_evokeds(go_nogo_evoked,picks = ['F7','Fz','F8','T8','P8','P7','Pz','O1','Cz','T7'],axes='topo',show=False)
    f[0].suptitle('Subject' + subject_idx + ' (Event End)',fontsize = 40)
    f[0].set_dpi(1000)
    f[0].savefig('plots/'+save_path+"both/topo.png",dpi=200)
    
    
    # for ch in ch_names:
        
    #     go_sem = sem(go_epochs.get_data(picks=[ch])[0:,0])
    #     ch_go_data = go_evoked.get_data(picks=[ch])[0]
    #     nogo_sem = sem(nogo_epochs.get_data(picks=[ch])[0:,0])
    #     ch_nogo_data = nogo_evoked.get_data(picks=[ch])[0]
        
    #     f= go_evoked.plot(picks=[ch],show=False,time_unit='ms',window_title='Subject' + subject_idx + ' '+ ch + ' (Event End)')
    #     plt.title('Subject' + subject_idx + ' '+ ch + ' (Go Event End)')
    #     plt.axvline(x=0,color='k',linestyle='dashed',linewidth='0.75')
    #     for frame_diff in go_response_frame_diff[0:,0:,0].flatten():
    #         plt.axvline(x = frame_diff*-1000/sfreq, color = 'b', alpha=0.02)
    #     f.tight_layout()
    #     f.savefig('plots/'+save_path+"go/"+ch+".png",dpi=800)
        
    #     f=nogo_evoked.plot(picks=[ch],show=False,time_unit='ms',window_title='Subject' + subject_idx + ' '+ ch + ' (Event End)')
    #     plt.title('Subject' + subject_idx + ' '+ ch + ' (NoGo Event End)')
    #     plt.axvline(x=0,color='k',linestyle='dashed',linewidth='0.75')
    #     for frame_diff in nogo_response_frame_diff[0:,0:,0].flatten():
    #         plt.axvline(x = frame_diff*-1000/sfreq, color = 'r', alpha=0.02)
    #     f.tight_layout()
    #     f.savefig('plots/'+save_path+"nogo/"+ch+".png",dpi=800)
        
        
    #     figs = mne.viz.plot_compare_evokeds(go_nogo_evoked,picks=[ch],show=False,title='Subject' + subject_idx + ' '+ ch + ' (Event End)',time_unit='ms',show_sensors='lower left',truncate_xaxis=False,truncate_yaxis=False)
    #     # mne.viz.plot_compare_evokeds(go_nogo_evoked,picks=[ch],show=False,title='Subject' + subject_idx + ' '+ ch + ' (Event End)',time_unit='ms',show_sensors='lower left',truncate_xaxis=False)
    #     axs = figs[0].axes
        
    #     time = np.linspace(-500*1000/sfreq,250*1000/sfreq,num =751)
        
    #     max_go_error = np.add(ch_go_data,go_sem)*1e6
    #     min_go_error=np.subtract(ch_go_data,go_sem)*1e6
    #     axs[0].fill_between(time,max_go_error, min_go_error, color='b', alpha=.1)
        
    #     max_nogo_error = np.add(ch_nogo_data,nogo_sem)*1e6
    #     min_nogo_error=np.subtract(ch_nogo_data,nogo_sem)*1e6
    #     axs[0].fill_between(time,max_nogo_error, min_nogo_error, color='r', alpha=.1)
        
    #     for frame_diff in nogo_response_frame_diff[0:,0:,0].flatten():
    #         axs[0].axvline(x = frame_diff*-1000/sfreq, color = 'r', alpha=0.02)
    #     for frame_diff in go_response_frame_diff[0:,0:,0].flatten():
    #         axs[0].axvline(x = frame_diff*-1000/sfreq, color = 'b', alpha=0.02)
            
    #     plt.savefig('plots/'+save_path+"both/"+ch+".png",dpi=800)
        

        
