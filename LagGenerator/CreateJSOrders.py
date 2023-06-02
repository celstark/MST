# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 17:14:56 2019

@author: craig

Lifting code from MST_Copt_PsychoPy.py to load the order files, do the 
randomization (exactly as in that code) and write out a version that can
be readily loaded into the jsPsych version.


"""

import numpy as np
import os, csv

NImagePairs = 192  # Number of image pairs

def check_files(SetName):
    """ 
    SetName should be something like "C" or "1"
    Checks to make sure there are the right #of images in the image directory
    Loads the lure bin ratings into the global set_bins list and returns this
    """
    import glob
    import os

    #print(SetName)
    #print(P_N_STIM_PER_LIST)

    
    bins = []  # Clear out any existing items in the bin list
    
    # Load the bin file
    with open("Set"+str(SetName)+" bins.txt","r") as bin_file:
        reader=csv.reader(bin_file,delimiter='\t')
        for row in reader:
            if int(row[0]) > NImagePairs:
                raise ValueError('Stimulus number ({0}) too large - not in 1-192 in binfile'.format(row[0]))
            if int(row[0]) < 1:
                raise ValueError('Stimulus number ({0}) too small - not in 1-192 in binfile'.format(row[0]))
            bins.append(int(row[1]))
    if len(bins) != NImagePairs:
        raise ValueError('Did not read correct number of bins in binfile')
    
    return bins

def load_and_decode_order(repeat_list,lure_list,foil_list,
                          lag_set='Copt_4-30_orders',order=1,base_dir='.',
                          stim_set='1'):
    """
    Loads the order text file and decodes this into a list of image names, 
     conditions, lags, etc.
    
    lag_set: Directory name with the order files
    order: Which order file to use (numeric index)
    base_dir: Directory that holds the set of lag sets
    stim_set = Set we're using (e.g., '1', or 'C')
    repeat_list,lure_list,foil_list: Lists (np.arrays actually) created by setup_list_permuted
    

    In the order files files we have 2 columns:
        1st column is the stimulus type + number:
        Offset_1R = 0; % 1-100 1st of repeat pair
        Offset_2R = 100; % 101-200  2nd of repeat pair
        Offset_1L = 200; % 201-300 1st of lure pair
        Offset_2L = 300; % 301-400 2nd of lure pair
        Offset_Foil = 400; % 401+ Foil
        
        2nd column is the lag + 500 (-1 for 1st and foil)

    Returns:
        lists / arrays that are all N-trials long
        
        type_code: 0=1st of repeat
                   1=2nd of repeat
                   2=1st of lure
                   3=2nd of lure
                   4=foil
        ideal_resp: 0=old
                    1=similar
                    2=new
        lag: Lag for this item (-1=1st/foil, 0=adjacent, N=items between)
        fnames: Actual filename of image to be shown
    """
    fname=base_dir + os.sep + lag_set + os.sep + "order_{0}.txt".format(order)
    fdata=np.genfromtxt(fname,dtype=int,delimiter=',')
    
    lag = fdata[:,1]
    lag[lag != -1] = lag[lag != -1] - 500
    
    type_code = fdata[:,0]//100  #Note, this works b/c we loaded the data as ints
    
    stim_index = fdata[:,0]-100*type_code
    
    ideal_resp = np.zeros_like(stim_index)
    ideal_resp[type_code==4]=2
    ideal_resp[type_code==0]=2
    ideal_resp[type_code==2]=2
    ideal_resp[type_code==1]=0
    ideal_resp[type_code==3]=1
    
    fnames=[]
#    dirname='Set {0}{1}'.format(stim_set, os.sep)  # Get us to the directory
    dirname='Set {0}_rs/'.format(stim_set)  # Get us to the directory
    for i in range(len(type_code)):
        stimfile='UNKNOWN'
        if type_code[i]==0 or type_code[i]==1:
            stimfile='{0:03}a.jpg'.format(repeat_list[stim_index[i]])
        elif type_code[i]==2:
            stimfile='{0:03}a.jpg'.format(lure_list[stim_index[i]])
        elif type_code[i]==3:
            stimfile='{0:03}b.jpg'.format(lure_list[stim_index[i]])
        elif type_code[i]==4:
            stimfile='{0:03}a.jpg'.format(foil_list[stim_index[i]])
        fnames.append(dirname+stimfile)
    
    return (type_code,ideal_resp,lag,fnames)
    
    
def setup_list_permuted(set_bins):
    """
    set_bins = list of bin values for each of the 192 stimuli -- set specific
    
    Assumes check_files() has been run so we have the bin numbers for each stimulus

    Returns lists with the image numbers for each stimulus type (study, repeat...)
    in the to-be-used permuted order. Full 64 given for all.  This will get
    cut down and randomized in create_order()

    """

    
    if len(set_bins) != NImagePairs:
        raise ValueError('Set bin length is not the same as the stimulus set length (192)')

    
    # Figure the image numbers for the lure bins
    lure1=np.where(set_bins == 1)[0] + 1
    lure2=np.where(set_bins == 2)[0] + 1
    lure3=np.where(set_bins == 3)[0] + 1
    lure4=np.where(set_bins == 4)[0] + 1
    lure5=np.where(set_bins == 5)[0] + 1
    
    # Permute these
    lure1 = np.random.permutation(lure1)
    lure2 = np.random.permutation(lure2)
    lure3 = np.random.permutation(lure3)
    lure4 = np.random.permutation(lure4)
    lure5 = np.random.permutation(lure5)
    
    lures = np.empty(NImagePairs//3,dtype=int)
    # # Make the Lure list to go L1, 2, 3, 4, 5, 1, 2 ... -- 64 total of them (max)
    # lure_count = np.zeros(5,dtype=int)
    # nonlures = np.arange(1,NImagePairs+1,dtype=int)
    # for i in range(NImagePairs//3):  
    #     if i % 5 == 0:
    #         lures[i]=lure1[lure_count[0]]
    #         lure_count[0]+=1
    #     elif i % 5 == 1:
    #         lures[i]=lure2[lure_count[1]]
    #         lure_count[1]+=1
    #     elif i % 5 == 2:
    #         lures[i]=lure3[lure_count[2]]
    #         lure_count[2]+=1
    #     elif i % 5 == 3:
    #         lures[i]=lure4[lure_count[3]]
    #         lure_count[3]+=1
    #     elif i % 5 == 4:
    #         lures[i]=lure5[lure_count[4]]
    #         lure_count[4]+=1
    #     nonlures=np.delete(nonlures,np.argwhere(nonlures == lures[i]))

    # Given that we look at *all* pairs first, we can be certain we have >64 items
    # across bins 3-5.  So, just fill up 64 of them with these going 3,4,5,3,4,5,...
    # Our repeat pairs will have ones that would have been more L1-2-ish
    lure_count = np.zeros(5,dtype=int)
    nonlures = np.arange(1,NImagePairs+1,dtype=int)
    for i in np.arange(NImagePairs//3):  
        if i % 3 == 0:
            lures[i]=lure3[lure_count[2]]
            lure_count[2]+=1
        elif i % 3 == 1:
            lures[i]=lure4[lure_count[3]]
            lure_count[3]+=1
        elif i % 3 == 2:
            lures[i]=lure5[lure_count[4]]
            lure_count[4]+=1
        nonlures=np.delete(nonlures,np.argwhere(nonlures == lures[i]))



    # Randomize the non-lures and split into 64-length repeat and foils
    nonlures=np.random.permutation(nonlures)
    foils = nonlures[0:NImagePairs//3]
    repeats = nonlures[NImagePairs//3:2*NImagePairs//3]
           
    # At this point, we're full 64-item length lists for everything
    # break this down into the right size
    #repeatstim=repeats[0:set_size]
    #lurestim=lures[0:set_size]
    #foilstim=foils[0:set_size]
    
    # Our lures are still in L1, 2, 3, 4, 5, 1, 2, ... order -- fix that
    #lurestim=np.random.permutation(lurestim)
            
    
    return (repeats,lures,foils)

def CreateJSFile(lag_set='Copt_4-30_orders', stim_set='1', order=1, nruns=20):
    set_bins = np.array(check_files(stim_set))
    # Figure out which stimuli will be shown in which conditions and order them
    print('Ordering...')
    (repeat_list, lure_list, foil_list) = setup_list_permuted(set_bins)
    
    # Load up the order file and decode it, creating all the needed vectors
    (type_code,ideal_resp,lag,fnames)=load_and_decode_order(repeat_list,
            lure_list,foil_list,lag_set=lag_set,
            order=order, stim_set=stim_set)
    for run in range(nruns):
        outname='jsOrders{0}{1}_{2}_{3}_{4}.js'.format(os.sep,lag_set,stim_set,order,run+1) 
        fp=open(outname,'w')
        fp.write('var trial_stim=[\n')
        for i in np.arange(len(type_code)):
            fp.write('  {' + "trial: {0}, image: '{1}', type: {2}, correct_resp: {3}, lag: {4}".format(
                    i,fnames[i],type_code[i],ideal_resp[i],lag[i]) +'}')
            if i < (len(type_code)-1):
                fp.write(',\n')
            else:
                fp.write('\n')
        fp.write(']\n')
        fp.close()

def UberCreate():
    for sset in np.arange(1,7):
        for order in np.arange(1,13):
            CreateJSFile(lag_set='Copt_4-30_orders', stim_set=str(sset), order=order, nruns=20)
            CreateJSFile(lag_set='Copt_2-30_orders', stim_set=str(sset), order=order, nruns=20)
    