# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 18:36:04 2021

@author: chudc
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


# user defined class to calculate DailyReturns, MonthlyReturns, QuarterlyReturns
class Returns:
    def __init__(self, df_name, ticker_name):
        self.df_name = df_name
        self.ticker_name = ticker_name
        # create a 'base' dataframe that only contains the ticker information
        self.df_base = pd.DataFrame(self.df_name.loc[self.df_name.ticker == self.ticker_name])
        # sort values by date to correctly calculate returns
        self.df_base.sort_values(by='date', inplace = True)
        
    # user defined function to calculate daily returns
    def DailyReturns(self):
        # copy previously created dataframe
        df_daily = self.df_base.copy()
        # add a new column to the dataframe with the DailyReturns for the ticker indicated
        df_daily['DailyReturns_{0}'.format(self.ticker_name)] = df_daily['closingprice'].pct_change()
        # drop unnecessary columns
        df_daily = df_daily.drop(columns = ['closingprice', 'securityId', 'ticker'])
        # set date as index
        df_daily.set_index('date', inplace = True)
        return df_daily
    
    # user defined function to calculate monthly returns
    def MonthlyReturns(self):
        # create a new dataframe using the 'base' that only keeps the first date of the month 
        df_monthly = pd.DataFrame(self.df_base.groupby(self.df_base.date.dt.to_period('m')).first())
        # add a new column to the dataframe with the MonthlyReturns for the ticker indicated
        df_monthly['MonthlyReturns_{0}'.format(self.ticker_name)] = df_monthly['closingprice'].pct_change()
        # drop unnecessary columns
        df_monthly = df_monthly.drop(columns = ['date','closingprice', 'securityId', 'ticker'])
        return df_monthly
    
    # user defined function to calculate quarterly returns
    def QuarterlyReturns(self):
        # create a new dataframe using the 'base' that only keeps the first date of the quarter
        df_quarterly = pd.DataFrame(self.df_base.groupby(self.df_base.date.dt.to_period('Q')).first())
        # add a new column to the dataframe with the QuarterlyReturns for the ticker indicated
        df_quarterly['QuarterlyReturns_{0}'.format(self.ticker_name)] = df_quarterly['closingprice'].pct_change()
        # drop all unnecessary columns
        df_quarterly = df_quarterly.drop(columns = ['date','closingprice', 'securityId', 'ticker'])
        return df_quarterly        

# user defined function that creates class objects and calculates returns for each ticker indicated in previous list.
# Then merges returns into a dataframe where each row is a date and each column is the return of a security
def Merge_df(dataframe, tickers):
    # empty list to save the class objects
    object_list = []
    # loop through the ticker list and append the class objects to empty list
    for i in tickers: 
        j = Returns(dataframe, i)
        object_list.append(j)
    
    # start three dataframes by calling the class functions for the first element of object_list
    daily_merged = object_list[0].DailyReturns()
    monthly_merged = object_list[0].MonthlyReturns()
    quarterly_merged = object_list[0].QuarterlyReturns()
    # loop through the rest of the elements of object_list and perform an outer join by 'date'
    for i in range(1, len(object_list)):
        daily_merged = pd.merge(daily_merged, object_list[i].DailyReturns(), on = 'date', how = 'outer')
        monthly_merged = pd.merge(monthly_merged, object_list[i].MonthlyReturns(), on = 'date', how = 'outer')
        quarterly_merged = pd.merge(quarterly_merged, object_list[i].QuarterlyReturns(), on = 'date', how = 'outer')
    
    # change the index from PeriodIndex to DateTimeIndex to avoid issues while plotting
    monthly_merged.index = monthly_merged.index.to_timestamp()
    quarterly_merged.index = quarterly_merged.index.to_timestamp()
    
    return daily_merged, monthly_merged, quarterly_merged

