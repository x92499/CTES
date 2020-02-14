# Data Visualization: Template
# Original file provided by Ryan Meyer, NREL, 3/2019
# Modified for ice tank measure analysis by Karl Heine, Mines, 5/2019

# Description: This python script creates an interactive html graph for specific data extracted from an E+ eso file.
# Users must specify which variables are to be parsed from the eso with the appropriate Hourly, and they must specify
# the plot charateristics. An rgb color index is included at the bottom of this file for reference in selecting custom
# line colors.

# Online Reference for Plotly: https://plot.ly/python/line-and-scatter/

import os
import sys
import calendar
import esoreader
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly import subplots

# [Name of .eso file, Ice Capacity [ton-hrs]]
runs = [#['SSB15_Sep',0,'Baseline'],
		#['SS47L15_SEP',2000,'Standard Operation'],
		#['SSDR9_21_12+5C',2000,'5hr DR SHED 9/21 w/Chiller'],
		['SSDR9_21_12+5',2000,'5hr DR SHED 9/21 w/o Chiller']]
		#['SSDR9_21_12+5_add',2000,'5hr DR ADD 9/21'],
		#['SSDR9_19_1130+3',2000,'3hr DR 9/19 w/Chiller']]
		#['SSDR7_20_14+6',2000,'6hr DR 7/20']]

## Simulation Control and Model Parameters------------------------------------------------------------------------------
f1 = False		#Cooling Rates and Ice SoC
f2 = True		#Electricity Use Profiles
f3 = False		#Ice Usage ** Turn on F2 for full plot **
f4 = False		#Zone Temperature Inspection
f5 = False		#Return and Supply Water Temps
f6 = False		#Pumps and Fans ** Turn on F2 for full plot **
f7 = False		#Max Demand Curves
f8 = False		#Average Daily Electric Demand Profiles
f9 = False		#Runtime and Average COP Values

# Define Run Period - Must match esos
run = [pd.datetime(2006,9,1,0), pd.datetime(2006,9,30,23,59)]

# Define Ouput Windows
out19 = pd.date_range(start = pd.datetime(2006,9,19,0), end = pd.datetime(2006,9,20,11,59), freq = '15min')
out21 = pd.date_range(start = pd.datetime(2006,9,21,0), end = pd.datetime(2006,9,22,11,59), freq = '15min')

# Define Timestep
ts_per_hr = 4

# X Axis Values
x_m = ['September']
x_dy = pd.date_range(start = run[0], end = run[1], freq = '1D')
x_hr = pd.date_range(start = run[0], end = run[1], freq = '1H')
x_ts = pd.date_range(start = run[0], end = run[1], freq = '15min')	# Must update if using diff. timestep!
x_ld_dy = np.linspace(1,31,31)
x_ld_hr = np.linspace(1,31*24,31*24)
x_ld_ts = np.linspace(1,31*24*ts_per_hr,31*24*ts_per_hr)
x_24 = np.linspace(0,23,24)

# Set Discharge, Charge, and On-Peak Windows
#dchg = [8, 21]
#chg = [22, 7.5]
#peak = [12, 18]

# Define weekend day indices
wknd = [5, 6] # Corresponds to Sat/Sun in Pandas Timestamp

# Names of Chiller/Ice Tank
ice_name = 'THERMAL STORAGE ICE DETAILED 1'
chill_name = '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON'		#Secondary School

# Plot Title Text
title_text = 'Secondary School in CZ 2A'
## END Simulation Control and Model Parameters--------------------------------------------------------------------------

## Set Up Iterations and Define Empty Lists-----------------------------------------------------------------------------
# Define Paths
paths = []
filepath = os.getcwd()
for i in range(len(runs)):
	paths.append(filepath + '/esos/' + runs[i][0] + '.eso')

# Empty Trace Variables
elec = []
pl_elec = []
pumps = []
fans = []
b_elec = []
ch_elec = []
ch_cool = []
ice_cool = []
ice_chrg = []
ice_soc = []
ch_sp = []
ice_sp = []
supply_temp = []
return_temp = []
ch_a = []
ice_a = []
chg_a = []
d_soc_avail = []
ld_chill = []
ld_p = []
ld_f = []
ld_p_c = []
ld_p_d = []
ld_p_o = []
ld_p_p = []
d_max_kw = []
d_tod_kw = []
m_max_kw = []
avg_sep = []
avg_may = []
avg_feb = []
## END Set Up Iterations and Define Empty Lists-------------------------------------------------------------------------

