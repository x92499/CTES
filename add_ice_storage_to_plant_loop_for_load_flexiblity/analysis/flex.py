# Facility Load Flexibilty Calculations for Ice Storage
# by Karl Heine, Mines, 9/2019

# Description: This python script loads an eso and performs calculations at each timestep for the potential of the
# facility to reduce its max kW and total kWh over specified "future" time horizons. The results are then reported
# in .csv/.txt output and plotted as .html interactive graphics.

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

# External Functions
from performance import ice_performance

# Program Control
exp = False		#Export Results
f1 = False		#Plot Results for Flex
add = True		#Perform Load Add Calcs

#-----------------------------------------------------------------------------------------------------------------------
## Model and Analysis Parameter Definitions

# Define Filepath
filepath = os.getcwd() + '/esos/'

# Define Model Parameters
filename = 'SS47L15.eso'	#Secondary School, CZ 2A, ice meets up to 30% of design load, chiller downsize applied
ice_cap = 2000					#ton-hours
chiller_cap = 347				#tons
chiller_COP = 2.80				#nominal chiller COP
min_cap = 0.15 * chiller_cap	#min PLR * nominal chiller capacity
descriptor = 'Secondary School in CZ 2A'

# Load File
print('Loading File: ' + filename)
dd, data = esoreader.read(filepath + filename)

# Define Chiller/Ice Tank Names for ESO Data Directory Inspection
ice_name = 'THERMAL STORAGE ICE DETAILED 1'
chill_name = '90.1-2010 AIRCOOLED WITHCONDENSER  CHILLER 0 456TONS 1.3KW/TON'

# Define Run Period
run_start = pd.datetime(2006,1,1,0)				#Hour 0 on Jan 1
run_end = pd.datetime(2006,12,31,23,59)			#Hour 23:59 on Dec 31
ts_per_hr = 4									#15 minute simulation timestep !!!! Adjust date_range objects too!
x_ts = pd.date_range(start = run_start, end = run_end, freq = '15min')		#Vector of timestamps for simulation run pd

# Define Analysis Peirod
an_start = pd.datetime(2006,1,1,0)				#Analysis Start Hour
an_end = pd.datetime(2006,12,31,17)			#Analysis Finish Hour
an_pd = []										#Index range of analysis period - empty
idx = 0
for x in x_ts:
	if x == an_start:
		an_pd.append(idx)
	if x == an_end:
		an_pd.append(idx)
	idx += 1

x_an = pd.date_range(start = x_ts[an_pd[0]], end = x_ts[an_pd[1]], freq = '15min')	#Timestamp vector - for plotting
print(x_an[0])

# Define Occupied Hours and Days
occ_flag = 0
occ_hrs = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]		#Occupied from 08:00 through 20:00 (Pandas Hours Range from 0-23)
occ_days = [0, 1, 2, 3, 4]		#Excludes Sat and Sun

# Define Flex Windows - number of future hours over which flexibilty is required
window = [0.5, 1, 2, 3, 4, 5, 6]

# Define Variables and Arrays for Load Shed Calcs
kw_tr = [[None for i in range(len(x_an))] for j in range(len(window))]
kw_future_tr = [[None for i in range(len(x_an))] for j in range(len(window))]
kwh_tr = [[None for i in range(len(x_an))] for j in range(len(window))]
post_flex_soc_tr = [[None for i in range(len(x_an))] for j in range(len(window))]
no_flex_soc_tr = [[None for i in range(len(x_an))] for j in range(len(window))]
occ_counter = 0
no_rate_counter = [0 for j in range(len(window))]
no_soc_counter =[0 for j in range(len(window))]
total_counter = [0 for j in range(len(window))]
flex_counter = [0 for j in range(len(window))]
flex_future_counter = [0 for j in range(len(window))]
occ_flex_counter = [0 for j in range(len(window))]
avg_flex = [0 for j in range(len(window))]
avg_flex_future = [0 for j in range(len(window))]
avg_occ_flex = [0 for j in range(len(window))]
avg_kwh_flex = [0 for j in range(len(window))]

#Define Variables and Arrays for Load Add Clacs
add = [[None for i in range(len(x_an))] for j in range(len(window))]
add_occ = [[None for i in range(len(x_an))] for j in range(len(window))]
add_counter = [0 for j in range(len(window))]
add_occ_counter = [0 for j in range(len(window))]
avg_add = [0 for j in range(len(window))]
avg_add_occ = [0 for j in range(len(window))]

