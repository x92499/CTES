# Timestep "Sensitivity" Plots
# Karl Heine, 9/26/2019

import os
import esoreader
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly import subplots

# Empty Trace Variables
PWR_tr = []
Chiller_tr = []
CRate_tr = []
T1_tr = []
T2_tr = []

# Create x-axis variables
x_60 = pd.date_range(start = pd.datetime(2006,9,10,0), end = pd.datetime(2006,9,23,23,59), freq = '1H')
x_15 = pd.date_range(start = pd.datetime(2006,9,10,0), end = pd.datetime(2006,9,23,23,59), freq = '15min')
x_5 = pd.date_range(start = pd.datetime(2006,9,10,0), end = pd.datetime(2006,9,23,23,59), freq = '5min')
x_1 = pd.date_range(start = pd.datetime(2006,9,10,0), end = pd.datetime(2006,9,23,23,59), freq = '1min')

# Define Filepath
filepath = os.getcwd() + '/esos/'

## Baseline Sets-------------------------------------------

## 60 Min Baseline-----------------------------
dd, data = esoreader.read(filepath + 'SSB60_short.eso')
# Chiller Power
key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Electric Power']
vals = [j / 1000 for j in data[key]]
Chiller_tr.append(go.Scatter(x = x_60, y = vals, name = 'B60 Chiller Power', legendgroup = 'B60'))

# Chiller Cooling Rate
key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Evaporator Cooling Rate']
vals = [w * 0.0002843451 for w in data[key]]	#W to tons
CRate_tr.append(go.Scatter(x = x_60, y = vals, name = 'B60 Chiller Cooing Rate', legendgroup = 'B60'))

## 1 Min Baseline---------------------------
## Facility Power
dd, data = esoreader.read(filepath + 'SSB1_short.eso')
#key = dd.index['TimeStep', None, 'Electricity:Facility']
#vals = [j * 2.77778e-7 * 60 for j in data[key]]
#PWR_tr.append(go.Scatter(x = x_1, y = vals, name = 'B1 Facility Power', legendgroup = 1))

# Room Temp(s)
#key = dd.index['TimeStep', 'CORNER_CLASS_2_POD_2_ZN_1_FLR_2 ZN', 'Zone Air Temperature']
#T1_tr.append(go.Scatter(x = x_1, y = data[key], name = 'B1 Room 1 Temp', legendgroup = 1))

# Chiller Power
key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Electric Power']
vals = [j / 1000 for j in data[key]]
Chiller_tr.append(go.Scatter(x = x_1, y = vals, name = 'B1 Chiller Power', legendgroup = 'B1'))

# Chiller Cooling Rate
key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Evaporator Cooling Rate']
vals = [w * 0.0002843451 for w in data[key]]	#W to tons
CRate_tr.append(go.Scatter(x = x_1, y = vals, name = 'B1 Chiller Cooing Rate', legendgroup = 'B1'))

## 1 Min w/Cap Baseline
# Facility Power
#dd, data = esoreader.read(filepath + 'SSB1CT_short.eso')
#key = dd.index['TimeStep', None, 'Electricity:Facility']
#vals = [j * 2.77778e-7 * 60 for j in data[key]]
#PWR_tr.append(go.Scatter(x = x_1, y = vals, name = 'B1CT Facility Power', legendgroup = 2))

# Room Temp(s)
#key = dd.index['TimeStep', 'CORNER_CLASS_2_POD_2_ZN_1_FLR_2 ZN', 'Zone Air Temperature']
#T1_tr.append(go.Scatter(x = x_1, y = data[key], name = 'B1CT Room 1 Temp', legendgroup = 2))

# Chiller Power
#key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Electric Power']
#vals = [j / 1000 for j in data[key]]
#Chiller_tr.append(go.Scatter(x = x_1, y = vals, name = 'B1CT Chiller Power', legendgroup = 2))

print('Base Complete')

## Ice Sets-----------------------------------------------------------
## 1 Min Ice
# Facility Power
dd, data = esoreader.read(filepath + 'SS47L1_short.eso')
#key = dd.index['TimeStep', None, 'Electricity:Facility']
#vals = [j * 2.77778e-7 * 60 for j in data[key]]
#PWR_tr.append(go.Scatter(x = x_1, y = vals, name = 'I1 Facility Power', legendgroup = 3))

# Room Temp(s)
#key = dd.index['TimeStep', 'CORNER_CLASS_2_POD_2_ZN_1_FLR_2 ZN', 'Zone Air Temperature']
#T1_tr.append(go.Scatter(x = x_1, y = data[key], name = 'I1 Room 1 Temp', legendgroup = 3))

# Chiller Power
key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Electric Power']
vals = [j / 1000 for j in data[key]]
Chiller_tr.append(go.Scatter(x = x_1, y = vals, name = 'I1 Chiller Power', legendgroup = 'I1'))

# Chiller Cooling Rate
key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Evaporator Cooling Rate']
vals = [w * 0.0002843451 for w in data[key]]	#W to tons
CRate_tr.append(go.Scatter(x = x_1, y = vals, name = 'I1 Chiller Cooing Rate', legendgroup = 'I1'))

## 1 Min w/Cap Ice
# Facility Power
#dd, data = esoreader.read(filepath + 'SS47L1CT_short.eso')
#key = dd.index['TimeStep', None, 'Electricity:Facility']
#vals = [j * 2.77778e-7 * 60 for j in data[key]]
#PWR_tr.append(go.Scatter(x = x_1, y = vals, name = 'I1CT Facility Power', legendgroup = 4))

# Room Temp(s)
#key = dd.index['TimeStep', 'CORNER_CLASS_2_POD_2_ZN_1_FLR_2 ZN', 'Zone Air Temperature']
#T1_tr.append(go.Scatter(x = x_1, y = data[key], name = 'I1CT Room 1 Temp', legendgroup = 4))

# Chiller Power
#key = dd.index['TimeStep', '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON', 'Chiller Electric Power']
#vals = [j / 1000 for j in data[key]]
#Chiller_tr.append(go.Scatter(x = x_1, y = vals, name = 'I1CT Chiller Power', legendgroup = 4))

print('TES Complete')

## Create Figure
fig = subplots.make_subplots(rows = 2, cols = 1, shared_xaxes = True,
							subplot_titles = ('Chiller Power [kW]', 'Chiller Cooling Rate [tons]'))

for i in range(len(Chiller_tr)):
	fig.append_trace(Chiller_tr[i],1,1)

for i in range(len(CRate_tr)):
	fig.append_trace(CRate_tr[i],2,1)

plotly.offline.plot(fig, filename = 'timestep_comparison.html')

print('Figures Complete')
