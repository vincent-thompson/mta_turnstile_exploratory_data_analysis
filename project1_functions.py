#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import datetime


# In[10]:


def get_data(week_nums):
    url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt"
    dfs = []
    for week_num in week_nums:
        file_url = url.format(week_num)
        dfs.append(pd.read_csv(file_url))
    return dfs

def clean_dfs(dfs):
    import clean_data as cld
    clean_dfs = []
    for df in dfs:
        clean_dfs.append(cld.clean_data(df))
    return clean_dfs

def concat_dfs(dfs):
    df_sorted = pd.concat(dfs)
    df_sorted['weekly_turns']= df_sorted['total_turns']/len(dfs)
    return df_sorted

def get_boroughs(df_sorted):
    '''
    Description: Function that adds a "borough" column \
                    to cleaned df from latitude/longitude column
    Args: df_sorted - sorted dataframe with 'location_string' column
    Returns: df_sorted - returns the input df with additional "borough" column
    '''
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="project1")
    df_sorted['location_string_copy'] = df_sorted['location_string'].copy()
    loc = df_sorted.location_string.dropna().unique()
    loc
    borough_set = set(['Manhattan', 'Brooklyn', 'Queens', 'The Bronx', 'Staten Island'])
    for i, l in enumerate(loc):
        print(i)
        sub = str(geolocator.reverse(l))
        sub_split = sub.split(', ')
        station_borough = list(borough_set.intersection(sub_split))
        if len(station_borough) > 1:
            station_borough = station_borough[0]
        if station_borough == []:
            station_borough = 'Unknown'
        df_sorted.location_string_copy.replace({l:station_borough}, inplace=True)
        print(station_borough)
    df_sorted = df_sorted.rename(columns={'location_string_copy':'borough'})
    return df_sorted
        


# In[20]:


