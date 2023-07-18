# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:14:14 2023

@author: Marina Dziuba
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

## Data plotting functions

def combined_lineplot_w_stdev_as_shadows(replicates, tidy_df, xlabel, ylabel):
    '''Plot mean values of the measuremens as line plots with standard deviations
    as shaded regions on a 
    single plot by looping through columns of the tidy data frame (tidy_df).
    Accepts a dictionary with replicate wells and a tidy pandas df with 
    pre-calculated mean value and st.dev. '''
    fig, ax = plt.subplots(figsize = (10, 8))
    plotted_means = []
    plotted_stds = []
    x = tidy_df['Time [h]'].astype(float)

    for k, v in replicates.items():
        for column in tidy_df.columns:
            if k + " : " + "Mean value" in column:
                y_mean = tidy_df[column].astype(float)
                plotted_means.append(y_mean)
                
                for std_column in tidy_df.columns:
                    if k in std_column and "St. dev" in std_column:
                        y_std = tidy_df[std_column].astype(float)
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


def optimum_grid(replicates, plot_width, plot_height, space, left, right, bottom, top):
    '''Calculates optimum number of rows and columns depending on the number of 
    replicates and pre-set margin sizes. '''
    
    # calculate the optimum number of rows and columns so that no more than 3 plots in one row are plotted
    nrows = int(len(replicates.items()) / 3) + int(len(replicates.items()) % 3 > 0)
    ncols = 3 if len(replicates.items()) >= 3 else len(replicates.items())    
    # Calculation of optimum figure size
    fig_width = ncols * plot_width + (ncols - 1) * space + left + right
    fig_height = nrows * plot_height + (nrows - 1) * space + bottom + top
    fig_size = (fig_width, fig_height)    
    return ncols, nrows, fig_size 


def separate_lineplots_w_stdev_as_shadows(replicates, ncols, nrows, fig_size, df, xlabel, ylabel, same_yscale=True):
    '''Plot values in separate line plots with errors shown as shaded regions 
    by looping through columns and replicates passed by the user.
    Accepts a dictionary with replicate wells and a tidy pandas df with pre-calculated 
    meanvalue and st.dev. '''
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=fig_size, sharey = False)
    fig.subplots_adjust(hspace=0.5, wspace=0.5) # adjust the spacing between the subplots
    
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
    
    if ncols * nrows > len(replicates.items()):
        n_to_hide = ncols * nrows - len(replicates.items())
        while n_to_hide > 0:    
            axes[nrows - 1, n_to_hide].set_visible(False)
            n_to_hide = n_to_hide - 1
    fig.tight_layout()

def paired_plots(replicates, ncols, nrows, fig_size, df1, df2, xlabel = 'Time [h]', ylabel1 = None, 
                 ylabel2 = None, same_yscales = True, 
                 color1 = 'blue', color2 = 'orange'):
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=fig_size, sharey = False)
    fig.subplots_adjust(hspace=0.5, wspace=0.5) # adjust the spacing between the subplots
    
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
        sns.lineplot(x=x, y=mean, ax=ax1, color = color1, label = ylabel1)
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
    sns.set_style("white")
    for j, (mean2, std2) in enumerate(zip(plotted_means2, plotted_stds2)):
        c = j % ncols
        r = j // ncols
        error = 0.5 * std2
        lower2 = mean2 - error
        upper2 = mean2 + error
        ax2 = axes[r, c]
        ax2 = ax2.twinx()
        sns.lineplot(x=x, y=mean2, ax=ax2, color = color2, label = ylabel2)
        ax2.legend(loc = "lower right")
        ax2.fill_between(x, lower2, upper2, color = color2, alpha=0.2)
        if same_yscales is True:
            ax2.set_ylim(y_min2, y_max2)
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel2)
    
    if ncols * nrows > len(replicates.items()):
        n_to_hide = ncols * nrows - len(replicates.items())
        while n_to_hide > 0:    
            axes[nrows - 1, n_to_hide].set_visible(False)
            n_to_hide = n_to_hide - 1
