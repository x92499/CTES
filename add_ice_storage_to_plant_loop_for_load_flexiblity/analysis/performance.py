# Ice Performance Curve Function
# Karl Heine, 9/2019

# This function calculates the maximum ice discharge rate
# Ref. E+ Engineering Reference, section 15.1.2, (p. 791 in v. 9.1.0)

def ice_performance (soc, return_temp, supply_temp, ice_cap, flag):

    # Import req'd packages
    import numpy as np

    # Ice Storage Curve Parameters
    c = [0, 0.09, -0.15, 0.612, -0.324, -0.216]         # Same Coefficients for both charge and discharge in OS default
    x_rng = [0, 1]          # Range on SOC Variable Inputs
    y_rng = [0, 9.9]        # Range on DTlm* Variable Inputs
    freeze_temp = 0         # Freezing temperature of the ice storage [C]
    DTlm_nom = 10           # Nominal delta T, must equal 10C based on E+ Engineering Reference Guide

    # Set Charge or Discharge values based on flag
    if flag == 0:           # Discharging
        x = (1 - soc)
    elif flag == 1:			# Charging - Incomplete!
        x = soc

    if (return_temp - freeze_temp) / (supply_temp - freeze_temp) >= 0:
        DTlm = (return_temp - supply_temp) / np.log((return_temp - freeze_temp) / (supply_temp - freeze_temp))
    else:
        DTlm = 0

    y = DTlm / DTlm_nom     # Non-dimensionalized DTlm value

    # Check limits on input variable values
    # x is either percent charged or percent discharged
    if x < x_rng[0]:
        x = x_rng[0]
    elif x > x_rng[1]:
        x = x_rng[1]

    # y is non-dimensionalized log mean temperature difference across ice heat exchanger
    if y < y_rng[0]:
        y = y_rng[0]
    elif y > y_rng[1]:
        y = y_rng[1]

    # Max rate of discharge from ice - neglect charging for now.
    q_star = (c[0] + (c[1] * x) + (c[2] * (x**2))) + ((c[3] + (c[4] * x) + (c[5] * (x**2))) * y)
    q = q_star * ice_cap / 1    # Divisor is timestep of performance curve [hr], assumed to be 1 hr.

    return q;
