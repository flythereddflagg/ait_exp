# /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Renames .csv files from old to new naming convention

old: compound_phase_sampSize_temp_date_time.csv
new: compound_phase_date_time_sampSize_temp.csv
'''

import os

indir = os.path.dirname(os.path.realpath(__file__))

for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        if f[-4:] == '.csv':
            parsed = f[:-4].split('_')
            #print parsed
            fp = "%s/%s" %(root,f)
            if len(parsed[-1]) == 4 and len(parsed[-2]) == 6:
                t = parsed.pop()
                dt = parsed.pop()
                parsed.insert(2,t)
                parsed.insert(2,dt)   
                new = '_'.join(parsed) + '.csv'
                print "Changing %s to %s" %(f, new)
                np = "%s/%s" %(root,new)
                os.rename(fp,np)                