#-----------------------------------------------------------------------------------------------------------------------
## Load Required Variables

#facility electric energy [J -> kW]
key = dd.index['TimeStep', None, 'Electricity:Facility']
pwr_facil = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#HVAC electric energy [J -> kWh]
key = dd.index['TimeStep', None, 'Electricity:HVAC']
pwr_hvac = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#cooling electric energy [J -> kW]
key = dd.index['TimeStep', None, 'Cooling:Electricity']
pwr_cool = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#pump electric energy [J -> kW]
key = dd.index['TimeStep', None, 'Pumps:Electricity']
pwr_pump = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#fan electric energy [J -> kW]
key = dd.index['TimeStep', None, 'Fans:Electricity']
pwr_fan = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#chiller electric energy [J -> kW] - incl condenser unit
key = dd.index['TimeStep', chill_name, 'Chiller Electric Energy']
pwr_chill = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#plant total electric energy [J -> kW] - all Plants!
key = dd.index['TimeStep', None, 'Electricity:Plant']
pwr_plant = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#ice tank ancillary electric energy [J -> kW]
key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage Ancillary Electric Energy']
pwr_ice = [j * 2.77778e-7 * ts_per_hr for j in data[key]]

#chiller cooling rate [W -> tons]
key = dd.index['TimeStep', chill_name, 'Chiller Evaporator Cooling Rate']
rate_chill = [w * 0.0002843451 for w in data[key]]

#ice tank cooling rate [W -> tons]
key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage Cooling Discharge Rate']
rate_dchg = [w * 0.0002843451 for w in data[key]]

#ice tank charging rate [W -> tons]
key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage Cooling Charge Rate']
rate_chg = [w * 0.0002843451 for w in data[key]]

#ice state of charge [-]
key = dd.index['TimeStep', ice_name, 'Ice Thermal Storage End Fraction']
soc = data[key]

#drybulb temperature [C]
key = dd.index['TimeStep', 'Environment', 'Site Outdoor Air Drybulb Temperature']
tdb = data[key]

#wetbulb temperature [C]
key = dd.index['TimeStep', 'Environment', 'Site Outdoor Air Wetbulb Temperature']
twb = data[key]

#return water temperature [C]
key = dd.index['TimeStep', 'CHILLED WATER LOOP SUPPLY INLET NODE', 'System Node Temperature']
return_temp = data[key]

#supply water temperature [C]
key = dd.index['TimeStep', 'CHILLED WATER LOOP SETPOINT SCHEDULE (NEW)', 'Schedule Value']
supply_temp = data[key]

#facility electric power w/o chiller [kW]
pwr_facil_wo_chill = [pwr_facil[i] - pwr_chill[i] for i in range(len(pwr_facil))]

#total cooling rate - chiller and ice [tons]
rate_cool = [0] * len(rate_chill)
for i in range(len(rate_chill)):
	if rate_chg[i] == 0:
		rate_cool[i] = rate_chill[i] + rate_dchg[i]
	else:
		rate_cool[i] = rate_chill[i] - rate_chg[i]

print(' Data Successfully Loaded.\n')

#-----------------------------------------------------------------------------------------------------------------------
## Calculations
print('Performing Calculations')