## Perform Iterations---------------------------------------------------------------------------------------------------
for i in range(len(runs)):
	print(runs[i][0])
	print(' Loading ESO Data...')
	dd, data = esoreader.read(paths[i])
	print(' Data Load Complete.\n Performing Calculations...')

	# Reset Select Variables
	pl_dchg = []
	pl_chg = []
	pl_pk = []
	pl_off = []

	# F1: Cooling Rates==============================
	if f1:

		if runs[i][1] != 0:
			# Ice Cooling Rate [W -> tons]
			key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage Cooling Discharge Rate']
			vals = data[key]
			vals = [k * 0.0002843451 for k in vals]		#tons

			# Ice Cooling Rate Line Plot
			ice_cool.append(go.Scatter(x = x_ts, y = vals,
									   name = runs[i][2] + ' Ice Cooling Rate [tons]',
									   #line = dict(color = '#b50b24', width = 1.5),
									   hoverlabel = dict(namelength = -1)))

			# Ice Cooling Rate Area Plot [W]
			ice_a.append(go.Scatter(x = x_ts, y = vals,
									stackgroup = str(i),
									legendgroup = str(i),
							  		name = runs[i][2] + ' Ice Cooling Rate [tons]',
									hoverlabel = dict(namelength = -1)))

		# Chiller Cooling Rate [W -> Tons]
		key =  dd.index['TimeStep', chill_name, 'Chiller Evaporator Cooling Rate']
		vals = data[key]
		cooling_total = sum(vals) / 1000	# kW
		vals = [k * 0.0002843451 for k in vals]	# tons

		# Chiller Cooling Rate Line Plot
		ch_cool.append(go.Scatter(x = x_ts, y = vals,
								  legendgroup = str(i),
								  name = runs[i][2] + ' Chiller Cooling Rate [tons]',
								  #line = dict(color = '#b50b24', width = 1.5),
								  hoverlabel = dict(namelength = -1)))

		# Chiller Cooling Rate Area Plot [Tons]
		ch_a.append(dict(x = x_ts, y = vals,
						 stackgroup = str(i),
						 legendgroup = str(i),
						 name = runs[i][2] + ' Chiller Cooling Rate [tons]',
						 hoverlabel = dict(namelength = -1)))

	# END F1: Cooling Rates==========================

	# F2: Electricity Profiles=======================
	if f2:
		# Power - Facility [J -> kW] (timestep data)
		key = dd.index['TimeStep', None, 'Electricity:Facility']
		kw_f = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		elec.append(go.Scatter(x = x_ts, y = kw_f,
							   name = runs[i][2] + ' Facility Electricity Demand [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

	    # Electricity - Chillers [J -> kW]
		key = dd.index['TimeStep', chill_name, 'Chiller Electric Energy']
		kw_c = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		ch_elec.append(go.Scatter(x = x_ts, y = kw_c,
								  name = runs[i][2] + ' Chiller Demand [kW]',
								  legendgroup = str(i),
								  #line = dict(color = '#b50b24', width = 1.5),
								  hoverlabel = dict(namelength = -1)))

		# Total Facility Electricity for Run Period
		print(' Run Period Facility Electricity: ', (sum(kw_f) / ts_per_hr), ' kWh.')

		# Total Chiller Electricity for Run Period
		elec_chiller = sum(kw_c)
		print(' Run Period Chiller Electricity [kWh]: ', elec_chiller / ts_per_hr)

		# Average Chiller COP for Run Period
		#avg_cop = cooling_total / elec_chiller
		#print(' Average Chiller COP (full year): ', avg_cop)
	# END F2: Electricity Profiles===================

	# F3: Ice Usage==================================
	if f3:
		if runs[i][1] != 0:
		    # Ice State of Charge [-]
			key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage End Fraction']
			soc = data[key]
			ice_soc.append(go.Scatter(x = x_ts, y = soc,
			 						  name = runs[i][2] + ' Ice State of Charge [-]',
									  legendgroup = str(i),
									  #line = dict(color = '#b50b24', width = 1.5),
									  hoverlabel = dict(namelength = -1)))
	# END F3: Ice Usage==============================

	# F4: Zone Temperature Inspection================
	if f4:
		x
	# END F4: Zone Temperature Inspection============

	# F5: Return and Supply Water Temps==============
	if f5:
	    # Return Temps [C]
		key = dd.index['TimeStep', 'CHILLED WATER LOOP SUPPLY INLET NODE', 'System Node Temperature']
		return_temp.append(go.Scatter(x = x_ts, y = data[key],
									  name = runs[i][2] + ' Return Water Temp [C]',
									  legendgroup = str(i),
									  #line = dict(color = '#b50b24', width = 1.5),
									  hoverlabel = dict(namelength = -1)))

		# Supply Temps [C]
		key = dd.index['TimeStep', 'CHILLED WATER LOOP SUPPLY OUTLET NODE', 'System Node Temperature']
		supply_temp.append(go.Scatter(x = x_ts, y = data[key],
									  name = runs[i][2] + ' Supply Water Temp [C]',
									  legendgroup = str(i),
									  #line = dict(color = '#b50b24', width = 1.5),
									  hoverlabel = dict(namelength = -1)))
	# END F5: Return and Supply Water Temps==========

	# F6: Pumps and Fans=============================
	if f6:
		# Power - Fans [J -> kW] (timestep data)
		key = dd.index['TimeStep', None, 'Fans:Electricity']
		kw_fans = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		fans.append(go.Scatter(x = x_ts, y = kw_fans,
								name = runs[i][2] + ' Total Fan Power [kWe]',
								legendgroup = str(i),
								hoverlabel = dict(namelength = -1)))

		# Power - Pumps [J -> kW] (timestep data)
		key = dd.index['TimeStep', None, 'Pumps:Electricity']
		kw_pumps = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		pumps.append(go.Scatter(x = x_ts, y = kw_pumps,
								name = runs[i][2] + ' Total Pump Power [kWe]',
								legendgroup = str(i),
								hoverlabel = dict(namelength = -1)))
	# END F6: Pumps and Fans=========================



print("Writing Elec Output 9/21 - Transfer to Excel")
# Output (last run) to Data File
file1 = open('dr_kwe.txt', 'w')
file1.write(str(runs[0]) + '\n')
for i in range(len(kw_f)):
	if x_ts[i] in out21:
		file1.write(str(x_ts[i].hour) + ':' + str(x_ts[i].minute) + '  ' + str(kw_f[i]) + '\n')
file1.close


## Create Figures-------------------------------------------------------------------------------------------------------
standard_template = go.layout.Template(layout = go.Layout(height = 700, width = 1400,
										title_font = dict(family = 'Rockwell', size = 28),
										xaxis = dict(title_font = dict(family = 'Rockwell', size = 24),
												tickfont = dict(family = 'Rockwell', size = 20),
												showgrid = True, gridcolor = 'rgb(203,203,203)'),
										yaxis = dict(title_font = dict(family = 'Rockwell', size = 24),
												tickfont = dict(family = 'Rockwell', size = 20),
												showgrid = True, gridcolor = 'rgb(203,203,203)'),
										paper_bgcolor = 'rgba(0,0,0,0)', plot_bgcolor = 'rgba(0,0,0,0)',
										#legend = dict(x = 0.5, y = 1.1, font = dict(family = 'Rockwell', size = 18)),
										hovermode = 'closest'))

# F1: Cooling Rates==========================
if f1:
	fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = True)
	                          #subplot_titles = ('Cooling Rates [tons]','Ice Tank States of Charge [-]'))

	for i in range(len(ice_a)):
		fig.append_trace(ice_a[i],1,1)

	for i in range(len(ch_a)):
		fig.append_trace(ch_a[i],1,1)

	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'dr_rates_soc.html')