# user defined class to creat time series plots
class TimeSeriesPlots:
    def __init__(self, df_name, ticker_list=None, benckmark=None, time_period=None, title=None):
        self.df_name = df_name
        self.ticker_list = ticker_list
        self.benckmark = benckmark
        self.time_period = time_period
        self.title = title
        
    # user defined function to plot the returns
    def ReturnPlots(self):
         # define number of subplots - four rows and three columns
         figure, axis = plt.subplots(4, 3,sharey='all',figsize=(25,25))
         # initialize row and column counter
         row = 0
         col = 0
         # loop through each ticker in the ticker_list
         for tick in self.ticker_list:
             # define the axis of the plot - X will be the date - Y will be the returns
             axis[row, col].plot(self.df_name.index, self.df_name['{}Returns_{}'.format(self.time_period,tick)])
             axis[row, col].plot(self.df_name.index, self.df_name['{}Returns_{}'.format(self.time_period,self.benckmark)])
             # change the title
             axis[row, col].set_title('{} & {} - {} Returns'.format(tick, self.benckmark, self.time_period))
             # change the Y-axis label
             axis[row, col].set_ylabel('returns')
             
             # update the counter
             if col < 2:
                 col = col + 1
             else:
                 col = 0
                 row = row + 1
                 
         # remove last plot since it is empty
         axis.flat[-1].set_visible(False)
         
         return plt.show()
    
    # user defined function to plot the rolling volatility of the daily returns
    def RollingVolatilityPlots(self):
        # define number of subplots - four rows and three columns
        figure, axis = plt.subplots(4, 3, sharey='all',figsize=(25,25))
        # initialize row and column counter
        row = 0
        col = 0
        # loop through each ticker in the ticker_list
        for tick in self.ticker_list:
            # define the axis of the plot - X will be the date - Y will be the returns
            axis[row, col].plot(self.df_name.index, self.df_name['Volatility_{}'.format(tick)])
            axis[row, col].plot(self.df_name.index, self.df_name['Volatility_{}'.format(self.benckmark)])
            # change the title
            axis[row, col].set_title('{} & {} Rolling Volatility'.format(tick, self.benckmark))
            # change the Y-axis label
            axis[row, col].set_ylabel('rolling volatility')
        
            # update the counter
            if col < 2:
                col = col + 1
            else:
                col = 0
                row = row + 1
        
        # remove last plot since it is empty
        axis.flat[-1].set_visible(False)
        
        return plt.show()
    
    # user defined function to plot the normalized adjusted close
    def NormalizedAdjClosePlots(self):
        # define number of subplots - four rows and three columns
        figure, axis = plt.subplots(4, 3,sharey='all',figsize=(25,25))
        # initialize row and column counter
        row = 0
        col = 0
        # loop through each ticker in the ticker_list
        for tick in self.ticker_list:
            # define the axis of the plot - X will be the date - Y will be the normalized adjusted close
            axis[row, col].plot(self.df_name.index, self.df_name['{}'.format(tick)])
            axis[row, col].plot(self.df_name.index, self.df_name['{}'.format(self.benckmark)])
            # change the title
            axis[row, col].set_title('{} & {} - Normalized Adjusted Close'.format(tick, self.benckmark))
            # change the Y-axis label
            axis[row, col].set_ylabel('Normalized Adjusted Close')
            axis[row, col].tick_params(labelrotation=35)
            
            # update the counter
            if col < 2:
                col = col + 1
            else:
                col = 0
                row = row + 1
        
        # remove last plot since it is empty
        axis.flat[-1].set_visible(False)
 
        return plt.show()
    
    # user defined function to plot all the normalized adjusted close prices in one figure
    def NormalizedAdjRecessionPlots(self):
        fig, ax = plt.subplots(figsize = (12, 6))
        self.df_name.plot(ax = ax)
        ax.legend(loc='lower left', ncol=2)
        plt.title(self.title)
        plt.ylabel('adjusted close price')
        plt.gca().spines['top'].set_color(None)
        plt.gca().spines['right'].set_color(None)
        
        return plt.show()
     

# user defined function to calculate the rolling volatility
def Rolling_Volatility(dataframe, ticker_list):
    # create new dataframe for volatility
    monthly_vol = pd.DataFrame()
    quarterly_vol = pd.DataFrame()
    trading_days = 252
    for ticker in ticker_list:
        # add a new column to the dataframe with the DailyReturns for the ticker indicated
        monthly_vol['Volatility_{0}'.format(ticker)] = dataframe['DailyReturns_{0}'.format(ticker)].rolling(window=30,
                                                                                    min_periods=1).std()*np.sqrt(trading_days)
        quarterly_vol['Volatility_{0}'.format(ticker)] = dataframe['DailyReturns_{0}'.format(ticker)].rolling(window=90,
                                                                                    min_periods=1).std()*np.sqrt(trading_days)
    return monthly_vol, quarterly_vol    

