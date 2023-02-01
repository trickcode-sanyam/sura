import matplotlib.pyplot as plt
import mne
import numpy as np
from scipy.stats import sem
import os

# Load raw data
data_path = os.getcwd() +'/data_with_ica/'

for x in os.walk(data_path):
    subjects = x[1]
    break

events_dict = {"subject1":{
	"sst1":[229066, 358533, 483000],
	"reading1":[109033],
	"sst2":[237200, 242000, 508800, 669666],
	"reading2": [48600]
},
"subject2":{
	"sst1":[185980, 322090, 335900, 438270, 642730],
	"reading1":[65770, 165690],
	"sst2":[220760, 347410, 473550],
	"reading2":[113570, 269540]
},
"subject3":{
	"sst1":[194270, 321930, 441670, 585470],
	"reading1":[96930, 171880],
	"sst2":[182280, 207030, 214040, 396620, 549290, 670670],
	"reading2":[65730, 169370, 215580]
},
"subject4":{
	"sst1":[139000, 218300, 315600, 367900, 431600, 526800, 658700],
	"reading1":[50100, 123500, 195400, 260300],
	"sst2":[103700, 198500, 240100, 372500, 507200, 530900, 553900, 601400, 608600, 643700],
	"reading2":[20600, 107300, 186200, 301400]
},
"subject8":{
	"sst1":[201300, 399800, 486700, 690400],
	"reading1":[155300, 215500, 292300, 343800],
	"sst2":[175000, 384400, 468700, 531200, 609200],
	"reading2":[53800, 12200, 231500, 350700]
},
"subject9":{
	"sst1":[197800, 358100, 603600, 724300],
	"reading1":[58600, 109600, 23900],
	"sst2":[15100, 125400, 202900, 288600, 345600, 409700, 564500],
	"reading2":[116300, 136500, 184100, 198600]
},
"subject10":{
	"sst1":[187500, 285200, 414600, 595600, 664700],
	"reading1":[72500, 201600, 258200],
	"sst2":[152800, 218200, 290000, 465900, 667600],
	"reading2":[100800, 188800, 252400, 431400]
}
}

all_notif_epochs =[]
for subject in subjects:
    
    subject_idx = subject[7:]
    
    all_ch_data,epochs_list= [],[[],[]]
    

    
    for j in range(2):
        bids_fname = (data_path +subject+'/sub'+subject_idx+'_sst'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        raw.set_eeg_reference('average', projection=False, verbose=False)
        raw.filter(l_freq=0.1, h_freq=30, fir_design='firwin', verbose=False)
        sfreq = raw.info['sfreq']
        
        events_ann, event_dict = mne.events_from_annotations(raw, verbose=False)
        
        m1 = events_ann[3][0]
        
        events = np.array([np.array([int(event*sfreq/1000+m1),0,10015]) for event in events_dict['subject'+subject_idx]['sst'+str(j+1)]])

        epochs_list[j].append(mne.Epochs(raw,
                    events, None,
                    -1, 1,
                    baseline=(None,0), 
                    preload=True
                   ))
        
    for j in range(2):
        bids_fname = (data_path +subject+'/sub'+subject_idx+'_reading'+str(j+1)+'.vhdr')
        raw = mne.io.read_raw_brainvision(bids_fname, preload=True, verbose=False)
        raw.info['line_freq'] = 50.
        montage = mne.channels.make_standard_montage('easycap-M1')
        raw.set_montage(montage, verbose=False)
        # raw.set_eeg_reference('average', projection=False, verbose=False)
        # raw.filter(l_freq=0.1, h_freq=30, fir_design='firwin', verbose=False)
        sfreq = raw.info['sfreq']
    
        epochs_list[j].append(mne.Epochs(raw,
                    events, None,
                    -1, 1,
                    baseline=(None,0), 
                    preload=True
                   ))
    for j in range(2):
        epochs_list[j] = mne.concatenate_epochs(epochs_list[j])
        
    notif_epochs = mne.concatenate_epochs(epochs_list)
    all_notif_epochs.append(notif_epochs)
    notif_evoked = notif_epochs.average()
    
    ch_names = notif_evoked.ch_names
    
    save_path = 'notifs/'+subject+'/'
    if not os.path.exists(save_path):
        curr = 'plots'
        for directory in save_path.split('/'):
            curr=curr+'/'+ directory
            if not os.path.exists(curr):
                os.mkdir(curr)
                print('Created path ' + curr)
    

    
    f = mne.viz.plot_compare_evokeds(notif_evoked,picks = ['F7','Fz','F8','T8','P8','P7','Pz','O1','Cz','T7'],axes='topo',show=False)
    f[0].suptitle('Subject' + subject_idx + ' Notifications',fontsize = 40)
    f[0].savefig('plots/'+save_path+"topo.png",dpi=250)
    
    f= notif_evoked.plot(spatial_colors=True)
    # f.suptitle('Subject' + subject_idx + ' (31 Channels)')
    f.savefig('plots/'+save_path+"all.png",dpi=250)
    
    for ch in ch_names:
        
        ch_sem = sem(notif_epochs.get_data(picks=[ch])[0:,0])
        ch_data = notif_evoked.get_data(picks=[ch])[0]
        
        figs = mne.viz.plot_compare_evokeds(notif_evoked,picks=[ch],show=False,title='Subject' + subject_idx + ' '+ ch + ' (Event Onset)',time_unit='ms',show_sensors='lower left',truncate_xaxis=False,truncate_yaxis=False, legend=False)
        axs = figs[0].axes
        
        time = np.linspace(-1000,1000,num =int(sfreq*2+1))
        
        max_first_error = np.add(ch_data,ch_sem)*1e6
        min_first_error=np.subtract(ch_data,ch_sem)*1e6
        axs[0].fill_between(time,max_first_error, min_first_error, color='b', alpha=.1)
       
      
        plt.savefig('plots/'+save_path+ch+".png",dpi=250)
        