def plot_total_traffic_by_station(df_sorted, metric='total_turns', borough=False):
    '''
    Function to plot the total turnstile turns for all stations, or a subset of stations belonging to 
        the same borough
    Args: df_sorted - cleaned df to be plotted
            metric - 'y value to be plotted (eg. total turns, weekly turns, entry/exit ratio)
            borough - indicate borough to be plotted (e.g. 'Manhattan') defaults to false, which is all stations
    
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    get_ipython().run_line_magic('matplotlib', 'inline')
    
    if borough:
        df_sorted = df_sorted[df_sorted['borough']==borough]
    
    #Group by Station-Line Name Combo... eg, 34th Penn Station is one huge station but the street team
    #cannot be at the A-C-E entrance and the 1-2-3 entrance simultaneously, so that traffic should be 
    #split accordingly
    df_sorted_station = df_sorted.groupby(['station_unique', 'turnstiles']).agg({'entries_diff': 'sum', 'exits_diff':'sum',                                  'total_turns':'sum', 'weekly_turns':'sum'})
    #Reset turnstiles index and aggregate again to count number of turnstiles per station
    #Add turns per turnstile column
    df_sorted_station = df_sorted_station.reset_index(level='turnstiles').groupby('station_unique').agg({'turnstiles':'count', 'entries_diff': 'sum', 'exits_diff':'sum',                                  'total_turns':'sum', 'weekly_turns':'sum'})
    df_sorted_station['weekly_turns_per_turnstile'] = df_sorted_station['weekly_turns']/df_sorted_station['turnstiles']
    df_sorted_station['total_turns_per_turnstile'] = df_sorted_station['total_turns']/df_sorted_station['turnstiles']
    df_sorted_station['entry_ratio'] = df_sorted_station['entries_diff']/df_sorted_station['total_turns']
    
    #Set y values to be total entries + exits,  x values to be # of turnstiles at each station
    #names will be the station name labels for each scatter plot point
    x = df_sorted_station.turnstiles
    y = df_sorted_station[metric]
    names = df_sorted_station.index

    #initiate scatter plot
    get_ipython().run_line_magic('matplotlib', 'notebook')
    fig,ax = plt.subplots(figsize=(10,8))
    sc = ax.scatter(x,y,s=100, alpha=0.3)

    
    
    #Borrowed code from https://stackoverflow.com/questions/7908636/possible-to \
    #-make-labels-appear-when-hovering-over-a-point-in-matplotlib
    annot = ax.annotate("", xy=(0,0), xytext=(-30,-30), size = 15, textcoords="offset points",                     bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "{}".format(" ".join([names[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)
    
    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
                
    fig.canvas.mpl_connect("motion_notify_event", hover)

    ax.set_xlabel('Number of turnstiles')
    ax.set_ylabel('Total Weekly Turnstile Turns')
    ax.grid(True)
    plt.show()
    
# plot_total_traffic_by_station(df_sorted, metric='weekly_turns', borough='Brooklyn')
    


# In[19]:


def plot_traffic_density(df_sorted, stations = 10, metric='weekly_turns_per_turnstile', borough=False):
    import numpy as np
    import matplotlib.pyplot as plt
    get_ipython().run_line_magic('matplotlib', 'inline')
    
    if borough:
        df_sorted = df_sorted[df_sorted['borough']==borough] 
    
    
    #Group by Station-Line Name Combo... eg, 34th Penn Station is one huge station but the street team
    #cannot be at the A-C-E entrance and the 1-2-3 entrance simultaneously, so that traffic should be 
    #split accordingly
    df_sorted_station = df_sorted.groupby(['station_unique', 'turnstiles']).agg({'entries_diff': 'sum', 'exits_diff':'sum',                                  'total_turns':'sum', 'weekly_turns':'sum'})
    #Reset turnstiles index and aggregate again to count number of turnstiles per station
    #Add turns per turnstile column
    df_sorted_station = df_sorted_station.reset_index(level='turnstiles').groupby('station_unique').agg({'turnstiles':'count', 'entries_diff': 'sum', 'exits_diff':'sum',                                  'total_turns':'sum', 'weekly_turns':'sum'})
    df_sorted_station['weekly_turns_per_turnstile'] = df_sorted_station['weekly_turns']/df_sorted_station['turnstiles']
    df_sorted_station['total_turns_per_turnstile'] = df_sorted_station['total_turns']/df_sorted_station['turnstiles']
    df_sorted_station['entry_ratio'] = df_sorted_station['entries_diff']/df_sorted_station['total_turns']
    
    #Set y values to be total entries + exits,  x values to be # of turnstiles at each station
    #names will be the station name labels for each scatter plot point
    x = df_sorted_station.turnstiles
    y = df_sorted_station[metric]
    
    


#Plot bar graph of the traffic density, or turns per turnstile, for busiest subway stations
    df_busiest = df_sorted_station.sort_values('total_turns', ascending=False).head(stations)
    fig,ax = plt.subplots(figsize=(15,stations/2))
    y_pos = np.arange(len(df_busiest.total_turns_per_turnstile))
    ax.barh(y_pos, df_busiest.total_turns_per_turnstile)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_busiest.index)
    ax.set_xlabel('Turns Per Turnstile')
    ax.invert_yaxis() #set labels so that busiest stations are at top

# plot_traffic_density(df_sorted, stations = 40, borough = 'Brooklyn')


# In[17]:


def plot_traffic_by_day_of_week(df_sorted, num_stations=10, custom_stations=None, borough=False, title = 'Title',                                 ylabel = 'Total Turnstile Turns'):
    import matplotlib.pyplot as plt
    get_ipython().run_line_magic('matplotlib', 'inline')
    
    if borough:
        df_sorted = df_sorted[df_sorted['borough']==borough]
        
    df_sorted_station = df_sorted.groupby(['station_unique', 'turnstiles', 'day_of_week'                                              ]).agg({'entries_diff': 'sum', 'exits_diff':'sum',                                                  'total_turns':'sum'})

    df_sorted_station = df_sorted_station.reset_index(level='turnstiles').groupby(['station_unique',                                                     'day_of_week']).agg({'entries_diff':                                                         'sum', 'exits_diff':'sum',                                                          'total_turns':'sum'})

    df_sorted_station = df_sorted_station.reset_index(level=['station_unique', 'day_of_week'])

    df_busiest = df_sorted_station.groupby('station_unique').sum().sort_values('total_turns',                                                                            ascending = False)
    
    
    busiest_stations = df_busiest.index
    
    plt.figure(figsize=(14,10))
    
    if custom_stations != None:
        for station in custom_stations:
            df_subset = df_sorted_station[df_sorted_station.station_unique == station]
            daily_mean = (df_subset.total_turns.sum())/df_subset.total_turns.count()
            df_subset['deviation_from_daily_mean'] = (df_subset['total_turns']-daily_mean)/daily_mean
            plt.plot('day_of_week', 'total_turns', data=df_subset, label=station)
    else:
        for station in busiest_stations[:num_stations]:
            df_subset = df_sorted_station.loc[df_sorted_station['station_unique']==station].copy()
            daily_mean = (df_subset.total_turns.sum())/df_subset.total_turns.count()
            df_subset['deviation_from_daily_mean'] = (df_subset['total_turns']-daily_mean)/daily_mean
            plt.plot('day_of_week', 'total_turns', data=df_subset, label=station)
    plt.legend(framealpha=0.25, fontsize='small', bbox_to_anchor=(1.05,1))
    plt.xlabel('Day of the Week')
    plt.ylabel('Total Turnstile Turns')
    plt.title(title, fontsize='x-large')
    plt.tight_layout()


# In[16]:


def histogram(df_sorted):
    import matplotlib.pyplot as plt
    get_ipython().run_line_magic('matplotlib', 'inline')
    df_sorted_station = df_sorted.groupby(['station_unique', 'turnstiles', 'day_of_week'                                              ]).agg({'entries_diff': 'sum', 'exits_diff':'sum',                                                  'total_turns':'sum'})

    df_sorted_station = df_sorted_station.reset_index(level='turnstiles').groupby('station_unique').agg({'entries_diff':                                                         'sum', 'exits_diff':'sum',                                                          'total_turns':'sum'})
    plt.figure(figsize=(14,10))
    plt.hist((df_sorted_station['total_turns']), bins = 50);
    


# In[21]:


def list_busiest(df_sorted, amount=30):
    
    df_sorted_station = df_sorted.groupby(['station_unique', 'turnstiles', 'day_of_week'                                              ]).agg({'entries_diff': 'sum', 'exits_diff':'sum',                                                  'total_turns':'sum'})

    df_sorted_station = df_sorted_station.reset_index(level='turnstiles').groupby('station_unique').agg({'entries_diff':                                                         'sum', 'exits_diff':'sum',                                                          'total_turns':'sum'})
    return df_sorted_station['total_turns'].sort_values(ascending=False).head(amount)


# In[ ]:


def plot_traffic_by_time(df_sorted, borough=False):
    import matplotlib.pyplot as plt
    get_ipython().run_line_magic('matplotlib', 'inline')
    
    if borough:
            df_sorted = df_sorted[df_sorted['borough']==borough]

    df_times = df_sorted.groupby(['station_unique', 'time_round']).sum()
    df_times.reset_index(level=['time_round', 'station_unique'], inplace=True)
    df_times.head(20)

    for num in range(len(df_times['time_round'])):
        if df_times.loc[num, 'time_round'] >4 and df_times.loc[num, 'time_round'] <=12:
            df_times.loc[num, 'time_round'] = 'Morning: 4am - 12pm'
        elif df_times.loc[num, 'time_round'] >12 and df_times.loc[num, 'time_round'] <=20:
            df_times.loc[num, 'time_round'] = 'Afternoon: 12pm - 8pm'
        else:
            df_times.loc[num, 'time_round'] = 'Night: 8pm - 4am'
        
    df_busiest = df_times.groupby('station_unique').sum().sort_values('total_turns',                                                                            ascending = False)
    
    
    busiest_stations = df_busiest.index

    # if custom_stations != None:#     for station in custom_stations:#         df_subset = df_sorted_station[df_sorted_station.station_unique == station]#         daily_mean = (df_subset.total_turns.sum())/df_subset.total_turns.count()#         df_subset['deviation_from_daily_mean'] = (df_subset['total_turns']-daily_mean)/daily_mean#         plt.plot('day_of_week', 'total_turns', data=df_subset, label=station)# else:plt.figure(figsize=[13,10])
    plt.figure(figsize=(13,10))
    plt.subplot(1, 2, 1)
    plt.suptitle('Relative Turnstile Traffic Of Busiest Stations By Time of Day', y=1.0)
    for station in busiest_stations[:10]:
        df_subset = df_times.loc[df_times['station_unique']==station].groupby('time_round').sum()
        weekly_turns = (df_subset.weekly_turns.sum())
        df_subset['ratio'] = df_subset['weekly_turns']/weekly_turns
        plt.scatter(df_subset.index, df_subset['ratio'],  label=station, s = 50, marker='D')
    plt.legend(framealpha=0.5, fontsize='small')
    plt.ylabel('Percentage of Total Turnstile Traffic')
    plt.title('Top 10 Busiest Stations')

    plt.subplot(1,2,2)
    for station in busiest_stations[10:20]:
        df_subset = df_times.loc[df_times['station_unique']==station].groupby('time_round').sum()
        weekly_turns = (df_subset.weekly_turns.sum())
        df_subset['ratio'] = df_subset['weekly_turns']/weekly_turns
        plt.scatter(df_subset.index, df_subset['ratio'],  label=station, s = 50, marker='D')
    plt.legend(framealpha=0.5, fontsize='small')
    plt.title('11th - 20th Busiest Stations')
    
# plot_traffic_by_time(df_sorted, borough='Brooklyn')


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[5]:





# In[12]:





# In[13]:





# In[ ]:





# In[ ]:




