# -*- coding: utf-8 -*-
# This first one is potentially too complicated and may take a lot of
# testing and calibrating

# import numpy as np

def f_to_k(fahrenheit):
    return (fahrenheit - 32) * 5 / 9 + 273.15

def smart_temp_check(body_temp,envi_temp,age,weight):
    '''Takes inputs of body temperature and environmental temperature
    and returns a string containing 'high','ok', or 'low' to indicate
    the child's condition. Temperatures should be in Kelvin, age in
    years, and weight in kilograms.'''
    # Radiation as the most important heat loss mechanism
    # head surface area - depends on age, estimate by weight
    bsa = 4.688*(weight*1000)**(0.8168-0.0154*np.log10(weight*1000)) #cm^2
    hsa = (bsa/10000)*.6  #m^2 and adjustment
    emis = 0.97 # Constant - skin emmisivity
    sb_const = 5.67 * 10**-8 # Stefan-Boltzmann constant
    radiation_rate = emis * sb_const * hsa * (body_temp**4 - envi_temp**4)
    
    # Calculate heat production
    #(using http://cdn.intechopen.com/pdfs-wm/30408.pdf)
    if (age < 2):
        metab = age*0.25 + 2
    elif (age < 4):
        metab = 2.5
    elif (age == 18):
        metab = 1
    else:
        metab = (age-3.5)*-0.33 + 2.5
        
    metab = metab * weight # in kcal/h
    metab = metab * 1.163 # in Watts
    
    if ((radiation_rate - metab) > 1.5):
        out = 'low'
    elif ((metab - radiation_rate) > 1.5):
        out = 'high'
    else:
        out = 'ok'
        
    return out
    
# Here is a simpler but less scientific alternative
def simple_temp_check(body_temp,envi_temp):
    # Set bounds (replace with the real numbers)
    low_temp = 98
    high_temp = 100
    if (body_temp <= low_temp and envi_temp <= 70):
        out = 'low'
    elif (body_temp >= high_temp and envi_temp >= 80):
        out = 'high'
    else:
        out = 'ok'
        
    return out