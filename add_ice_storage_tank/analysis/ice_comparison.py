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
runs = [#['SS47L15_6_68', 2000, 'Ice - 60% Chiller, 68% Limiter'],
		['SS47L15_6_70', 2000, 'Ice - 60% Chiller, 70% Limiter'],
		['SS47L15', 2000, 'Ice - 70% Chiller, 65% Limiter'],
		['SS48I', 2000, '70% Chiller Downstream']]
		#['SSFull', 3200, 'Full Storge']]
		#['SSB15', 0, 'Baseline']]
		#['SS-Base',0,'Baseline:']]

#Set Timestep
ts_per_hr = 4
ems = False

f1 = False		#Cooling Rates and Ice SoC
f2 = False		#Stacked Area Plot Totalling Ice and Chiller Cooling Rates - Unnecessary, already wrapped into fig 1
f3 = False		#Electricity Use Profiles
f4 = False		#Daily Unused Ice
f5 = False		#Return and Supply Water Temps - Ice Only
f6 = True		#Load Duration Curves
f7 = False		#Max Demand Curves
f8 = False		#Average Daily Electric Demand Profiles
f9 = True		#Runtime and Average COP Values - KEEP ON

# X Axis Values
x_m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
x_dy = pd.date_range(start = pd.datetime(2006,1,1,0), end = pd.datetime(2006,12,31,23,59), freq = '1D')
x_hr = pd.date_range(start = pd.datetime(2006,1,1,0), end = pd.datetime(2006,12,31,23,59), freq = '1H')
x_ts = pd.date_range(start = pd.datetime(2006,1,1,0), end = pd.datetime(2006,12,31,23,59), freq = '15min')
#x_ts = x_hr
x_ld_dy = np.linspace(1,365,365)
x_ld_hr = np.linspace(1,365*24,365*24)
x_ld_ts = np.linspace(1,365*24*ts_per_hr,365*24*ts_per_hr)
#x_24 = np.linspace(0,23.75,24*ts_per_hr)
x_24 = np.linspace(0,23,24)

# Set Discharge, Charge, and On-Peak Windows
#dchg = [12, 18]
dchg = [8, 18]
chg = [19, 7]
peak = [12, 18]

# Define weekend day indices
wknd = [5, 6] # Corresponds to Sat/Sun in Pandas Timestamp

# Define Limited Analysis Peirod - If Needed for Reduced-Size Plots
#an_start = pd.datetime(2006,9,10,0)				#Hour 0 on Sept 10
#an_end = pd.datetime(2006,9,24,0)				#Hour 0 on Sept 24
#an_pd = []										#Index range of analysis period - empty
#idx = 0
#for x in x_ts:
#	if x == an_start:
#		an_pd.append(idx)
#	if x == an_end:
#		an_pd.append(idx)
#	idx += 1

#x_an = pd.date_range(start = x_ts[an_pd[0]], end = x_ts[an_pd[1]], freq = '1min')	#Timestamp vector - for plotting

# Names of Chiller/Ice Tank
ice_name = 'THERMAL STORAGE ICE DETAILED 1'
#chill_name = '90.1-2010 WATERCOOLED  CENTRIFUGAL CHILLER 0 618TONS 0.6KW/TON'		#Large Office
chill_name = '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON'		#Secondary School

# Plot Title Text
title_text = 'Secondary School in CZ 2A'
#title_text = 'Large Office in CZ 5B'

# Define Paths
paths = []
filepath = os.getcwd()
for i in range(len(runs)):
	paths.append(filepath + '/esos/' + runs[i][0] + '.eso')

# Empty Trace Variables
elec = []
pl_elec = []
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
limiter = []