# Iterate Over Every Timestep in Analysis Period
for t in range(an_pd[0], an_pd[1]):

	# Determine if t is in occupied hour
	if x_ts[t].dayofweek in occ_days and x_ts[t].hour in occ_hrs:
		occ_flag = 1
		occ_counter += 1
	else:
		occ_flag = 0

	# Iterate Analysis over Every Flex Window
	for w in window:

		e_flag = 0			# Sufficient energy in ice tank flag
		p_flag = 0			# Sufficient discharge capacity (power) flag
		flag = [0, 0, 0]	# Charge/discharge indicator flag (start, peak, end)

		# Determine Number of Timesteps in Analysis Period
		steps = int(w * ts_per_hr)

		# Integrate and Find Max Cooling and Electric Loads
		c = 0
		load_cool_to_pk = 0
		e = 0
		e_no_chill = 0
		load_e_no_chill = 0
		load_cool = 0		# Total cooling energy required over analysis period [ton-hours]
		pk_cool = 0			# Peak cooling rate required over analysis period [tons]
		pk_c_ts = 0			# Timestep index of peak cooling rate [-]
		load_elec = 0		# Total facility energy required over analysis period [kWh]
		pk_elec = 0			# Peak facility power required over analysis period [kW]
		pk_e_ts = 0			# Timestep index of peak facility power [-]

		#(Chiller Cooling Rate + Ice Cooling Rate) * ts [ton-hours]
		c = rate_cool[t:t+steps]						# Subsection of total cooling load (provided) profile [tons]
		load_cool = sum(c) / ts_per_hr					# Convert tons into ton-hours of cooling
		pk_cool = max(c)								# Max tons of cooling in analysis period
		pk_c_ts = t + c.index(pk_cool) + 1				# Timestep of max cooling
		load_cool_to_pk = sum(rate_cool[t:pk_c_ts])		# Cooling load up to peak cooling timestep

		#Facility Power * ts [kWh]
		e = pwr_facil[t:t+steps]						# Subsection of facility power curve [kW]
		e_no_chill = pwr_facil_wo_chill[t:t+steps]		# Subsection of facility power w/o chiller curve [kW]
		load_elec = sum(e) / ts_per_hr					# Convert kW into kWh values using timesteps/hour
		load_e_no_chill = sum(e_no_chill) / ts_per_hr	# Convert kW into kWh values
		pk_elec = max(e)								# Max kW for facility in analysis period
		pk_e_ts = t + e.index(pk_elec) + 1				# Timestep of max kW

		# Check Cooling Energy Capacity Remaining
		avail_cap = ice_cap * soc[t]
		if avail_cap > load_cool:
			soc_at_end = (avail_cap - load_cool) / ice_cap
			e_flag = 1
		else:
			no_soc_counter[window.index(w)] += 1

		# Set Charge/Discharge Flag
		idx = 0
		for i in [t, pk_c_ts, t+steps]:
			if rate_chg[i] > 0:
				flag[idx] = 1
			elif rate_dchg[i] > 0:
				flag[idx] = 0
			else:
				flag[idx] = -1

		# Check Cooling Rate Ice Can Provide
		soc_at_peak = (avail_cap - load_cool_to_pk) / ice_cap
		max_dchg = [0, 0, 0]		# @ start, peak, and end
		max_dchg[0] = ice_performance(soc[t], return_temp[t], supply_temp[t], ice_cap, 0)
		max_dchg[1] = ice_performance(soc_at_peak, return_temp[pk_c_ts], supply_temp[pk_c_ts], ice_cap, 0)
		max_dchg[2] = ice_performance(soc_at_end, return_temp[t+steps], supply_temp[t+steps], ice_cap, 0)

		# If cooling rates can meet start, max, and average, then there is no cooling rate restriction on the DR shed
		# All units in tons
		if (max_dchg[0] + max_dchg[2]) / 2 * w >= load_cool \
		and max_dchg[1] > pk_cool and max_dchg[2] > c[-1]:
			p_flag = 1
		else:
			no_rate_counter[window.index(w)] += 1

		# If ice can meet both energy and rate requirements, remove chiller power from load to calculate flex potential
		if e_flag and p_flag:

			#Total flex possible counter
			total_counter[window.index(w)] += 1

			# Calculate the projected kWh shaved over analysis window
			kwh_flex = load_elec - load_e_no_chill

			# Calc kW reduction relative to current timestep and to analysis window
			new_max_kw = max(pwr_facil_wo_chill[t:t+steps])
			kw_flex = pwr_facil[t] - new_max_kw
			kw_flex_future = pk_elec - new_max_kw

			# Do not include periods when no kW reduction is provided (relative to pk_elec)
			if kw_flex_future <= 0:
				kw_flex_future = 0
			else:
				flex_future_counter[window.index(w)] += 1
				avg_flex_future[window.index(w)] += kw_flex_future

				# Calculate shed flex during occupied hours only
				if occ_flag == 1:
					occ_flex_counter[window.index(w)] += 1
					avg_occ_flex[window.index(w)] += kw_flex_future
					avg_kwh_flex[window.index(w)] += kwh_flex

			# Calculate flexibility relative to current timestep power as well
			if kw_flex <= 0:
				kw_flex = 0
			else:
				flex_counter[window.index(w)] += 1
				avg_flex[window.index(w)] += kw_flex

		else:	# No flexiblity assumed if ITS cannot meet rate or energy requirements
			kw_flex = 0
			kw_flex_future = 0
			kwh_flex = 0

		# Update trace variables for shed plots
		kw_tr[window.index(w)][(t-an_pd[0])] = -kw_flex
		kw_future_tr[window.index(w)][(t-an_pd[0])] = kw_flex_future
		kwh_tr[window.index(w)][(t-an_pd[0])] = kwh_flex
		post_flex_soc_tr[window.index(w)][(t-an_pd[0])] = soc_at_end
		no_flex_soc_tr[window.index(w)][(t-an_pd[0])] = soc[t+steps]

		if add:
			# Average cooling required over analysis period
			c_bar = sum(c) / steps			# average tons

			# Average cooling provided by chiller over analysis period (excluding charging!)
			c_chill = []
			for z in range(t,t+steps):
				c_chill.append(rate_chill[z] - rate_chg[z])
			c_bar_chill = sum(c_chill) / steps		# average tons

			# If chiller capacity is nominally sufficient, add load based on nominal COP (convert tons to kW)
			if c > c_chill:
				add_counter[window.index(w)] += 1
				if c_bar_chill <= chiller_cap:
					add[window.index(w)][(t-an_pd[0])] = (c_bar - c_bar_chill) / 0.2843451 / chiller_COP
				elif c_bar_chill > chiller_cap:
					add[window.index(w)][(t-an_pd[0])] = (chiller_cap - c_bar_chill) / 0.2843451 / chiller_COP

				if occ_flag:
					add_occ_counter[window.index(w)] += 1
					if c_bar_chill <= chiller_cap:
						add_occ[window.index(w)][(t-an_pd[0])] = (c_bar - c_bar_chill) / 0.2843451 / chiller_COP
					elif c_bar_chill > chiller_cap:
						add_occ[window.index(w)][(t-an_pd[0])] = (chiller_cap - c_bar_chill) / 0.2843451 / chiller_COP
				else:
					add_occ[window.index(w)][(t-an_pd[0])] = 0

				# Calc the average add terms
				avg_add[window.index(w)] += add[window.index(w)][(t-an_pd[0])]
				avg_add_occ[window.index(w)] += add_occ[window.index(w)][(t-an_pd[0])]

			elif c <= c_chill:
				add[window.index(w)][(t-an_pd[0])] = 0

