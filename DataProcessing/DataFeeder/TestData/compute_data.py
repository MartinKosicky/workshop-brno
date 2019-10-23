
import os
import numpy
import random

fname = os.path.join(os.path.dirname(__file__), "default_data.txt")
new_fname = os.path.join(os.path.dirname(__file__), "calculated_data.txt")

items = []

with open(fname,"r") as fp:
    with open(new_fname, "w") as out_fp:
        lines = fp.readlines()
        for l in lines:
            name = l.rstrip().replace("\t"," ")
            sigma_install = 0.2
            sigma_uninstall = 0.2
            value_install = random.random() * 0.2 - 0.55
            value_uninstall = 0.5 - random.random() * 0.4
            out_fp.write(f"{name}\t{sigma_install}\t{sigma_uninstall}\t{value_install}\t{value_uninstall}\n")






