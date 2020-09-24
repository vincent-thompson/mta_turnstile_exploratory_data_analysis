def clean_data(df):

    import pandas as pd
    import datetime as dt
    import numpy as np
   
    # rename columns to get rid of the funny 'EXITS     ' issue
    df.columns = ['C/A','UNIT','SCP','STATION','LINENAME',\
                  'DIVISION','DATE','TIME','DESC','ENTRIES','EXITS']
    
    # remove index 180052 (project technology error)
    df.drop(df.index[180052])
    
    # convert to datetime/make turnstile column
    df['converted_time'] = pd.to_datetime(df['DATE']+' '+df['TIME'])
    df['turnstiles'] = df['C/A'] + '-' + df['UNIT'] + '-' + df['SCP'] + '-' + df['STATION']
    
    # sort by date and location
    df_sorted = df.sort_values(['turnstiles', 'converted_time'])
    
    # group by turnstile so we can get entry/exit differences
    turnstile_df = df_sorted.groupby('turnstiles')
    df_sorted['entries_diff'] = turnstile_df['ENTRIES'].diff()
    df_sorted['exits_diff'] = turnstile_df['EXITS'].diff()
    
    '''
    # calculates IQR for entries_diff
    Q3 = df_sorted['entries_diff'].quantile(0.75) 
    Q1 = df_sorted['entries_diff'].quantile(0.25)
    IQR = Q3 - Q1
    
    # calculates IQR range using outliers 
    IQR_range = (Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
    
    # removes values outside of lower and upper bounds
    df_sorted = df_sorted[df_sorted['entries_diff'].between(0, IQR_range[1])]
    
    # repeats process for exits_diff
    Q3_2 = df_sorted['exits_diff'].quantile(0.75) 
    Q1_2 = df_sorted['exits_diff'].quantile(0.25)
    IQR_2 = Q3_2 - Q1_2
    IQR_range_2 = (Q1_2 - 1.5 * IQR, Q3_2 + 1.5 * IQR)
    df_sorted = df_sorted[df_sorted['exits_diff'].between(0, IQR_range_2[1])]
    '''
    
    # removes negative values (ONLY NEEDED if no outliers removed)
    df_sorted = df_sorted[df_sorted['entries_diff'].between(0, np.inf)]
    df_sorted = df_sorted[df_sorted['exits_diff'].between(0, np.inf)]
    
    # round to nearest hour 
    df_sorted['time_round']=pd.to_datetime(df['TIME'], format='%H:%M:%S')
    df_sorted['time_round']=df_sorted['time_round'].dt.round('H').dt.hour
    
    # created new column turnstile_turns with total turnstile interactions per turnstile
    df_sorted['turnstile_turns'] = df_sorted.entries_diff + df_sorted.exits_diff
    df_sorted.turnstile_turns.describe()

    # replaces NaN values with mean for entries_diff and exits_diff
    df_sorted.entries_diff = df_sorted.entries_diff.fillna(df_sorted.entries_diff.mean())
    df_sorted.exits_diff = df_sorted.exits_diff.fillna(df_sorted.exits_diff.mean())

    # provides column day_of_week that designates the day of the week 
    df_sorted['day_of_week']=df_sorted.converted_time.dt.dayofweek
    
    #Create new column to differentiate stations serving different subway lines but with identical names
    df_sorted['station_unique'] = df_sorted['STATION'] + '-' + df_sorted['LINENAME']
    
    return df_sorted