# Calculate the Average Flexibility Provided by ITS
for i in range(len(window)):
	if flex_counter[i] != 0:
		avg_flex[i] = avg_flex[i] / flex_counter[i]
		avg_flex_future[i] = avg_flex_future[i] / flex_future_counter[i]
		avg_kwh_flex[i] = avg_kwh_flex[i] / occ_flex_counter[i]

	if occ_flex_counter[i] != 0:
		avg_occ_flex[i] = avg_occ_flex[i] / occ_flex_counter[i]

	if add_counter[i] != 0:
		avg_add[i] = avg_add[i] / add_counter[i]

	if add_occ_counter[i] != 0:
		avg_add_occ[i] = avg_add_occ[i] / add_occ_counter[i]


# Print Desired Outputs
print('Flex Counter:', [(i / ts_per_hr) for i in flex_counter])
print('Average Flex:', avg_flex)
print('Average Flex (Future):', avg_flex_future)
print('Total Hours:', len(x_an) / 4)
print('Occupied Flex Counter:', [(i / ts_per_hr) for i in occ_flex_counter])
print('Average Occupied Flex:', avg_occ_flex)
print('Occupied Hours:', occ_counter / 4)
print('Total Yes Flex Count:', [(i / ts_per_hr) for i in total_counter])
print('No Rate Count:', [(i / ts_per_hr) for i in no_rate_counter])
print('No SOC Count:', [(i / ts_per_hr) for i in no_soc_counter])
print('Average kWh Flex:', avg_kwh_flex)
print('Average Add kW:', avg_add)
print('Average Occ Add kW:', avg_add_occ)
print('Add Hours:', add_counter)
print('Add Occupied Hours:', add_occ_counter)


print(' Calculations Complete.\n')

#-----------------------------------------------------------------------------------------------------------------------
## Create Figures
print('Creating Figures')

