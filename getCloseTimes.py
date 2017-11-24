#!/usr/bin/env dls-python
"""
Created on 21 Nov 2017

@author: ig43

Application to derive device max close times by reading PLC register blocks via EPICS PVs
then extracting the register(s) that report the device max close time.

"""

import os
from pkg_resources import require

require("cothread")
import cothread
import cothread.catools
from numpy import *
import json


def print_value(value):
    print value.name, value


if __name__ == "__main__":
    # May not need this - but hey...
    os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '1000000'

    # Load the file which defines all the devices we are interested in
    # their relevant D register and scaling factors.
    # This is performed via json.load() so that the local 'data' variable
    # becomes a JSON representation of the file JSON content.
    with open('maxclosetime.json') as json_file:
        data = json.load(json_file)

    # Iterate through the JSON defined devices and extract info for each one
    for p in data['devices']:
        device = p['device']

        # It seems that strings from json.load() are returned as unicode
        # so we need to convert them to standard ascii.
        pv = (p['DMPV']).encode('ascii', 'ignore')
        idx = p['index']
        scale = 1.0
        if "scale" in p:
            scale = p['scale']
        # print('Device: ' + device)
        # print('DM PV: ' + pv)
        # print('Index: ', idx)
        val = None
        ct = None
        try:
            # Do an EPICS channel access caget to return the PV value.
            # The PLC D register block is returned as type ca_array and needs
            # converting to standard Python list type.
            val = cothread.catools.caget(pv)
            registers = val.tolist()
            ct = registers[idx]*scale
            print("Max Close time for {0:s} is {1:0.2f} seconds".format(device, ct))
        except cothread.catools.ca_nothing:
            # Something went wrong - just flag it to the user.
            print"Didn't work for {0:s} :".format(device)
        # print ("registers = {0!r}".format(registers))

    # Don't need waitForQuit() here, as all the data retrieval is synchronous.
    # WaitForQuit()
