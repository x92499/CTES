# Performance Curve Plots
# xarl Heine, 20190605

# This script plots the performance curve data taxen from the default curves within OpenStudio for the Ice Storage object.
# Ref. object: OS:ThermalStorage:Ice:Detailed
# EnergyPlus Engineering Reference: Ch 16.1.2
# EnergyPlus Input-Output Reference: Ch 1.56.11 (Curves)

import sys
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly import subplots

# Set charge/discharge curve coefficients

## Detailed Model
# Curve Type: Quadratic Linear - values from the OpenStudio object defaults
c = [0,			# constant
	 0.09,		# x
	 -0.15,		# x^2
	 0.612,		# y
	 -0.324,	# x*y
	 -0.216]	# x^2*y

Tin = -1
Tout = -5		#C
Tfreeze = 0                 #C
DeltaT = abs(Tin - Tout)	#F to C
DeltaT_Nominal = 10		    #C

LMTD_star_actual = []
LMTD_star_model = []

# As Modeled in OpenStudio Measure
LMTD_star_model = (DeltaT/np.log((Tin - Tfreeze)/(Tout - Tfreeze)) / DeltaT_Nominal)

Pd = np.linspace(0,1,100)

q_star_model = []
q_star_model_trace = []

# Calculate q* and q
for j in range(len(Pd)):
	x = Pd[j]
	y = LMTD_star_model
	q_star_model.append(c[0] + c[1]*x + c[2]*(x**2) + c[3]*y + c[4]*y*x + c[5]*y*(x**2))

q_star_model_trace.append(go.Scatter(x = Pd, y = q_star_model, name = 'Model', hoverlabel = dict(namelength = -1)))

## Create Figures
fig = subplots.make_subplots(rows = 1, cols = 1)

for i in range(len(q_star_model_trace)):
	fig.append_trace(q_star_model_trace[i],1,1)

fig['layout'].update(title = 'Ice Charge Curve: Inlet Water at ' + str(round(Tin, 1)) +
 					 'C, Outlet Water at ' + str(round(Tout, 1)) + 'C, Delta T at ' + str(round(DeltaT, 1)) +
                     'C', hovermode = 'closest', showlegend = False)
fig['layout']['xaxis1'].update(title='Fraction Charged [-]')
fig['layout']['yaxis1'].update(title='q* [-]')


plotly.offline.plot(fig, filename = 'ice_curves.html')