standard_template = go.layout.Template(
	layout = go.Layout(
		height = 650, width = 1400,
		title_font = dict(family = 'Rockwell', size = 28),
		xaxis = dict(
			title_font = dict(family = 'Rockwell', size = 24),
			tickfont = dict(family = 'Rockwell', size = 20),
			showgrid = True,
			gridcolor = 'rgb(203,203,203)'
			),
		yaxis = dict(
			title_font = dict(family = 'Rockwell', size = 24),
			tickfont = dict(family = 'Rockwell', size = 20),
			showgrid = True,
			gridcolor = 'rgb(203,203,203)'
			),
		paper_bgcolor = 'rgba(0,0,0,0)', plot_bgcolor = 'rgba(0,0,0,0)',
		#legend = dict(x = 0.5, y = 1.1, font = dict(family = 'Rockwell', size = 18)),
		hovermode = 'closest'
	)
)

kw_trace = []
for i in range(len(kw_tr)):
	kw_trace.append(go.Scatter(x = x_an, y = kw_tr[i], name = f'{window[i]} Hr kW Flex', legendgroup = i))

kw_future_trace = []
for i in range(len(kw_future_tr)):
    kw_future_trace.append(go.Scatter(x = x_an, y = kw_future_tr[i],
									name = f'{window[i]} Hr kW Flex (Future)', legendgroup = i))

kwh_trace = []
for i in range(len(kwh_tr)):
	kwh_trace.append(go.Scatter(x = x_an, y = kwh_tr[i], name = f'{window[i]} Hr kWh Flex', legendgroup = i))

no_flex_soc_trace = []
for i in range(len(no_flex_soc_tr)):
	no_flex_soc_trace.append(go.Scatter(x = x_an, y = no_flex_soc_tr[i], name = f'{window[i]} Hr SOC No Flex',
										legendgroup = i))

post_flex_soc_trace = []
for i in range(len(post_flex_soc_tr)):
	post_flex_soc_trace.append(go.Scatter(x = x_an, y = post_flex_soc_tr[i], name = f'{window[i]} Hr SOC Post Flex',
										legendgroup = i))

add_trace = []
for i in range(len(add)):
	add_trace.append(go.Scatter(x = x_an, y = add[i], name = f'{window[i]} Hr Add',
										legendgroup = i))

pwr_trace = go.Scatter(x = x_an, y = pwr_facil[an_pd[0]:an_pd[1]], name = 'Facil Pwr [kW]')

chill_trace = go.Scatter(x = x_an, y = pwr_chill[an_pd[0]:an_pd[1]], name = 'Chiller Pwr [kW]')

# Fig 1
if f1:
	fig = subplots.make_subplots(rows = 5, cols = 1, shared_xaxes = True,
	                       		subplot_titles = ('Facility Electric Load [kW]','kW Flex (Current)',
								 				'kW Flex (Future)', 'kWh Flex', 'Post SOC'))

	fig.append_trace(pwr_trace,1,1)
	fig.append_trace(chill_trace,1,1)

	for i in range(len(kw_trace)):
		fig.append_trace(kw_trace[i],2,1)

	for i in range(len(kw_future_trace)):
		fig.append_trace(kw_future_trace[i],3,1)

	for i in range(len(kwh_trace)):
		fig.append_trace(kwh_trace[i],4,1)

	for i in range(len(no_flex_soc_trace)):
		fig.append_trace(no_flex_soc_trace[i],5,1)

	for i in range(len(post_flex_soc_trace)):
		fig.append_trace(post_flex_soc_trace[i],5,1)

	#fig['layout'].update(template = standard_template, showlegend = False)
	plotly.offline.plot(fig, filename = 'flex.html')

# Add Plot
fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = True)

fig.append_trace(pwr_trace,1,1)
for i in range(len(add_trace)):
	fig.append_trace(add_trace[i],1,1)

plotly.offline.plot(fig, filename = 'addflex.html')

# Add and Shed Plot - Bounding!
fig = subplots.make_subplots(rows = 1, cols = 1, shared_xaxes = True)

fig.append_trace(add_trace[1],1,1)
fig.append_trace(kw_trace[1],1,1)

plotly.offline.plot(fig, filename = 'flexbound.html')


print(' Figures Complete.\n')
print('Script Finished.')
