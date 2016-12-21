# Convert pickle .dat files to readable .csv files

import pickle
import csv
import sys

if len(sys.argv) != 3:
    sys.exit('Correct usage: python converter.py input_file.dat output_file.csv')


input_file = sys.argv[1] #'relax.dat'
output_filename = sys.argv[2] #'test.csv'
recording = pickle.load(open(input_file, 'rb'))

# open the output file for writing
with open(output_filename, 'wb') as fp:

    # create csv writer object with standard delimiter
    a = csv.writer(fp, delimiter=',')

    # create header row for column names
    header = ['frame', 'time']
    electrode_list = ['FC3', 'FCZ', 'FC4', 'CP3', 'CPZ', 'CP4', 'PO7', 'PO3', 'POZ', 'PO4', 'PO8', 'POZ', 'O1', 'O2']

    header = header + electrode_list

    a.writerow(header)

    # iterate over the recorded frames, generating rows
    for frame in range(1, len(recording['times'])):
        for sample in range(0, len(recording['times'][frame])):
            row_entry = [frame, recording['times'][frame][sample]]

            for electrode in range(0, len(electrode_list)):
                row_entry.append(recording[frame][electrode][sample])

            a.writerow(row_entry)