# END F1: Cooling Rates==========================

# F2: Electricity Profiles=======================
if f2:
	fig = subplots.make_subplots(rows = 2, cols = 1, shared_xaxes = True,
							    subplot_titles = ('Facility Demand [kWe]', 'Chiller Demand [kWe]'))

	for i in range(len(elec)):
		fig.append_trace(elec[i],1,1)

	for i in range(len(ch_elec)):
		fig.append_trace(ch_elec[i],2,1)

	#fig['layout'].update(title = title_text)
	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'dr_elec.html')
# END F2: Electricity Profiles===================

# F3: Ice Usage==================================
if f3:
	fig = subplots.make_subplots(rows = 2, cols = 1, shared_xaxes = True,
								subplot_titles = ('Ice State of Charge [-]', 'Chiller Demand [kWe]'))

	for i in range(len(ice_soc)):
		fig.append_trace(ice_soc[i],1,1)

	if f2:
		for i in range(len(ch_elec)):
			fig.append_trace(ch_elec[i],2,1)

	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'dr_soc.html')
# END F3: Ice Usage==============================


# F5: Return and Supply Water Temps==============
if f5:
	fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = True,
								subplot_titles = ('Loop Temperatures [C]'))

	for i in range(len(supply_temp)):
		fig.append_trace(supply_temp[i],1,1)

	for i in range(len(return_temp)):
		fig.append_trace(return_temp[i],1,1)

	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'dr_temps.html')
# END F5: Return and Supply Water Temps==========

# F6: Pumps and Fans=============================
if f6:
	fig = subplots.make_subplots(rows = 3, cols = 1, shared_xaxes = True,
								subplot_titles = ('Pump Power [kWe]', 'Fan Power [kWe]', 'Chiller Electric Power [kWe]'))

	for i in range(len(pumps)):
		fig.append_trace(pumps[i],1,1)

	for i in range(len(fans)):
		fig.append_trace(fans[i],2,1)

	if f2:
		for i in range(len(ch_elec)):
			fig.append_trace(ch_elec[i],3,1)

	fig['layout'].update(template = standard_template, height = 1000)
	plotly.offline.plot(fig, filename = 'pumps_fans.html')
# END F6: Pumps and Fans=========================

## END Create Figures---------------------------------------------------------------------------------------------------
