import json
import csv

with open("eras_fam_med.json") as jf:
    data = json.load(jf)

cf = open("eras_fam_med.csv", "w")

cw = csv.writer(cf)
count = 0
for d in data:
    if count == 0:
        # Writing headers of CSV file
        header = d.keys()
        cw.writerow(header)
        count += 1

    # Writing data of CSV file
    cw.writerow(d.values())

cf.close()