# user defined function to normalize adjusted close
def AdjCloseNormalized(df_name, start_date, end_date, ticker_list):
    df_window_normalized = pd.DataFrame()
    df_window = pd.DataFrame()
    for ticker in ticker_list:
        df_window[ticker] = df_name[ticker].loc[start_date:end_date]
        df_window_normalized[ticker] = df_window[ticker] / df_window[ticker].iloc[0]*100
        
    return df_window_normalized
    
# user defined class to plot heatmaps
class HeatMapPlots:
    def __init__(self, df_name, start_date_1=None, end_date_1=None, start_date_2 =None,
                 end_date_2=None, title1=None, title2=None):
        self.df_name = df_name
        self.start_date_1 = start_date_1
        self.end_date_1 = end_date_1
        self.start_date_2 = start_date_2
        self.end_date_2 = end_date_2
        self.title1 = title1  
        self.title2 = title2
        # define color palette for heatmaps
        self.color = sns.diverging_palette(10, 150, as_cmap = True)
        # Create copy of dataframe to avoid future issues while plotting
        self.df = self.df_name.copy()
        # changing index to only show the 'date' part in the heatmap
        self.df.index = self.df.index.date
    
    # user defined function to plot the returns in a heatmap
    def HeatMapReturns(self):
        # transpose dataframe so that date is in the x axis and the different returns in Y axis
        df_transposed = self.df.T
        #plot
        fig, ax = plt.subplots(figsize=(15,12))    
        sns.heatmap(df_transposed,cmap = self.color, annot=False, ax=ax)
        ax.set_title(self.title1)
        
        return plt.show()
    
    # user defined function so that user can create customizable heatmaps 
    def HeatMapCustomizable(self):
        '''
        Parameters
        ----------
        df_name: dataframe of interest 
        start_date_1: in the form YYYY-MM-DD to start filtering information for example'2007-07-01'
        end_date_1: to end filtering information
        start_date_2: second start date to filter information of another period
        end_date_2: to end filtering information
        title1: for the heatmap of the first period filtered, for example,
                    'Heatmap of the Great Recession - Monthly Returns'
        title2: for the heatmap of the second period filtered

        Returns plot

        '''
        # change format of start and end dates to be able to filter the dataframe
        self.start_date_1 = pd.to_datetime(self.start_date_1).date()
        self.end_date_1 = pd.to_datetime(self.end_date_1).date()
        self.start_date_2 = pd.to_datetime(self.start_date_2).date()
        self.end_date_2 = pd.to_datetime(self.end_date_2).date()
        df1 = self.df.loc[self.start_date_1:self.end_date_1].T
        df2 = self.df.loc[self.start_date_2:self.end_date_2].T
        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize = (15,8))
        sns.heatmap(df1, cmap = self.color, annot = False, ax=ax1, cbar = False,linewidths=.5)
        ax1.set_title(self.title1)
        sns.heatmap(df2, cmap=self.color, annot=False, ax=ax2, yticklabels = False,linewidths=.5)
        ax2.set_title(self.title2)
        
        return plt.show()  

# user defined function to calculate statistics for a defined time period
def CustomizableStatistics(start_date, end_date, df_name, timeperiod, ticker_list):
    output = pd.DataFrame()
    for ticker in ticker_list:
        output['{}'.format(ticker)] = df_name.loc[start_date:end_date]['{}Returns_{}'.format(timeperiod, ticker)].describe()
    return output

