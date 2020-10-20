import pandas as pd
import json
import requests
import socketio
import fxcmpy

#print(fxcmpy.version)
#print(socketio.version)

con = fxcmpy.fxcmpy(config_file='fxcm.cfg', server='demo')

inst = con.get_instruments()

con.close()

print(inst)