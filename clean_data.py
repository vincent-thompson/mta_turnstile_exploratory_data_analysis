def clean_data(df):

    import pandas as pd
    import datetime as dt
    import numpy as np
   
    # standardizes column name and spacing for easy calling in code
    df.columns = ['C/A','UNIT','SCP','STATION','LINENAME',\
                  'DIVISION','DATE','TIME','DESC','ENTRIES','EXITS']
    
    ### TIMEDATE conversion / rounding
    
    # converts the time to datetime function to make it easier to work with this data, and consolidated turnstile information
    df['converted_time'] = pd.to_datetime(df['DATE']+' '+df['TIME'])
    df['turnstiles'] = df['C/A'] + '-' + df['UNIT'] + '-' + df['SCP'] + '-' + df['STATION']
    df_sorted = df.sort_values(['turnstiles', 'converted_time'])
    
    # rounds timeframe to nearest hour 
    df_sorted['time_round']=pd.to_datetime(df['TIME'], format='%H:%M:%S')
    df_sorted['time_round']=df_sorted['time_round'].dt.round('H').dt.hour
    
    ### time-specific ENTRIES / EXITS and total TURNSTILE_TURNS columns 
    
    # creats a new column to represent number of turns per time period, as opposed to cumulative over full collection period
    turnstile_df = df_sorted.groupby('turnstiles')
    df_sorted['entries_diff'] = turnstile_df['ENTRIES'].diff()
    df_sorted['exits_diff'] = turnstile_df['EXITS'].diff()
    
    # removes negative values (connected to audits and technological interferences)
    df_sorted = df_sorted[df_sorted['entries_diff'].between(0, np.inf)]
    df_sorted = df_sorted[df_sorted['exits_diff'].between(0, np.inf)]
    
    # replaces NaN values with mean for entries_diff and exits_diff
    df_sorted.entries_diff = df_sorted.entries_diff.fillna(df_sorted.entries_diff.mean())
    df_sorted.exits_diff = df_sorted.exits_diff.fillna(df_sorted.exits_diff.mean())
    
    # created new column turnstile_turns with total turnstile interactions per turnstile
    df_sorted['total_turns'] = df_sorted.entries_diff + df_sorted.exits_diff
    

    ### DAY_OF_WEEK column
    
    # provides column day_of_week that designates the day of the week 
    def get_weekday(x):
        weekday_key = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun' }
        return weekday_key[x]
    df_sorted['day_of_week'] = df_sorted.converted_time.dt.dayofweek.apply(get_weekday)
    
    #Create new column to differentiate stations serving different subway lines but with identical names
    df_sorted['station_unique'] = df_sorted['STATION'] + '-' + df_sorted['LINENAME']
    
<<<<<<< HEAD

=======
    
    ### Merges LATITUDE / LONGITUDE data
    
>>>>>>> 7a9779be430cde22571d36fd3d807ac4d91f40fb
    # merges with latitude and longitude data, providing three new columns - lat, lng and location_string (string w coordinates)
    github_df = pd.read_csv("https://raw.githubusercontent.com/dirtylittledirtbike/mta_data/master/location_by_remote_unit.csv")
    new_df = pd.merge(df_sorted, github_df, on='UNIT', how='left') 
    
    # based on missing coordinates for PATH stations, we added lat / lng pairs for each PATH station
<<<<<<< HEAD
    nan_stations = ('HARRISON', 'JOURNAL SQUARE', 'GROVE STREET', 'EXCHANGE PLACE', 'PAVONIA/NEWPORT', 'CHRISTOPHER ST',
                    '9TH STREET', '14TH STREET', 'TWENTY THIRD ST', 'THIRTY ST', 'LACKAWANNA', 'THIRTY THIRD ST', 
                    'PATH WTC 2', 'PATH NEW WTC','34 ST-HUDSON YD')
    nan_lat = [40.7384, 40.7326, 40.7197, 40.7162, 40.7267, 40.7331, 40.7342, 40.7374, 40.7429, 40.7491, 40.7350, 40.7491,
               40.7126, 40.7126, 40.7550]
    nan_lng = [-74.1557, -74.0627, -74.0431, -74.0329, -74.0348, -74.0071, -73.9988, -73.9969, -73.9929, -73.9882, 
               -74.0275, -73.9882, -74.0099, -74.0099, -74.0010]
=======
    nan_stations = ('HARRISON','JOURNAL SQUARE','GROVE STREET','EXCHANGE PLACE','PAVONIA/NEWPORT','CHRISTOPHER ST',
                    '9TH STREET','14TH STREET','TWENTY THIRD ST','THIRTY ST','LACKAWANNA','THIRTY THIRD ST', 
                    'PATH WTC 2','PATH NEW WTC','34 ST-HUDSON YD')
    nan_lat = [40.7384,40.7236,40.7197,40.7162,40.7267,40.7331,40.7342,40.7374,40.7429,40.7491,40.7350,40.7491,
               40.7126,40.7126,40.7550]
    nan_lng = [-74.1557,-72.0627,-74.0431,-74.0329,-74.0348,-74.0071,-73.9988,-73.9969,-73.9929,-73.9882, 
               -74.0275,-73.9882,-74.0099,-74.0099,-74.0010]
>>>>>>> 7a9779be430cde22571d36fd3d807ac4d91f40fb
    coordinate_list=[]

    for i in range(0, len(nan_lat)):
        coordinates = str(nan_lat[i]) + ',' + str(nan_lng[i])
        coordinate_list.append(coordinates)
        
    for i in range (0, len(nan_stations)):
       new_df.loc[new_df['STATION']==nan_stations[i], 
                  ['lat', 'lng', 'location_string']] = nan_lat[i], nan_lng[i], coordinate_list[i]
    
    # based on inconclusive Newark turnstile specifics, we generalized all Newark stops to one generalized coordinate
    newark_stations = ('NEWARK HW BMEBE', 'NEWARK BM BW', 'NEWARK C', 'NEWARK HM HE')

    for i in range (0, 4):
       new_df.loc[new_df['STATION']==newark_stations[i], 
                  ['lat', 'lng', 'location_string']] = 40.6895, -74.1745, '40.6895, -74.1745'
    
    return new_df
<<<<<<< HEAD

=======
>>>>>>> 7a9779be430cde22571d36fd3d807ac4d91f40fb