# user defined function to create horizontal bar charts of the statistics of interest
def PlotStatistics(df_name_08, df_name_20, stat1, stat2, title1, title2, title3, title4):
    '''
    Parameters
    ----------
    df_name_08 : dataframe with stats of the Great Recession
    df_name_20 : dataframe with stats of the Covid Recession
    stat1 : first statistic of interest (for example mean)
    stat2 : second statistic of interest (for example std)
    title1 : for the horizontal bar chart of df_name_08 & stat1, for example
                'Mean of Monthly Returns - The Great Recession'
    title2 : for the horizontal bar chart of df_name_08 & stat2
    title3 : for the horizontal bar chart of df_name_20 & stat1
    title4 : for the horizontal bar chart of df_name_20 & stat2\
        
    Returns plot
    
    '''
    # obtain statistics of interest for the Great Recession
    # and format it to plot it as a horizontal bar chart
    df_stat1_08 = df_name_08[df_name_08.index == stat1]
    df_stat1_08 = (df_stat1_08.sort_values(by = stat1 , axis = 1, ascending = False)).T
    df_stat2_08 = df_name_08[df_name_08.index == stat2]
    df_stat2_08 = (df_stat2_08.sort_values(by = stat2 , axis = 1, ascending = False)).T
    
    # obtain statistics of interest for the Covid Recession
    # and format it to plot it as a horizontal bar chart
    df_stat1_20 = df_name_20[df_name_20.index == stat1]
    df_stat1_20 = (df_stat1_20.sort_values(by = stat1 , axis = 1, ascending = False)).T
    df_stat2_20 = df_name_20[df_name_20.index == stat2]
    df_stat2_20 = (df_stat2_20.sort_values(by = stat2 , axis = 1, ascending = False)).T
    
    # set up axes for the horizontal bar charts
    fig, ((ax1, ax2), (ax3,ax4)) = plt.subplots(2, 2, figsize = (15, 15))
    
    ax1.barh(df_stat1_08.index, df_stat1_08[stat1].values)
    ax1.set_xlabel(title1)
    ax1.set_ylabel('Sectors')

    #ax2
    ax2.barh(df_stat2_08.index, df_stat2_08[stat2].values)
    ax2.set_xlabel(title2)
    ax2.set_ylabel('Sectors')
    
    #ax3
    ax3.barh(df_stat1_20.index, df_stat1_20[stat1].values)
    ax3.set_xlabel(title3)
    ax3.set_ylabel('Sectors')
    
    #ax4
    ax4.barh(df_stat2_20.index, df_stat2_20[stat2].values)
    ax4.set_xlabel(title4)
    ax4.set_ylabel('Sectors')

    return plt.show()

# user defined funciton to create side by side plots of correlation matrices
def CorrelationMatrix(df_name_08, df_name_20, title1, title2):
    '''
    Parameters
    ----------
    df_name_08 : correlation matrix for Great Recession
    df_name_20 : correlation matrix for Covid Recession
    title1 : for the Great Recession plot, for example, 
                'Correlation of the Monthly Returns - The Great Recession'
    title2 : for the Covid Recession plot

    Returns plot
    
    '''
    # set up axis
    fig, (ax1, ax2) = plt.subplots(ncols=2,figsize = (20, 10))
    # heatmap for the frist dataframe
    sns.heatmap(df_name_08, cmap="YlGnBu",square = True, linewidths=.5, annot=False, ax=ax1)
    ax1.set_title(title1)
    # heatmap for the second dataframe
    sns.heatmap(df_name_20, cmap="YlGnBu", square = True, linewidths=.5, annot=False, ax=ax2, yticklabels= False)
    ax2.set_title(title2)
    
    return plt.show()

# user defined function to calulate nominal returns
def calcNominalReturns(dataframe, start_date, end_date):
    '''    
    Parameters
    ----------
    dataframe: dataframe with adjusted closing prices over a period of time
    start_date: in the form YYYY-MM-DD to start filtering information for example'2007-07-01'
    end_date: to end filtering information
    
    Returns numpy array of Nominal Returns 
    
    '''
    return dataframe[dataframe.index == end_date].values / dataframe[dataframe.index == start_date].values - 1

# user defined function to create a heatmap of the nominal returns
def HeatMapNominalReturns(dataframe):
    '''
    Parameters
    ----------
    dataframe: dataframe with nominal returns with which to create a heatmap
    
    Returnsplot
    
    '''
    plt.figure(figsize = (8, 6))
    redgreen = sns.diverging_palette(h_neg=13, h_pos=133, s=80, l=55, sep=3, as_cmap=True)
    return sns.heatmap(dataframe, cmap=redgreen, annot = True, fmt = '.2f', center = 0, vmin = -60);