## Ice Tank Runs
for i in range(len(runs)-1):
	#break
	print(runs[i][0])
	print(' Loading ESO Data...')
	dd, data = esoreader.read(paths[i])
	print(' Data Load Complete.\n Performing Calculations...')

	# Reset Select Variables
	pl_dchg = []
	pl_chg = []
	pl_pk = []
	pl_off = []

	# Data for Figures 1, 2, and 4:
	if f1 or f2 or f4 or f9:
		# Ice Cooling Rate [W -> tons]
		key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage Cooling Discharge Rate']
		vals = data[key]
		vals = [k * 0.0002843451 for k in vals]		#tons
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

	    # Ice Charging Rate [W]
		key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage Cooling Charge Rate']
		vals = data[key]
		vals = [k * 0.0002843451 for k in vals]		#tons
		ice_chrg.append(go.Scatter(x = x_ts, y = vals,
								   legendgroup = str(i),
								   #line = dict(color = '#b50b24', width = 1.5),
								   name = runs[i][2] + ' Ice Charge Rage [tons]',
								   hoverlabel = dict(namelength = -1)))

	    # Ice Charging Rate Area Plot [W]
		chg_a.append(go.Scatter(x = x_ts, y = vals,
						  		stackgroup = str(i),
								legendgroup = str(i),
								hoverlabel = dict(namelength = -1)))

	    # Ice State of Charge [-]
		key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage End Fraction']
		soc = data[key]
		ice_soc.append(go.Scatter(x = x_ts, y = soc,
		 						  name = runs[i][2] + ' Ice State of Charge [-]',
								  legendgroup = str(i),
								  #line = dict(color = '#b50b24', width = 1.5),
								  hoverlabel = dict(namelength = -1)))

	    # Find Min Daily Ice SOC - Ensure x_ts aligns with .eso timestamps
		#(must reformulate for smaller reporting timesteps and longer simulation run periods)
		day_min_soc = [1.0] * 365	#set for July only
		for j in range(len(soc)):
			idx = int(x_ts[j].dayofyear) - 1
			if dchg[0] <= x_ts[j].hour < dchg[1]:
				if soc[j] < day_min_soc[idx]:
					day_min_soc[idx] = soc[j]

		print(' Minimum Annual SOC: ', min(day_min_soc))

		# Unused Ice Energy [Ton-Hours]
		unused = [round(j * runs[i][1],0) for j in day_min_soc]
		d_soc_avail.append(go.Bar(x = x_dy, y = unused,
		 						  name = runs[i][2] + ' Unused Ice Capacity [Ton-Hours]',
								  opacity = 0.6, text = unused, textposition = 'auto',
								  legendgroup = str(i),
								  #marker_color = '#b50b24',
								  hoverinfo = 'y+name', marker = dict(color = '#000000'),
								  hoverlabel = dict(namelength = -1)))

	    # Chiller Cooling Rate [W -> Tons]
		key =  dd.index['TimeStep', chill_name, 'Chiller Evaporator Cooling Rate']
		vals = data[key]
		cooling_total = sum(vals) / 1000	# kW
		cooling_chiller = vals
		vals = [k * 0.0002843451 for k in vals]	# tons
		l1 = len(vals)
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

		vals = [x for x in vals if x > 2] # The chiller never goes to 0, Min is ~1.3kW Cooling Rate. (??)
		l2 = len(vals)
		print(' Chiller Runtime Hours: ', l2/l1*8760)
		print(' Chiller Total Annual Cooling [kWh]: ', cooling_total / ts_per_hr)

		if ems:
			# Chiller Limiter Counter
			key = dd.index['TimeStep', 'EMS', 'Chiller Limit Counter']
			vals = data[key]
			limiter_flag = [0] * len(vals)
			for idx in range(len(vals) - 1):
				if vals[idx + 1] - vals[idx] > 0:
					limiter_flag[idx] = 1

			limiter.append(go.Scatter(x = x_ts, y = limiter_flag,
									legendgroup = str(i),
									name = runs[i][2] + ' Chiller Limiter [-]',
									hoverlabel = dict(namelength = -1)))

			print(' Limiter Count [Zone Timesteps]: ', sum(limiter_flag))

	# Data for Figures 3, 6, 7, 8, and 9:
	if f3 or f6 or f7 or f8 or f9:
	    # Power - Facility [kW] (timestep data)
		key = dd.index['TimeStep', None, 'Electricity:Facility']
		kw = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		elec.append(go.Scatter(x = x_ts, y = kw,
							   name = runs[i][2] + ' Facility Electricity Demand [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

		print(' Annual Facility Electricity: ', (sum(kw) / ts_per_hr), ' kWh.')

		file1 = open('elec_ice.txt','w')
		for z in kw:
			file1.write(str(z) + '\n')
		file1.close

		# Find Max Daily kW (timestep data)
		daily_kw_max = [-1.0] * 365
		daily_kw_tod = [99] * 365
		monthly_kw_max = [0.0] * 12
		#average_weekdays = [[0.0 for h in range(24*ts_per_hr)] for m in range(12)]
		average_weekdays = [[0.0 for h in range(24)] for m in range(12)]
		num_weekday_steps = [0 for m in range(12)]
		average_weekend = [[0.0 for h in range(24)] for m in range(12)]
		num_wknd_steps = [0 for m in range(12)]
		average_7to7 = [[0.0 for h in range(24)] for m in range(12)]
		num_7to7_steps = [0 for m in range(12)]

		for k in range(len(kw)):
			idx = (x_ts[k].dayofyear) - 1
			if daily_kw_max[idx] < kw[k]:
				daily_kw_max[idx] = round(kw[k], 1)
				daily_kw_tod[idx] = x_ts[k].hour + (x_ts[k].minute / 60)
			mdx = x_ts[k].month - 1
			if monthly_kw_max[mdx] < kw[k]:
				monthly_kw_max[mdx] = int(round(kw[k], 0))

			# Determine "Average" Day for Each Month
			ddx = x_ts[k].day - 1
			dow = x_ts[k].dayofweek
			#tdx = x_ts[k].hour*ts_per_hr + (x_ts[k].minute/15)
			#tdx = int(tdx)
			tdx = x_ts[k].hour
			if dow not in wknd:
				#num_weekday_steps[mdx] = num_weekday_steps[mdx] + (1 / (24*ts_per_hr))
				num_weekday_steps[mdx] = num_weekday_steps[mdx] + (1 / 24)
				average_weekdays[mdx][tdx] = average_weekdays[mdx][tdx] + kw[k]
			if dow in wknd:
				num_wknd_steps[mdx] = num_wknd_steps[mdx] + (1 / 24)
				average_weekend[mdx][tdx] = average_weekend[mdx][tdx] + kw[k]

			#Perform M-Sat 7am-7am Monthly Averaging
			if dow != wknd[1]:
				if dow == 0 and tdx >= 7:
					num_7to7_steps[mdx] = num_7to7_steps[mdx] + (1 / 24)
					average_7to7[mdx][tdx] = average_7to7[mdx][tdx] + kw[k]
				elif dow == wknd[0] and tdx < 7:
					num_7to7_steps[mdx] = num_7to7_steps[mdx] + (1 / 24)
					average_7to7[mdx][tdx] = average_7to7[mdx][tdx] + kw[k]
				elif dow in [1,2,3,4]:
					num_7to7_steps[mdx] = num_7to7_steps[mdx] + (1 / 24)
					average_7to7[mdx][tdx] = average_7to7[mdx][tdx] + kw[k]

		for m in range(12):
			average_weekdays[m] = [v / num_weekday_steps[m] for v in average_weekdays[m]]
			average_weekend[m] = [v / num_wknd_steps[m] for v in average_weekend[m]]
			average_7to7[m] = [v / num_7to7_steps[m] for v in average_7to7[m]]

		print(' Max Annual Demand [kW]: ', max(monthly_kw_max))

		filename4 = 'avg_profiles_' + runs[i][0] + '.txt'
		file4 = open(filename4,'w')
		file4.write(runs[i][0] + ' Average Daily Profiles by Month \n')
		for m in range(12):
			file4.write(str(m) + ' ')
			for t in range(len(average_weekdays[m])):
				file4.write(str(round(average_weekdays[m][t],2)) + ' ')
			file4.write('\n')
		file4.write('\n Weekend Profiles \n')
		for m in range(12):
			file4.write(str(m) + ' ')
			for t in range(len(average_weekend[m])):
				file4.write(str(round(average_weekend[m][t],2)) + ' ')
			file4.write('\n')
		file4.write('\n 7-7 Profiles \n')
		for m in range(12):
			file4.write(str(m) + ' ')
			for t in range(len(average_7to7[m])):
				file4.write(str(round(average_7to7[m][t],2)) + ' ')
			file4.write('\n')
		file4.close

		d_max_kw.append(go.Scatter(x = x_dy, y = daily_kw_max,
								   name = runs[i][2] + ' Daily Max Demand [kW]',
								   legendgroup = str(i),
								   #line = dict(color = '#b50b24', width = 1.5, dash = 'dot'),
								   mode = 'markers+lines',
								   hoverlabel = dict(namelength = -1)))

		m_max_kw.append(go.Bar(x = x_m, y = monthly_kw_max,
							   name = runs[i][2] + ' Monthly Max Demand [kW]',
							   #marker_color = '#b50b24',
							   legendgroup = str(i),
							   opacity = 0.9, text = monthly_kw_max, textposition = 'auto',
							   hoverinfo = 'x+y+name', hoverlabel = dict(namelength = -1)))

		avg_sep.append(go.Scatter(x = x_24, y = average_7to7[8],
								  #line = dict(color = '#b50b24', width = 1.5),
								  name = runs[i][2] + ' September [kW]'))

		avg_may.append(go.Scatter(x = x_24, y = average_7to7[4],
								  #line = dict(color = '#b50b24', width = 1.5),
								  name = runs[i][2] + ' May [kW]'))

		avg_feb.append(go.Scatter(x = x_24, y = average_7to7[1],
								  #line = dict(color = '#b50b24', width = 1.5),
								  name = runs[i][2] + ' February [kW]'))

	    # Facility Load Duration Curves - Timestep Data [kW]
		kw.sort(reverse = True)
		ld_f.append(go.Scatter(x = x_ld_ts, y = kw,
							   name = runs[i][2] + ' Facility Electricity Demand [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

		b = np.array(kw)
		filename5 = 'ld_' + runs[i][0] + '.txt'
		file5 = open(filename5,'w')
		for z in b:
			file5.write(str(z) + '\n')
		file5.close

		a = np.linspace(0,8760*ts_per_hr,8760*ts_per_hr)
		A = np.vstack([a, np.ones(len(a))]).T
		lin_fit = np.linalg.lstsq(A, b, rcond = None)
		print('', lin_fit[0])

	    # Electricity Demand - Plant [kW]
		key = dd.index['TimeStep', None, 'Electricity:Plant']
		kw = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		pl_elec.append(go.Scatter(x = x_ts, y = kw,
								  name = runs[i][2] + ' Plant Electricity Demand [kW]',
								  legendgroup = str(i),
								  #line = dict(color = '#b50b24', width = 1.5),
								  hoverlabel = dict(namelength = -1)))

		for k in range(len(kw)):
			# Discharge Period Plant Loads
			if dchg[0] <= x_ts[k].hour < dchg[1]:
				if x_ts[k].dayofweek not in wknd:
					pl_dchg.append(kw[k])
			# Charge Period Plant Loads
			elif x_ts[k].hour >= chg[0] or x_ts[k].hour < chg[1]:
				pl_chg.append(kw[k])

			# Peak Period Plant Loads
			if peak[0] <= x_ts[k].hour < peak[1]:
				if x_ts[k].dayofweek not in wknd:
					pl_pk.append(kw[k])
			# Off Peak Periods Plant Loads
			else:
				pl_off.append(kw[k])

	    # Plant Load Duration Curves - Timestep Data [kW]
		kw.sort(reverse = True)
		pl_dchg.sort(reverse = True)
		pl_chg.sort(reverse = True)
		pl_pk.sort(reverse = True)
		pl_off.sort(reverse = True)

		ld_p.append(go.Scatter(x = x_ld_ts, y = kw,
							   name = runs[i][2] + ' Plant Electricity Demand [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

		ld_p_d.append(go.Scatter(x = x_ld_ts, y = pl_dchg,
							   name = runs[i][2] + ' Plant Electricity Demand During Discharge [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

		ld_p_c.append(go.Scatter(x = x_ld_ts, y = pl_chg,
							   name = runs[i][2] + ' Plant Electricity Demand During Charge [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

		ld_p_p.append(go.Scatter(x = x_ld_ts, y = pl_pk,
							   name = runs[i][2] + ' Plant Electricity Demand During Peak [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

		ld_p_o.append(go.Scatter(x = x_ld_ts, y = pl_off,
							   name = runs[i][2] + ' Plant Electricity Demand During Off-Peak [kW]',
							   legendgroup = str(i),
							   #line = dict(color = '#b50b24', width = 1.5),
							   hoverlabel = dict(namelength = -1)))

	    # Electricity - Chillers [kW]
		key = dd.index['TimeStep', chill_name, 'Chiller Electric Energy']
		kw = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
		ch_elec.append(go.Scatter(x = x_ts, y = kw,
								  name = runs[i][2] + ' Chiller Demand [kW]',
								  legendgroup = str(i),
								  #line = dict(color = '#b50b24', width = 1.5),
								  hoverlabel = dict(namelength = -1)))

		# Total Chiller Electricity for Run Period
		elec_chiller = sum(kw)
		print(' Chiller Annual Electricity [kWh]: ', elec_chiller / ts_per_hr)
		avg_cop = cooling_total / elec_chiller
		print(' Average Chiller COP (full year): ', avg_cop)

		# Chiller Average COP During Occupied Hours
		occ_elec_chiller = 0
		occ_cooling = 0
		occ_runtime = 0

		for k in range(len(kw)):
			if dchg[0] <= x_ts[k].hour < dchg[1]:
				if x_ts[k].dayofweek not in wknd:
					if cooling_chiller[k] > 0:
						occ_elec_chiller += kw[k]
						occ_cooling += cooling_chiller[k] / 1000
						occ_runtime += 1 / ts_per_hr

		occ_cop = occ_cooling/occ_elec_chiller
		print(' Average Chiller COP During Occupied Hours: ', occ_cop)
		print(' Chiller Runtime During Occupied Hours: ', occ_runtime)

	    # Chiller Load Duration Curves - TimeStep Data [kW]
		kw.sort(reverse = True)
		ld_chill.append(go.Scatter(x = x_ld_ts, y = kw,
								   name = runs[i][2] + ' Chiller Electricity [kW]',
								   legendgroup = str(i),
								   #line = dict(color = '#b50b24', width = 1.5),
								   hoverlabel = dict(namelength = -1)))

	# Data for Figure 5
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

		# Ice Setpoint Temps [C]
		#key = dd.index['TimeStep', ice_name + ' SETPOINT SCHEDULE (NEW)', 'Schedule Value']
		#ice_sp.append(go.Scatter(x = x_ts, y = data[key],
		#					 	 name = runs[i][2] + ' Ice Tank Setpoint [C]',
		#						 legendgroup = str(i),
		#						 hoverlabel = dict(namelength = -1)))

		# Chiller Setpoint Temps [C]
		#key = dd.index['TimeStep', chill_name + ' SETPOINT SCHEDULE (NEW)', 'Schedule Value']
		#ch_sp.append(go.Scatter(x = x_ts, y = data[key],
		#						name = runs[i][2] + ' Chiller Setpoint [C]',
		#						legendgroup = str(i),
		#						hoverlabel = dict(namelength = -1)))

	print(' Complete.')

## Baseline Model Variables
print(runs[-1][0])
print(' Loading Data...')
dd, data = esoreader.read(paths[-1])
print(' Data Load Complete.\n Performing Calculations...')

# Reset Select Variables
pl_dchg = []
pl_chg = []
pl_pk = []
pl_off = []

# Chiller Cooling Rate [W]
key =  dd.index['TimeStep', chill_name, 'Chiller Evaporator Cooling Rate']
vals = data[key]
cooling_total = sum(vals) / 1000	# kW - quarter hours
cooling_chiller = vals
vals = [k * 0.0002843451 for k in vals]
l1 = len(vals)
ch_cool.append(go.Scatter(x = x_ts, y = vals,
						  name = runs[-1][2] + ' Chiller Evaporator Cooling Rate [tons]',
						  legendgroup = str(-1),
					      hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
						  line = dict(color = '#000000', dash = 'dot', width = 1.5)))

vals = [x for x in vals if x > 2]
l2 = len(vals)
print(' Runtime Hours: ', l2/l1*8760)
print(' Chiller Total Annual Cooling* [kWh]: ', cooling_total / ts_per_hr)

# Power - Facility [kW]
key = dd.index['TimeStep', None, 'Electricity:Facility']
kw = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
elec.append(go.Scatter(x = x_ts, y = kw,
					   name = runs[-1][2] + ' Facility Electricity Demand [kW]',
					   legendgroup = str(-1),
					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

print(' Annual Facility Electricity: ', (sum(kw) / ts_per_hr), ' kWh.')

file2 = open('elec_base.txt','w')
for z in kw:
	file2.write(str(z) + '\n')
file2.close

# Find Max Daily kW (timestep data)
daily_kw_max = [-1.0] * 365
daily_kw_tod = [99] * 365
monthly_kw_max = [0.0] * 12
#average_weekdays = [[0.0 for h in range(24*ts_per_hr)] for m in range(12)]
average_weekdays = [[0.0 for h in range(24)] for m in range(12)]
num_weekday_steps = [0 for m in range(12)]
average_weekend = [[0.0 for h in range(24)] for m in range(12)]
num_wknd_steps = [0 for m in range(12)]
average_7to7 = [[0.0 for h in range(24)] for m in range(12)]
num_7to7_steps = [0 for m in range(12)]

for k in range(len(kw)):
	idx = (x_ts[k].dayofyear) - 1
	if daily_kw_max[idx] < kw[k]:
		daily_kw_max[idx] = round(kw[k], 1)
		daily_kw_tod[idx] = x_ts[k].hour + (x_ts[k].minute / 60)
	mdx = x_ts[k].month - 1
	if monthly_kw_max[mdx] < kw[k]:
		monthly_kw_max[mdx] = int(round(kw[k], 0))

	# Determine "Average" Day for Each Month
	ddx = x_ts[k].day - 1
	dow = x_ts[k].dayofweek
	#tdx = x_ts[k].hour*ts_per_hr + (x_ts[k].minute/15)
	#tdx = int(tdx)
	tdx = x_ts[k].hour
	if dow not in wknd:
		#num_weekday_steps[mdx] = num_weekday_steps[mdx] + (1 / (24*ts_per_hr))
		num_weekday_steps[mdx] = num_weekday_steps[mdx] + (1 / 24)
		average_weekdays[mdx][tdx] = average_weekdays[mdx][tdx] + kw[k]
	if dow in wknd:
		num_wknd_steps[mdx] = num_wknd_steps[mdx] + (1 / 24)
		average_weekend[mdx][tdx] = average_weekend[mdx][tdx] + kw[k]

	#Perform M-Sat 7am-7am Monthly Averaging
	if dow != wknd[1]:
		if dow == 0 and tdx >= 7:
			num_7to7_steps[mdx] = num_7to7_steps[mdx] + (1 / 24)
			average_7to7[mdx][tdx] = average_7to7[mdx][tdx] + kw[k]
		elif dow == wknd[0] and tdx < 7:
			num_7to7_steps[mdx] = num_7to7_steps[mdx] + (1 / 24)
			average_7to7[mdx][tdx] = average_7to7[mdx][tdx] + kw[k]
		elif dow in [1,2,3,4]:
			num_7to7_steps[mdx] = num_7to7_steps[mdx] + (1 / 24)
			average_7to7[mdx][tdx] = average_7to7[mdx][tdx] + kw[k]

for m in range(12):
	average_weekdays[m] = [v / num_weekday_steps[m] for v in average_weekdays[m]]
	average_weekend[m] = [v / num_wknd_steps[m] for v in average_weekend[m]]
	average_7to7[m] = [v / num_7to7_steps[m] for v in average_7to7[m]]

print(' Max Annual Demand [kW]: ', max(monthly_kw_max))

filename3 = 'avg_profiles_' + runs[-1][0] + '.txt'
file3 = open(filename3,'w')
file3.write('Baseline Average Daily Profiles by Month \n')
for m in range(12):
	file3.write(str(m) + ' ')
	for t in range(len(average_weekdays[m])):
		file3.write(str(round(average_weekdays[m][t],2)) + ' ')
	file3.write('\n')
file3.write('\n Weekend Profiles \n')
for m in range(12):
	file3.write(str(m) + ' ')
	for t in range(len(average_weekend[m])):
		file3.write(str(round(average_weekend[m][t],2)) + ' ')
	file3.write('\n')
file3.write('\n 7-7 Profiles \n')
for m in range(12):
	file3.write(str(m) + ' ')
	for t in range(len(average_7to7[m])):
		file3.write(str(round(average_7to7[m][t],2)) + ' ')
	file3.write('\n')
file3.close

d_max_kw.append(go.Scatter(x = x_dy, y = daily_kw_max,
						   name = runs[-1][2] + ' Daily Max Demand [kW]',
						   legendgroup = str(-1),
						   mode = 'markers+lines',
						   hoverlabel = dict(namelength = -1),
						   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

m_max_kw.insert(0, (go.Bar(x = x_m, y = monthly_kw_max,
					   	   name = runs[-1][2] + ' Monthly Max Demand [kW]',
					   	   opacity = 0.7, text = monthly_kw_max, textposition = 'auto',
						   legendgroup = str(-1),
					   	   hoverinfo = 'x+y+name', marker = dict(color = '#000000'),
					   	   hoverlabel = dict(namelength = -1))))

avg_sep.append(go.Scatter(x = x_24, y = average_7to7[8],
						  name = runs[-1][2] + ' September [kW]',
						  line = dict(color = '#000000', dash = 'dot', width = 1.5)))

avg_may.append(go.Scatter(x = x_24, y = average_7to7[4],
						  name = runs[-1][2] + ' May [kW]',
						  line = dict(color = '#000000', dash = 'dot', width = 1.5)))

avg_feb.append(go.Scatter(x = x_24, y = average_7to7[1],
						  name = runs[-1][2] + ' February [kW]',
						  line = dict(color = '#000000', dash = 'dot', width = 1.5)))

# Facility Load Duration Curves - Timestep Data [kW]
kw.sort(reverse = True)
ld_f.append(go.Scatter(x = x_ld_ts, y = kw,
					   name = runs[-1][2] + ' Facility Electricity Demand [kW]',
					   legendgroup = str(-1),
					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

b = np.array(kw)
filename6 = 'ld_' + runs[-1][0] + '.txt'
file6 = open(filename6,'w')
for z in b:
	file6.write(str(z) + '\n')
file6.close

a = np.linspace(0,8760*ts_per_hr,8760*ts_per_hr)
A = np.vstack([a, np.ones(len(a))]).T
#lin_fit = np.linalg.lstsq(A, b, rcond = None)
#print('', lin_fit[0])
#lin_fit_vals = [v * lin_fit[0][0] + lin_fit[0][1] for v in a]

# Electricity Demand - Plant [kW4]
#key =  dd.index['TimeStep', None, 'Electricity:Plant']
#kw = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
#pl_elec.append(go.Scatter(x = x_ts, y = kw,
#						  name = runs[-1][2] + ' Plant Electricity Demand [kW]',
#						  legendgroup = str(-1),
#					      hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
#						  line = dict(color = '#000000', dash = 'dot', width = 1.5)))

#for k in range(len(kw)):
#	# Discharge Period Plant Loads
#	if dchg[0] <= x_ts[k].hour < dchg[1]:
#		if x_ts[k].dayofweek not in wknd:
#			pl_dchg.append(kw[k])
#	# Charge Period Plant Loads
#	elif x_ts[k].hour >= chg[0] or x_ts[k].hour < chg[1]:
#		pl_chg.append(kw[k])

#	# Peak Period Plant Loads
#	if peak[0] <= x_ts[k].hour < peak[1]:
#		if x_ts[k].dayofweek not in wknd:
#			pl_pk.append(kw[k])
#	# Off Peak Periods Plant Loads
#	else:
#		pl_off.append(kw[k])

# Plant Load Duration Curves - Timestep Data [kW]
#kw.sort(reverse = True)
#pl_dchg.sort(reverse = True)
#pl_chg.sort(reverse = True)
#pl_pk.sort(reverse = True)
#pl_off.sort(reverse = True)

#ld_p.append(go.Scatter(x = x_ld_ts, y = kw,
#					   name = runs[-1][2] + ' Plant Electricity Demand [kW]',
#					   legendgroup = str(-1),
#					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
#					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

#ld_p_d.append(go.Scatter(x = x_ld_ts, y = pl_dchg,
#					   name = runs[-1][2] + ' Plant Discharge Electricity [kW]',
#					   legendgroup = str(-1),
#					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
#					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

#ld_p_c.append(go.Scatter(x = x_ld_ts, y = pl_chg,
#					   name = runs[-1][2] + ' Plant Charge Electricity [kW]',
#					   legendgroup = str(-1),
#					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
#					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

#ld_p_p.append(go.Scatter(x = x_ld_ts, y = pl_pk,
#					   name = runs[-1][2] + ' Plant Peak Electricity [kW]',
#					   legendgroup = str(-1),
#					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
#					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

#ld_p_o.append(go.Scatter(x = x_ld_ts, y = pl_off,
#					   name = runs[-1][2] + ' Plant Off-Peak Electricity [kW]',
#					   legendgroup = str(-1),
#					   hoverlabel = dict(namelength  = -1), hoveron = 'points+fills',
#					   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

# Electricity Demand - Chillers [kW]
key = dd.index['TimeStep', chill_name, 'Chiller Electric Energy']
kw = [j * 2.77778e-7 * ts_per_hr for j in data[key]]
ch_elec.append(go.Scatter(x = x_ts, y = kw,
						  name = runs[-1][2] + ' Chiller Electricity [kW]',
						  legendgroup = str(-1),
						  hoverlabel = dict(namelength = -1), hoveron = 'points+fills',
						  line = dict(color = '#000000', dash = 'dot', width = 1.5)))

# Total Chiller Electricity for Run Period
elec_chiller = sum(kw)
print(' Chiller Annual Electricity [kWh]: ', elec_chiller / ts_per_hr)
avg_cop = cooling_total / elec_chiller
print(' Average Chiller COP (full year): ', avg_cop)

# Chiller Average COP During Occupied Hours
occ_elec_chiller = 0
occ_cooling = 0
occ_runtime = 0

for k in range(len(kw)):
	if dchg[0] <= x_ts[k].hour < dchg[1]:
		if x_ts[k].dayofweek not in wknd:
			if cooling_chiller[k] > 0:
				occ_elec_chiller += kw[k]
				occ_cooling += cooling_chiller[k] / 1000
				occ_runtime += 1 / ts_per_hr

occ_cop = occ_cooling/occ_elec_chiller
print(' Average Chiller COP During Occupied Hours: ', occ_cop)
print(' Chiller Runtime During Occupied Hours: ', occ_runtime)

# Chiller Load Duration Curves - TimeStep Data [kW]
kw.sort(reverse = True)
ld_chill.append(go.Scatter(x = x_ld_ts, y = kw,
						   name = runs[-1][2] + ' Chiller Electricity [kW]',
						   legendgroup = str(-1),
						   hoverlabel = dict(namelength = -1),
						   line = dict(color = '#000000', dash = 'dot', width = 1.5)))

# Return Temps [C]
#key = dd.index['TimeStep', 'CHILLED WATER LOOP SUPPLY INLET NODE', 'System Node Temperature']
#return_temp.append(go.Scatter(x = x_ts, y = data[key],
#							  name = runs[-1][2] + ' Return Water Temp [C]',
#							  legendgroup = str(-1),
#							  hoverlabel = dict(namelength = -1)))

# Supply Temps [C]
#supply_temp.append(go.Scatter(x = x_ts, y = data[key],
#							  name = runs[-1][2] + ' Supply Water Temp [C]',
#							  legendgroup = str(-1),
#							  hoverlabel = dict(namelength = -1)))

print(' Complete.\n')


## Create Figures
print('Creating Figures.\n')

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

# Fig 1 - Cooling Rates and Ice SoC
if f1:
	fig = subplots.make_subplots(rows = 3, cols = 1, shared_xaxes = True,
	                          	subplot_titles = ('Cooling Rates [tons]','Ice Tank States of Charge [-]',
								'Chiller Limiter Flag'))

	for i in range(len(ch_a)):
		fig.append_trace(ch_a[i],1,1)

	for i in range(len(ice_a)):
		fig.append_trace(ice_a[i],1,1)

	fig.append_trace(ch_cool[-1],1,1)

	for i in range(len(ice_soc)):
		fig.append_trace(ice_soc[i],2,1)

	for i in range(len(limiter)):
		fig.append_trace(limiter[i],3,1)

	fig['layout'].update(template = standard_template, height = 1000)
	plotly.offline.plot(fig, filename = 'rates_soc.html')

# Fig 2 - Stacked Area Plot Totalling Ice and Chiller Cooling Rates
if f2:
	fig = subplots.make_subplots(rows = len(runs)-1, cols = 1, shared_xaxes = True,
							  subplot_titles = [i[2] for i in runs[0:-1]])

	for x in range(1,len(runs)):
		fig.append_trace(ch_a[x-1],x,1)
		fig.append_trace(ice_a[x-1],x,1)
		fig.append_trace(ch_cool[-1],x,1)

	fig['layout'].update(height = 300*len(runs))
	fig['layout'].update(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
						 yaxis = dict(showgrid = True, gridcolor = 'rgb(203,203,203)'))

	plotly.offline.plot(fig, filename = 'stacks.html')

# Fig 3 - Electricity Use Profiles
if f3:
	fig = subplots.make_subplots(rows = 2, cols = 1, shared_xaxes = True,
								subplot_titles = ('Facility Demand [kWe]', 'Chiller Demand [kWe]'))

	for i in range(len(elec)):
		fig.append_trace(elec[i],1,1)

	for i in range(len(ch_elec)):
		fig.append_trace(ch_elec[i],2,1)

	#fig['layout'].update(title = title_text)
	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'elec.html')

# Fig 4 - Daily Unused Ice
if f4:
	fig = subplots.make_subplots(rows = 2, cols = 1, shared_xaxes = False,
							  	subplot_titles = ('Daily Unused Ice Capacity [ton-hours]', 'Ice Tank State of Charge'))

	for i in range(len(d_soc_avail)):
		fig.append_trace(d_soc_avail[i],2,1)

	for i in range(len(ice_soc)):
		fig.append_trace(ice_soc[i],1,1)

	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'unused_ice.html')

# Fig 5 - Return Water Temps
if f5:
	fig = subplots.make_subplots(rows = 2, cols = 1, shared_xaxes = True)

	for i in range(len(return_temp)):
		fig.append_trace(return_temp[i],2,1)

	for i in range(len(supply_temp)):
		fig.append_trace(supply_temp[i],1,1)

	for i in range(len(ice_sp)):
		fig.append_trace(ice_sp[i],1,1)

	for i in range(len(ch_sp)):
		fig.append_trace(ch_sp[i],1,1)

	plotly.offline.plot(fig, filename = 'return_temps.html')

# Fig 6 - Load Duration Curves
if f6:
	fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = False)
							  #subplot_titles = ('Facility [kWe]',
							  #					'Chiller [kWe]'))
												#'Cooling Plant [kWe]',
							  					#'Cooling Plant - Ice Dischage Hours Only (09-21 Weekdays) [kWe]',
												#'Cooling Plant - Ice Charge Hours Only [kWe]',
												#'Cooling Plant - On-Peak Hours Only (16-21 Weekdays) [kWe]',
												#'Cooling Plant - Off-Peak Hours Only [kWe]'))

	for i in range(len(ld_f)):
		fig.append_trace(ld_f[i],1,1)

	#for i in range(len(ld_chill)):
	#	fig.append_trace(ld_chill[i],2,1)

	#for i in range(len(ld_p)):
	#	fig.append_trace(ld_p[i],2,1)

	#for i in range(len(ld_p_d)):
	#	fig.append_trace(ld_p_d[i],3,1)

	#for i in range(len(ld_p_c)):
	#	fig.append_trace(ld_p_c[i],4,1)

	#for i in range(len(ld_p_p)):
	#	fig.append_trace(ld_p_p[i],5,1)

	#for i in range(len(ld_p_o)):
	#	fig.append_trace(ld_p_o[i],6,1)

	fig['layout'].update(title = 'Load Duration Curves', template = standard_template)
	fig.update_xaxes(title_text = 'Number of 15-Minute Timesteps in Year')
	fig.update_yaxes(title_text = '[kWe]')
	plotly.offline.plot(fig, filename = 'load_duration.html')

# Fig 7 - Max Demand Curves
if f7:
	fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = False)
							  #subplot_titles = ('Daily Max Facility Demand [kWe]','Monthly Max Facility Demand [kWe]'))

	#for i in range(len(d_max_kw)):
	#	fig.append_trace(d_max_kw[i],1,1)

	for i in range(len(m_max_kw)):
		fig.append_trace(m_max_kw[i],1,1)

	#fig['layout'].update(barmode = 'overlay')
	fig['layout'].update(title = 'Maximum Facility Monthly Demand', template = standard_template)
	fig.update_yaxes(title_text = 'kWe')
	plotly.offline.plot(fig, filename = 'max_kw.html')

# Fig 8 - Average Day Electricity Profiles
if f8:
	fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = False,
							  subplot_titles = (#'Average May Profile [kWe]',
												'Average September Profile [kWe]'))
												#'Average February Profile [kWe]'))

	#for i in range(len(avg_may)):
	#	fig.append_trace(avg_may[i],1,1)

	for i in range(len(avg_sep)):
		fig.append_trace(avg_sep[i],1,1)

	#for i in range(len(avg_feb)):
	#	fig.append_trace(avg_feb[i],3,1)

	fig['layout'].update(title = title_text, xaxis = dict(dtick = 1), xaxis2 = dict(dtick = 1), xaxis3 = dict(dtick = 1),
						 height = 1000)
	fig['layout'].update(template = standard_template)
	plotly.offline.plot(fig, filename = 'avg_months.html')

print('Script Finished.')
