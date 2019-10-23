import os
import random
import math
import numpy
import time

from typing import Dict



class TestData:

    class ItemParams:
        def __init__(self, name, sigma_install, value_install, sigma_uninstall, value_uninstall):
            self.name = name
            self.sigma_install = sigma_install
            self.value_install = value_install
            self.sigma_uninstall = sigma_uninstall
            self.value_uninstall = value_uninstall

        def should_install(self):
            v = numpy.random.normal(0.0, self.sigma_install)
            return  v < self.value_install

        def should_uninstall(self):
            return numpy.random.normal(0.0, self.sigma_uninstall) < self.value_uninstall



    def __init__(self):

        dataFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculated_data.txt")

        self.all_items = {} # type: Dict[str, TestData.ItemParams]

        with open(dataFile, "r") as fp:
            lines = fp.readlines()

            for l in lines:
                parts = l.rstrip().split("\t")
                name = parts[0]
                sigma_install = float(parts[1])
                sigma_uninstall = float(parts[2])
                #sigma_install = 0.2
                #sigma_uninstall = 0.2
                value_install = float(parts[3])
                value_uninstall = float(parts[4])

                self.all_items[name] = TestData.ItemParams(name, sigma_install, value_install, sigma_uninstall , value_uninstall)


    def change_apps(self, cur_apps):
        cur_apps = set(cur_apps)
        new_apps = []
        for k,v in self.all_items.items():
            if k in cur_apps:
                continue
            if v.should_install():
                new_apps.append(v.name)

        num_uninstall = 0
        for app in cur_apps:
            if not self.all_items[app].should_uninstall():
                new_apps.append(app)
            else:
                num_uninstall+=1
        print("num_uninstalled = {}".format(num_uninstall))
        return new_apps






