import pandas as pd
import numpy as np
import xmltodict

#https://betterprogramming.pub/analyze-your-icloud-health-data-with-pandas-dd5e963e902f

input_path = './apple_health_export/export.xml'
with open(input_path, 'r') as xml_file:
    input_data = xmltodict.parse(xml_file.read())


records_list = input_data['HealthData']['Record']


raw_df = pd.DataFrame(records_list)

step_dist_df = raw_df[raw_df['@type'].isin(['HKQuantityTypeIdentifierStepCount', 'HKQuantityTypeIdentifierDistanceWalkingRunning'])].copy()

step_dist_df['value'] = step_dist_df['@value'].astype(float)
step_dist_df['localdate'] = pd.to_datetime(step_dist_df['@startDate'].str[:10])

#adding anomoly correction

step_dist_df['value'] = np.where((step_dist_df['@type'] == 'HKQuantityTypeIdentifierDistanceWalkingRunning') & (step_dist_df['value'] > 2.0), 2.0, step_dist_df['value'])
step_dist_df['value'] = np.where((step_dist_df['@type'] == 'HKQuantityTypeIdentifierStepCount') & (step_dist_df['value'] > 5000.0), 5000.0, step_dist_df['value'])


step_df = step_dist_df[step_dist_df['@type'] == 'HKQuantityTypeIdentifierStepCount'].groupby('localdate', as_index=False)['value'].sum().rename(columns={'localdate':'Date', 'value': 'Steps'})

#Fill in missing dates
step_df.set_index("Date", inplace=True)
step_df = step_df.asfreq("D", fill_value=0).reset_index()


milage_df = step_dist_df[step_dist_df['@type'] == 'HKQuantityTypeIdentifierDistanceWalkingRunning'].groupby('localdate', as_index=False)['value'].sum().rename(columns={'localdate':'Date', 'value': 'Miles'})

#Fill in missing days
milage_df.set_index("Date", inplace=True)
milage_df = milage_df.asfreq("D", fill_value=0).reset_index()


#Can change this to be made from a dataframe later
# event_df = pd.DataFrame([
# 	{'Date': pd.to_datetime('2019-07-20'), 'Event': 'Augustin in NYC. 100 degree weather'},
# 	{'Date': pd.to_datetime('2019-07-21'),'Event': 'Augustin in NYC. 100 degree weather'},
# 	{'Date': pd.to_datetime('2017-07-01'),'Event': 'London with Titouan'},
# 	{'Date': pd.to_datetime('2017-07-02'),'Event': 'London with Titouan'},
# 	{'Date': pd.to_datetime('2017-07-03'),'Event': 'Wimbledon'}

# ])
# event_df = pd.read_csv('events.csv')
# event_df['Date'] = pd.to_datetime(event_df.Date)

# step_df = step_df.merge(event_df, how='left', on='Date')
# milage_df = milage_df.merge(event_df, how='left', on='Date')



step_df.to_csv('steps.csv', index=False)
milage_df.to_csv('milage.csv', index=False)