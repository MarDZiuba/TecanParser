# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 16:19:55 2023

@author: Marina Dziuba
"""

#Importing libraries
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#import argparser as arg

'''
Here there will be code on parsing the user arguments. For now, the arguments
are given as set variables for simple tests 
'''
i = "04.07.17-06.07.17 MSR PmmH189 lux kinetics.xlsx"
o = "Result_test"
g = (69, 1219)
lux = (1222, 1320)
b = "A1"
rep = {"Clone1" : ("B2", "B4", "B6"), 
       "Clone2" : ("B8", "B10","C3"), 
       "Clone3" : ("C5", "C7", "C9"),
       "Clone4" : ("C11","D2", "D4"),
        "Clone5" : ("D6", "D8", "D10"),
        "Clone6" : ("E3", "E5", "E7"),
        "Clone7" : ("E9", "E11", "F2"),
        "Clone8" : ("F4", "F6", "F8"),
        "Clone9" : ("F10", "G3", "G5"),
        "Clone10" : ("G7", "G9", "G11")}
        
tecan_data = pd.read_excel(i)
#Test if the data are in the right orientation (must be horizontal layout)

try:
    test_horizontal = list(tecan_data.iloc[g[0]-1, 1:11])
    test_horizontal = [int(i) for i in test_horizontal]
    test_horizontal == [1,2,3,4,5,6,7,8,9,10] 
except:
    print("Error: the data in your Excel sheet is not arranged horizontally")
    sys.exit()

growth_data = tecan_data.iloc[(g[0]-2):(g[1]-1), :].reset_index(drop = True)
growth_df = pd.DataFrame(dtype="object")

#Extracting the time column and copying into the new df
 
for i, r in growth_data.iterrows():
    if r[0] == "Zeit [s]" or r[0] == "Time [s]":
        growth_df[0] = r.T
        break
growth_df.reset_index(drop = True, inplace = True)

#Transform time to hours
time_hr = growth_df.iloc[1:,0].divide(3600)
time_hr.loc[-1] = "Time [h]"
time_hr = time_hr.sort_index()
time_hr.reset_index(drop = True, inplace = True)
growth_df = pd.concat([growth_df, time_hr], axis=1, ignore_index=True)

#Funtion to extract the value measured in a certain well if multiple measuremens per 
#well were conducted 
def extract_values_with_multimeasurements(well, df):
    '''Extract the mean value of multiple measurements in a well. 
    Well should be passed as a string'''
    try:
        well_index = df[df["Application: Tecan i-control"] == well].index
    except:
        well_index = df[df["Programm: Tecan i-control"] == well].index
    
    well_values = df.iloc[well_index + 3, :]
    well_values_T = well_values.T #transposes the data from the selected row
    well_values_T.reset_index(drop = True, inplace = True)
    return  well_values_T

#Extracting the blank data from the raw data and adding them to the new df
blank_values = extract_values_with_multimeasurements(b, growth_data)
blank_values.iloc[0,0] = "Blank"

#Extracting the values for the wells specified by the user

for k, v in rep.items():
   for i in v:
       values = extract_values_with_multimeasurements(i, growth_data)
       values.iloc[1:,0] = values.iloc[1:,0].subtract(blank_values.iloc[1:, 0]) #subtract blank values from measurements
       values.iloc[0,0] =str(k + " : " + i)
       growth_df = pd.concat([growth_df, values], axis=1, ignore_index=True)        
   #Calculate mean value for the replicates 
   row_means = growth_df.iloc[1:, -len(v):].mean(axis = 1)
   #Calculate standard deviation for the replicates
   row_std = growth_df.iloc[1:, -len(v):].std(axis = 1)
   #Add mean value and std to the df
   growth_df = pd.concat([growth_df, row_means], axis=1, ignore_index=True)
   growth_df.iloc[0,-1] = str(k + " : " + "Mean value")
   growth_df = pd.concat([growth_df, row_std], axis = 1, ignore_index=True)
   growth_df.iloc[0,-1] = str(k + " : " + "St. dev")
  
#Pass the first row as colum names
growth_df.columns = growth_df.iloc[0]
growth_df = growth_df.drop(0)
growth_df.reset_index(drop = True, inplace = True)

#Correct any values lower than 0 to 0.01
growth_df[growth_df < 0] = 0.01

#Save the resulting df as excel table
excel = pd.ExcelWriter(o+".xlsx", engine = "xlsxwriter")
growth_df.to_excel(excel, sheet_name="Growth", index=False)
#Here might be also added luminescence or other measurements
# excel.close()

'''
Plotting the curves

'''

def combined_lineplot_w_shadows(replicates, df, xlabel, ylabel):
    '''Plot values as line plots with errors as shaded regions on a single plot
    by looping through columns and replicates passed by the user.
    Accepts a dictionary with replicate wells and a tidy pandas df with pre-calculated 
    meanvalue and st.dev. '''
    fig, ax = plt.subplots(figsize = (10, 8))
    plotted_means = []
    plotted_stds = []
    x = df['Time [h]'].astype(float)

    for k, v in replicates.items():
        for column in df.columns:
            if k + " : " + "Mean value" in column:
                y_mean = df[column].astype(float)
                plotted_means.append(y_mean)
                
                for std_column in df.columns:
                    if k in std_column and "St. dev" in std_column:
                        y_std = df[std_column].astype(float)
                        plotted_stds.append(y_std)
                        break
                    
        if len(plotted_means) == len(plotted_stds):
            for mean, std in zip(plotted_means, plotted_stds):
                error = 0.5 * std
                lower = mean - error
                upper = mean + error
                sns.lineplot(x=x, y=mean, ax=ax, label=mean.name.split(":")[0])
                ax.fill_between(x, lower, upper, alpha=0.2)
                
            plotted_means.clear()
            plotted_stds.clear()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

##Plotting growth data on a single combined plot##
sns.set_theme(palette = "colorblind", font_scale = 1, style = "whitegrid", font = "Verdana") 
xlabel = 'Time [h]'
ylabel = 'OD [AU]'
combined_lineplot_w_shadows(rep, growth_df, xlabel, ylabel)

plt.savefig(o + "_growth" + "_one_plot" + ".png", format = "png", dpi = 300)
plt.savefig(o + "_growth" + "_one_plot" + ".pdf", format = "pdf")
plt.savefig(o + "_growth" + "_one_plot" + ".svg", format = "svg")
plt.show()

##Plotting growth data as separate subplots##

# set plot properties using sns.set()
sns.set_theme(palette = "colorblind", font_scale = 1, style = "whitegrid", font = "Verdana")

#Set the size of the plots and margin sizes
plot_width = 6  # width of each subplot in inches
plot_height = 4  # height of each subplot in inches
space = 0.4  # desired spacing between subplots in inches
left = 0.1  # left margin in inches
right = 0.9  # right margin in inches
bottom = 0.1  # bottom margin in inches
top = 0.9  # top margin in inches

def optimum_grid(replicates, plot_width, plot_height, space, left, right, bottom, top):
    '''Calculates optimum number of rows and columns depending on the number of 
    replicates and pre-set margin sizes. '''
    
    # calculate the optimum number of rows and columns so that no more than 3 plots in one row are plotted
    nrows = int(len(rep.items()) / 3) + int(len(rep.items()) % 3 > 0)
    ncols = 3 if len(rep.items()) >= 3 else len(rep.items())    
    # Calculation of optimum figure size
    fig_width = ncols * plot_width + (ncols - 1) * space + left + right
    fig_height = nrows * plot_height + (nrows - 1) * space + bottom + top
    fig_size = (fig_width, fig_height)    
    return ncols, nrows, fig_size 

ncols, nrows, fig_size = optimum_grid(rep, plot_width, plot_height, space, left, right, bottom, top)

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=fig_size, sharey = False)
fig.subplots_adjust(hspace=0.5, wspace=0.5) # adjust the spacing between the subplots
xlabel = 'Time [h]'
ylabel = 'OD [AU]'

def separate_lineplots_with_shadows(replicates, df, ncols, xlabel, ylabel, same_yscale=True):
    '''Plot values in separate line plots with errors shown as shaded regions 
    by looping through columns and replicates passed by the user.
    Accepts a dictionary with replicate wells and a tidy pandas df with pre-calculated 
    meanvalue and st.dev. '''
    
    x = df['Time [h]'].astype(float)
    plotted_means = []
    plotted_stds = []

    for k, v in replicates.items():
        for column in df.columns:
            if k + " : " + "Mean value" in column:
                y_mean = df[column].astype(float)         
                plotted_means.append(y_mean)                
                for std_column in df.columns:
                    if k in std_column and "St. dev" in std_column:
                        y_std = df[std_column].astype(float)
                        plotted_stds.append(y_std)
                        break
    #Finding min and max of all data to set y axis to the same scale
    if same_yscale is True:
        concat_means = pd.concat(plotted_means, axis = 0)
        concat_std = pd.concat(plotted_stds, axis = 0)
        y_mean_min = concat_means.min()
        y_mean_max = concat_means.max()
        y_std_min = concat_std.min()
        y_std_max = concat_std.max()
        y_min = y_mean_min-0.5*y_std_min
        y_max = y_mean_max + 0.5*y_std_max
    else: 
        pass

    for i, (mean, std) in enumerate(zip(plotted_means, plotted_stds)):
        c = i % ncols
        r = i // ncols
        error = 0.5 * std
        lower = mean - error
        upper = mean + error
        ax = axes[r, c]
        sns.lineplot(x=x, y=mean, ax=ax, label=mean.name.split(":")[0])
        ax.fill_between(x, lower, upper, alpha=0.2)
        if same_yscale is True:
            ax.set_ylim(y_min, y_max)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    plotted_means.clear()
    plotted_stds.clear()
    
    if ncols * nrows > len(rep.items()):
        n_to_hide = ncols * nrows - len(rep.items())
        while n_to_hide > 0:    
            axes[nrows - 1, n_to_hide].set_visible(False)
            n_to_hide = n_to_hide - 1

fig.tight_layout()

separate_lineplots_with_shadows(rep, growth_df, ncols, xlabel, ylabel, False)
plt.show()
#Hide the blank subplots 
# if ncols * nrows > len(rep.items()):
#     n_to_hide = ncols * nrows - len(rep.items())
#     while n_to_hide > 0:    
#         axes[nrows - 1, n_to_hide].set_visible(False)
#         n_to_hide = n_to_hide - 1
fig.tight_layout()

plt.savefig(o + "_growth" + "_sep_plot" + ".png", format = "png", dpi = 300)
plt.savefig(o + "_growth" + "_sep_plot" + ".pdf", format = "pdf")
plt.savefig(o + "_growth" + "_sep_plot" + ".svg", format = "svg")
plt.show()

##Processing luminescence data##

lux_data = tecan_data.iloc[(lux[0]-2):(lux[1]-1), :].reset_index(drop = True)
lux_df = pd.DataFrame(dtype="object")

#Adding the time columns to luminescence results. Here, the same loops are repeated as for growth in case
#luminescence data are processed independently of growth

for i, r in lux_data.iterrows():
    if r[0] == "Zeit [s]" or r[0] == "Time [s]":
        lux_df[0] = r.T
        break
lux_df.reset_index(drop = True, inplace = True)

#Transform time to hours
time_hr = lux_df.iloc[1:,0].divide(3600)
time_hr.loc[-1] = "Time [h]"
time_hr = time_hr.sort_index()
time_hr.reset_index(drop = True, inplace = True)
lux_df = pd.concat([lux_df, time_hr], axis=1, ignore_index=True)

#Funtion to extract the value measured in a certain well if single measurement per 
#well was conducted, like often for luminescence 
def extract_values_with_monomeasurements(well, df):
    '''Extract the values measured in a well if single measurement was conducted. 
    Well should be passed as a string'''
    try:
        well_index = df[df["Application: Tecan i-control"] == well].index
    except:
        well_index = df[df["Programm: Tecan i-control"] == well].index
    
    well_values = df.iloc[well_index, :]
    well_values_T = well_values.T #transposes the data from the selected row
    well_values_T.reset_index(drop = True, inplace = True)
    return  well_values_T

#Extracting the values for the wells specified by the user
for k, v in rep.items():
    for i in v:
        values = extract_values_with_monomeasurements(i, lux_data)
        values.iloc[0,0] =str(k + " : " + i)
        lux_df = pd.concat([lux_df, values], axis=1, ignore_index=True)        
    #Calculate mean value for the replicates 
    row_means = lux_df.iloc[1:, -len(v):].mean(axis = 1)
    #Calculate standard deviation for the replicates
    row_std = lux_df.iloc[1:, -len(v):].std(axis = 1)
    #Add mean value and std to the df
    lux_df = pd.concat([lux_df, row_means], axis=1, ignore_index=True)
    lux_df.iloc[0,-1] = str(k + " : " + "Mean value")
    lux_df = pd.concat([lux_df, row_std], axis = 1, ignore_index=True)
    lux_df.iloc[0,-1] = str(k + " : " + "St. dev")
    
#Pass the first row as colum names
lux_df.columns = lux_df.iloc[0]
lux_df = lux_df.drop(0)
lux_df.reset_index(drop = True, inplace = True)

#Normalize luminescence to optical density (RLU) and save results to a separate spreadsheet
rlu_df = lux_df.copy()
for column in rlu_df.columns:
    if "Mean value" not in column and "St. dev" not in column and "Time" not in column and "Zeit" not in column:
        rlu_df[column] = lux_df[column].div(growth_df[column])
    if "Mean value" in column:
        col_idx = rlu_df.columns.get_loc(column)
        rlu_df[column] = rlu_df.iloc[:, col_idx-3:col_idx-1].mean(axis = 1)
    if "St. dev"  in column:
        rlu_df[column] = rlu_df.iloc[:, col_idx-3:col_idx-1].std(axis = 1)
 
#saving results to excel
lux_df.to_excel(excel, sheet_name="Luminescence_LU", index=False)
rlu_df.to_excel(excel, sheet_name="Luminescence_RLU", index=False)
excel.close()

#Plotting luminescence arbitrary units on a single plot#
xlabel = 'Time [h]'
ylabel = 'Luminescence [AU]'
combined_lineplot_w_shadows(rep, lux_df, xlabel, ylabel)
plt.savefig(o + "_one_plot" + "_LU" + ".png", format = "png", dpi = 300)
plt.savefig(o + "_one_plot" + "_LU" + ".pdf", format = "pdf")
plt.savefig(o + "_one_plot" + "_LU" + ".svg", format = "svg")
plt.show()

#Plotting relative luminescence units on a single plot#
ylabel = 'Luminescence [RLU]'
combined_lineplot_w_shadows(rep, rlu_df, xlabel, ylabel)
plt.savefig(o + "_one_plot" + "_RLU" + ".png", format = "png", dpi = 300)
plt.savefig(o + "_one_plot" + "_RLU" + ".pdf", format = "pdf")
plt.savefig(o + "_one_plot" + "_RLU" + ".svg", format = "svg")
plt.show()

##Plotting luminescence arbitrary units on separate plots##
ncols, nrows, fig_size = optimum_grid(rep, plot_width, plot_height, space, left, right, bottom, top)
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=fig_size, sharey = False)
fig.subplots_adjust(hspace=0.5, wspace=0.5) # adjust the spacing between the subplots
xlabel = 'Time [h]'
ylabel = ' Luminescence [AU]'
separate_lineplots_with_shadows(rep, lux_df, ncols, xlabel, ylabel)
#Hide the blank subplots 


plt.savefig(o + "_sep_plots" + "_LU" + ".png", format = "png", dpi = 300)
plt.savefig(o + "_sep_plots" + "_LU" + ".pdf", format = "pdf")
plt.savefig(o + "_sep_plots" + "_LU" + ".svg", format = "svg")
plt.show()

##Plotting relative luminescence units on separate plots##

ncols, nrows, fig_size = optimum_grid(rep, plot_width, plot_height, space, left, right, bottom, top)
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=fig_size, sharey = False)
fig.subplots_adjust(hspace=0.5, wspace=0.5) # adjust the spacing between the subplots
xlabel = 'Time [h]'
ylabel = ' Luminescence [RLU]'
separate_lineplots_with_shadows(rep, rlu_df, ncols, xlabel, ylabel, False)
#Hide the blank subplots 
if ncols * nrows > len(rep.items()):
    n_to_hide = ncols * nrows - len(rep.items())
    while n_to_hide > 0:    
        axes[nrows - 1, n_to_hide].set_visible(False)
        n_to_hide = n_to_hide - 1
fig.tight_layout()

plt.savefig(o + "_sep_plots" + "_RLU" + ".png", format = "png", dpi = 300)
plt.savefig(o + "_sep_plots" + "_RLU" + ".pdf", format = "pdf")
plt.savefig(o + "_sep_plots" + "_RLU" + ".svg", format = "svg")
plt.show()

##Plotting luminescence and growth together on separate subplots for each sample
'''Here there will be a function that will iterate through the growth means and 
luminescence means, growth std. devs and luminescence st. devs. and plot them in pairs
on the separate subplots'''
def paired_plots(replicates, df1, df2, xlabel = 'Time [h]', ylabel1 = None, ylabel2 = None, same_yscales = True, keyword1 = "growth", keyword2 = "luminescence",  color1 = 'blue', color2 = 'orange'):
    
    x = df1['Time [h]'].astype(float) #x axis is the same for all plots
    
    plotted_means1 = []
    plotted_stds1 = [] 
    plotted_means2 = []
    plotted_stds2 = []
    
    for k, v in replicates.items():
            for column in df1.columns:
                if k + " : " + "Mean value" in column:
                    y_mean = df1[column].astype(float)         
                    plotted_means1.append(y_mean)                
                    for std_column in df1.columns:
                        if k in std_column and "St. dev" in std_column:
                            y_std = df1[std_column].astype(float)
                            plotted_stds1.append(y_std)
                            break
            for column in df2.columns:
                if k + " : " + "Mean value" in column:
                    y_mean = df2[column].astype(float)         
                    plotted_means2.append(y_mean)                
                    for std_column in df2.columns:
                        if k in std_column and "St. dev" in std_column:
                            y_std = df2[std_column].astype(float)
                            plotted_stds2.append(y_std)
                            break

    #Finding min and max of all data to set y axis to the same scale
    if same_yscales is True:
        #find y limits for the first axis
        concat_means = pd.concat(plotted_means1, axis = 0)
        concat_std = pd.concat(plotted_stds1, axis = 0)
        y_mean_min1 = concat_means.min()
        y_mean_max1 = concat_means.max()
        y_std_min1 = concat_std.min()
        y_std_max1 = concat_std.max()
        y_min1 = y_mean_min1-0.5*y_std_min1
        y_max1 = y_mean_max1 + 0.5*y_std_max1
        #find y limits for the second axis
        concat_means = pd.concat(plotted_means2, axis = 0)
        concat_std = pd.concat(plotted_stds2, axis = 0)
        y_mean_min2 = concat_means.min()
        y_mean_max2 = concat_means.max()
        y_std_min2 = concat_std.min()
        y_std_max2 = concat_std.max()
        y_min2 = y_mean_min2-0.5*y_std_min2
        y_max2 = y_mean_max2 + 0.5*y_std_max2
    else: 
        pass    
    # Plotting data on the first y axis

    for i, (mean, std) in enumerate(zip(plotted_means1, plotted_stds1)):
        c = i % ncols
        r = i // ncols
        error = 0.5 * std
        lower = mean - error
        upper = mean + error
        ax1 = axes[r, c]
        sns.lineplot(x=x, y=mean, ax=ax1, color = color1, label = keyword1)
        ax1.legend(loc = "upper right")
        ax1.set_title(mean.name.split(":")[0])
        ax1.fill_between(x, lower, upper, color = color1, alpha=0.2)
        if same_yscales is True:
            ax1.set_ylim(y_min1, y_max1)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel1)
    plotted_means1.clear()
    plotted_stds1.clear()
    
    # Plotting data on the second y axis

    for j, (mean2, std2) in enumerate(zip(plotted_means2, plotted_stds2)):
        c = j % ncols
        r = j // ncols
        error = 0.5 * std2
        lower2 = mean2 - error
        upper2 = mean2 + error
        ax2 = axes[r, c]
        ax2 = ax2.twinx()
        sns.lineplot(x=x, y=mean2, ax=ax2, color = color2, label = keyword2)
        ax2.legend(loc = "lower right")
        ax2.fill_between(x, lower2, upper2, color = color2, alpha=0.2)
        if same_yscales is True:
            ax2.set_ylim(y_min2, y_max2)
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel2)
    
    if ncols * nrows > len(replicates.items()):
        n_to_hide = ncols * nrows - len(rep.items())
        while n_to_hide > 0:    
            axes[nrows - 1, n_to_hide].set_visible(False)
            n_to_hide = n_to_hide - 1
            
    
sns.set_style("white")
ncols, nrows, fig_size = optimum_grid(rep, plot_width, plot_height, space, left, right, bottom, top)
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=fig_size, sharey = False)
fig.subplots_adjust(hspace=0.5, wspace=0.5) # adjust the spacing between the subplots
color1 = 'blue'
color2 = 'orange'

paired_plots(rep, growth_df, rlu_df, xlabel = 'Time [h]', ylabel1 = 'OD [AU]', ylabel2 = 'Luminescence [RLU]', same_yscales = False)    
fig.tight_layout()   
plt.savefig(o + "_paired_plots" + "_RLU" + ".png", format = "png", dpi = 300)
plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    