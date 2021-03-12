#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import folium
import folium.plugins as plugins
from folium.plugins import HeatMap
from folium.plugins import HeatMapWithTime

import pandas as pd
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)

import math


# In[ ]:


# TO DO: 
# add legend 
# extend fuel stations 
# figure out how to actually use FAF correctly 


# In[ ]:


# Load Data 

conway = pd.read_excel('conwayanalytics_2017_2020.xlsx', sheet_name = 'Conway Analytics')
werner = pd.read_csv('werner_trip_count_enhanced_fws_conway.csv')
werner_pings = pd.read_csv('werner_pings_2020.csv')


origins = pd.read_excel('20192020ODStopVolumes.xlsx', sheet_name = 'Origin')
destinations = pd.read_excel('20192020ODStopVolumes.xlsx', sheet_name = 'Destination')

cresa = pd.read_excel('VisitsNearCresaSites_withMSA.xlsx', sheet_name = 'CresaDataAllStopsSummary', skiprows = 1)
drivers = pd.read_csv('driver_domiciles.csv')

msa_metrics = pd.read_csv('msa_metrics.csv')

werner_hubs = pd.read_csv('werner_dropyards.csv')

terminals = werner_hubs[werner_hubs.Name.str.startswith('Terminal')]
dropyards = werner_hubs[~werner_hubs.Name.str.startswith('Terminal')]

fuel_stations = pd.read_csv('alt_fuel_stations (Feb 8 2021).csv')


# In[ ]:


fuel_stations['Fuel Type Code'].value_counts()


# In[ ]:


# Data Transformations 

# conway 
conway = conway[(conway['Target Latitude'] != 0) & (conway['Target Longitude'] != 0)]
# conway['Target Latitude'] = conway['Target Latitude'].round(1)
# conway['Target Longitude'] = conway['Target Longitude'].round(1)
conway['Publish Date'] = pd.to_datetime(conway['Publish Date'])

# werner
werner = werner[(werner['latitude'] != 0) & (werner['longitude'] != 0)]
werner['latitude'] = werner['latitude'].round(1)
werner['longitude'] = werner['longitude'].round(1)
# werner['latitude'] = werner['latitude'].round(2)
# werner['longitude'] = werner['longitude'].round(2)

# origin
origins = origins[(origins['LATITUDE_NB'] != 0) & (origins['LONGITUDE_NB'] != 0)]
# origins['LATITUDE_NB'] = origins['LATITUDE_NB'].round(1)
# origins['LONGITUDE_NB'] = origins['LONGITUDE_NB'].round(1)

origins['TRIP_PARENT_BOOKING_DIVISION_CD'] = origins['TRIP_PARENT_BOOKING_DIVISION_CD'].str.strip()
origins_van = origins[origins.TRIP_PARENT_BOOKING_DIVISION_CD == 'V']
origins_ded = origins[origins.TRIP_PARENT_BOOKING_DIVISION_CD == 'D']


# destination
destinations = destinations[(destinations['LATITUDE_NB'] != 0) & (destinations['LONGITUDE_NB'] != 0)]
# destinations['LATITUDE_NB'] = destinations['LATITUDE_NB'].round(1)
# destinations['LONGITUDE_NB'] = destinations['LONGITUDE_NB'].round(1)

destinations['TRIP_PARENT_BOOKING_DIVISION_CD'] = destinations['TRIP_PARENT_BOOKING_DIVISION_CD'].str.strip()
destinations_van = destinations[destinations.TRIP_PARENT_BOOKING_DIVISION_CD == 'V']
destinations_ded = destinations[destinations.TRIP_PARENT_BOOKING_DIVISION_CD == 'D']

# cresa
cresa = cresa[(cresa['Latitude'] != 0) & (cresa['Longitude'] != 0)]
cresa['icon_num'] = cresa['XLRow'] - 1
cresa['area'] = cresa['Land Area (AC)']

# drivers
drivers = drivers[(drivers['LATITUDE'] != 0) & (drivers['LONGITUDE'] != 0)]
drivers['LATITUDE'] = drivers['LATITUDE'].round(2)
drivers['LONGITUDE'] = drivers['LONGITUDE'].round(2)

# msa
msa_metrics['icon_num'] = msa_metrics.index + 1


# In[ ]:


conway_map = conway.copy()
werner_map = werner.copy()

origin_map = origins.copy()
destination_map = destinations.copy()

origin_van_map = origins_van.copy()
destination_van_map = destinations_van.copy()

origin_ded_map = origins_ded.copy()
destination_ded_map = destinations_ded.copy()

cresa_map = cresa.copy()
driver_map = drivers.copy()

def generateBaseMap(default_location=[41.87,-87.6273494], default_zoom_start=5):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start, min_zoom= 0, max_zoom = 6)
    return base_map


# In[ ]:


base_map = generateBaseMap()


# In[ ]:


url = (
    "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data"
)
state_geo = f"{url}/us-states.json"
origin_state_data = pd.read_csv('faf_origin_value_2025_average_state.csv')
destination_state_data = pd.read_csv('faf_destination_value_2025_average_state.csv')

folium.Choropleth(
    geo_data=state_geo,
    name="2025 Origin State Average Value",
    data=origin_state_data,
    columns=["State", "VALUE_2025"],
    key_on="feature.id",
    # fill_color="YlGn",
    fill_color="YlOrRd",
    fill_opacity=0.4,
    line_opacity=0.2,
    legend_name="2025 Origin State Average Value",
    show = False
).add_to(base_map)

folium.Choropleth(
    geo_data=state_geo,
    name="2025 Destination State Average Value",
    data=destination_state_data,
    columns=["State", "VALUE_2025"],
    key_on="feature.id",
    fill_color="RdPu",
    fill_opacity=0.4,
    line_opacity=0.2,
    legend_name="2025 Destination State Average Value",
    show = False
).add_to(base_map)


# In[ ]:


andrew_feature_group = folium.FeatureGroup(name = 'Data Science Team Recommendations')
consultant_feature_group = folium.FeatureGroup(name = 'Cresa Consultant Recommendations')


# In[ ]:


# icons using plugins.BeautifyIcon
for i in cresa.itertuples():
    folium.CircleMarker(location=[i.Latitude, i.Longitude],
                  popup=i.City + "\n" + str(i.area) + " acres", 
                  color = 'black',
                  radius = i.area**(1.0/3.0),
                  fill = True, 
                  fill_color = 'gray').add_to(consultant_feature_group.add_to(base_map))


# In[ ]:


# icons using plugins.BeautifyIcon
for i in msa_metrics.head(30).itertuples():
    folium.Marker(location=[i.lat, i.lon],
                  popup=i.msa,
                  icon=plugins.BeautifyIcon(number=i.icon_num,
                                            border_color='blue',
                                            border_width=1,
                                            text_color='green',
                                            inner_icon_style='margin-top:0px;')).add_to(andrew_feature_group.add_to(base_map))


# In[ ]:


# icons using plugins.BeautifyIcon
# https://fontawesome.com/v4.7.0/icons/

dropyard_feature_group = folium.FeatureGroup(name = 'Werner Dropyards')
terminal_feature_group = folium.FeatureGroup(name = 'Werner Terminals')

for i in dropyards.itertuples():
    folium.Marker(location=[i.Latitude, i.Longitude],
                  popup=i.Name + "\n" + str(i.TrailerSpaces) + " trailer spaces",
                  icon= folium.Icon(icon = 'truck', prefix = 'fa', icon_color = 'lightblue')).add_to(dropyard_feature_group.add_to(base_map))

for i in terminals.itertuples():
    folium.Marker(location=[i.Latitude, i.Longitude],
                  popup=i.Name + "\n" + str(i.TrailerSpaces) + " trailer spaces",
                  icon= folium.Icon(icon = 'star', prefix = 'fa', icon_color = 'white', color = 'darkblue')).add_to(terminal_feature_group.add_to(base_map))

biodiesel_feature_group = folium.FeatureGroup(name = 'Biodiesel Fuel Stations', show = False)


# In[ ]:


fuel_stations['Latitude'] = fuel_stations['Latitude'].round(1)
fuel_stations['Longitude'] = fuel_stations['Longitude'].round(1)
fuel_stations['station_name'] = fuel_stations['Station Name'] 


# In[ ]:


fuel_stations['station_name'] = fuel_stations['Station Name'] 

# electric_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='ELEC']
electric_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='ELEC'].groupby(['Latitude', 'Longitude']).count().reset_index()
ethanol_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='E85'].groupby(['Latitude', 'Longitude']).count().reset_index()
propane_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='LPG'].groupby(['Latitude', 'Longitude']).count().reset_index()
compressed_natural_gas_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='CNG'].groupby(['Latitude', 'Longitude']).count().reset_index()
biodiesel_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='BD'].groupby(['Latitude', 'Longitude']).count().reset_index()
liquefied_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='LNG'].groupby(['Latitude', 'Longitude']).count().reset_index()
hydrogen_fuel_stations = fuel_stations[fuel_stations['Fuel Type Code']=='HY'].groupby(['Latitude', 'Longitude']).count().reset_index()


# In[ ]:


hydrogen_fuel_stations


# In[ ]:


"""[‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’, ‘darkpurple’, ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’, ‘gray’, ‘black’, ‘lightgray’]

"""

electric_feature_group = folium.FeatureGroup(name = 'Electric Fuel Stations', show = False)
for i in electric_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'pink').add_to(electric_feature_group.add_to(base_map))
    
ethanol_feature_group = folium.FeatureGroup(name = 'Ethanol Fuel Stations', show = False)
for i in ethanol_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'darkpurple').add_to(ethanol_feature_group.add_to(base_map))

propane_feature_group = folium.FeatureGroup(name = 'Propane Fuel Stations', show = False)
for i in propane_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'lightblue').add_to(propane_feature_group.add_to(base_map))
    
compressed_natural_gas_feature_group = folium.FeatureGroup(name = 'Compressed Natural Gas Fuel Stations', show = False)
for i in compressed_natural_gas_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'orange').add_to(compressed_natural_gas_feature_group.add_to(base_map))
    
biodiesel_feature_group = folium.FeatureGroup(name = 'Biodiesel Fuel Stations', show = False)
for i in biodiesel_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'darkgreen').add_to(biodiesel_feature_group.add_to(base_map))
    
liquefied_feature_group = folium.FeatureGroup(name = 'Liquefied Fuel Stations', show = False)
for i in liquefied_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'darkblue').add_to(liquefied_feature_group.add_to(base_map))
    
hydrogen_feature_group = folium.FeatureGroup(name = 'Hydrogen Fuel Stations', show = False)
for i in hydrogen_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'darkred').add_to(hydrogen_feature_group.add_to(base_map))


# In[ ]:


hydrogen_fuel_stations


# In[ ]:


# All Fuel Stations 
"""
fuel_station_feature_group = folium.FeatureGroup(name = 'Fuel Stations', show = False)
fuel_station_m = HeatMap(data=fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#F76BE2', 1: 'black', .65: '#EA02C7'},  radius = 8, max_zoom=10)
fuel_station_m.add_to(fuel_station_feature_group.add_to(base_map))


# Electric 
electric_feature_group = folium.FeatureGroup(name = 'Electric Fuel Stations', show = False)
electric_fuel_m = HeatMap(data=electric_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#F76BE2', 1: 'black', .65: '#EA02C7'},  radius = 8, max_zoom=10)
electric_fuel_m.add_to(electric_feature_group.add_to(base_map))

# Ethanol
ethanol_feature_group = folium.FeatureGroup(name = 'Ethanol Fuel Stations', show = False)
ethanol_fuel_m = HeatMap(data=ethanol_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#F76BE2', 1: 'black', .65: '#EA02C7'},  radius = 8, max_zoom=10)
ethanol_fuel_m.add_to(ethanol_feature_group.add_to(base_map))

# Propane
propane_feature_group = folium.FeatureGroup(name = 'Propane Fuel Stations', show = False)
propane_fuel_m = HeatMap(data=propane_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#F76BE2', 1: 'black', .65: '#EA02C7'},  radius = 8, max_zoom=10)
propane_fuel_m.add_to(propane_feature_group.add_to(base_map))

# Compressed Natural Gas 
compressed_natural_gas_feature_group = folium.FeatureGroup(name = 'Compressed Natural Gas Fuel Stations', show = False)
compressed_natural_gas_fuel_m = HeatMap(data=electric_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#F76BE2', 1: 'black', .65: '#EA02C7'},  radius = 8, max_zoom=10)
compressed_natural_gas_fuel_m.add_to(compressed_natural_gas_feature_group.add_to(base_map))

# Biodiesel
biodiesel_feature_group = folium.FeatureGroup(name = 'Biodiesel Fuel Stations', show = False)
biodiesel_fuel_m = HeatMap(data=biodiesel_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#F76BE2', 1: 'black', .65: '#EA02C7'},  radius = 8, max_zoom=10)
biodiesel_fuel_m.add_to(biodiesel_feature_group.add_to(base_map))

# Liquefied
liquefied_feature_group = folium.FeatureGroup(name = 'Liquefied Fuel Stations', show = False)
liquefied_fuel_m = HeatMap(data=liquefied_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.2: '#F76BE2', 1: 'black', .4: '#EA02C7'},  radius = 8, max_zoom=10)
liquefied_fuel_m.add_to(liquefied_feature_group.add_to(base_map))

# Hydrogen
hydrogen_feature_group = folium.FeatureGroup(name = 'Hydrogen Fuel Stations', show = False)
hydrogen_fuel_m = HeatMap(data=hydrogen_fuel_stations[['Latitude', 'Longitude', 'Fuel Type Code']].groupby(['Latitude','Longitude']).sum().reset_index().values.tolist(),  
                        gradient={.2: '#F76BE2', 1: 'black', .4: '#EA02C7'},  radius = 8, max_zoom=10)
hydrogen_fuel_m.add_to(hydrogen_feature_group.add_to(base_map))
"""
    


# In[ ]:


# icons using plugins.BeautifyIcon
"""
for i in electric_fuel_stations.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'green').add_to(electric_feature_group.add_to(base_map))
"""


# In[ ]:


werner_pings['PingCount'].describe()


# In[ ]:


werner_pings_map = werner_pings[werner_pings['PingCount'] >= 700]
werner_pings_map['PingCount'].describe()


# In[ ]:


werner_pings_group = folium.FeatureGroup(name = 'Werner Ping Count', show = False)

# icons using plugins.BeautifyIcon

for i in werner_pings_map.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'blue').add_to(werner_pings_group.add_to(base_map))

werner_pings_map_red = werner_pings_map[werner_pings_map['PingCount'] <= 1000]
werner_pings_map_yellow = werner_pings_map[(werner_pings_map['PingCount'] > 1000) & (werner_pings_map['PingCount'] <= 1600)]
werner_pings_map_green = werner_pings_map[werner_pings_map['PingCount'] > 1600]

werner_pings_heated_group = folium.FeatureGroup(name = 'Heated Werner Ping Count')

for i in werner_pings_map_red.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'red').add_to(werner_pings_heated_group.add_to(base_map))

for i in werner_pings_map_yellow.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'yellow').add_to(werner_pings_heated_group.add_to(base_map))
    
for i in werner_pings_map_green.itertuples():
    folium.Circle(location=[i.Latitude, i.Longitude],
                  # popup=i.station_name, 
                  color = 'green').add_to(werner_pings_heated_group.add_to(base_map))


# In[ ]:


base_map


# In[ ]:


# aqua, blue
werner_m = HeatMap(data=werner_map[['latitude', 'longitude', 'trip_count_x']].groupby(['latitude','longitude']).sum().reset_index().values.tolist(),  
                   gradient={.4: '#FF0000', .65: '#931F05', 1: 'black'},  radius=8, max_zoom=10)

conway_m = HeatMap(data=conway_map[['Target Latitude', 'Target Longitude', 'Investment (Million USD)']].groupby(['Target Latitude','Target Longitude']).sum().reset_index().values.tolist(),  
                   gradient={.4: 'lime', 1: 'black', .65: 'green'},  radius = 8, max_zoom=10)

driver_m = HeatMap(data=driver_map[['LATITUDE', 'LONGITUDE', 'ADDRESS_TYPE_CD']].groupby(['LATITUDE','LONGITUDE']).count().reset_index().values.tolist(),  
                   gradient={.2: '#74B7FA', 1: 'black', .4: '#0256A9'},  radius = 8, max_zoom=10)

origin_van_m = HeatMap(data=origin_van_map[['LATITUDE_NB', 'LONGITUDE_NB', 'VisitCount']].groupby(['LATITUDE_NB','LONGITUDE_NB']).sum().reset_index().values.tolist(),  
                   gradient={.4: '#B87AFE', 1: 'black', .65: '#5403B0'},  radius = 8, max_zoom=10)

destination_van_m = HeatMap(data=destination_van_map[['LATITUDE_NB', 'LONGITUDE_NB', 'VisitCount']].groupby(['LATITUDE_NB','LONGITUDE_NB']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#FECF9E', 1: 'black', .65: '#FC8A13'},  radius = 8, max_zoom=10)

origin_ded_m = HeatMap(data=origin_ded_map[['LATITUDE_NB', 'LONGITUDE_NB', 'VisitCount']].groupby(['LATITUDE_NB','LONGITUDE_NB']).sum().reset_index().values.tolist(),  
                   gradient={.4: '#B87AFE', 1: 'black', .65: '#5403B0'},  radius = 8, max_zoom=10)

destination_ded_m = HeatMap(data=destination_ded_map[['LATITUDE_NB', 'LONGITUDE_NB', 'VisitCount']].groupby(['LATITUDE_NB','LONGITUDE_NB']).sum().reset_index().values.tolist(),  
                        gradient={.4: '#FECF9E', 1: 'black', .65: '#FC8A13'},  radius = 8, max_zoom=10)

conway_m.add_to(folium.FeatureGroup(name = 'Conway Investment in Millions', show = False).add_to(base_map))

driver_m.add_to(folium.FeatureGroup(name = 'Driver Domiciles Count', show = False).add_to(base_map))


origin_van_m.add_to(folium.FeatureGroup(name = 'Van Origin Trip Count', show = False).add_to(base_map))

destination_van_m.add_to(folium.FeatureGroup(name = 'Van Destination Trip Count', show = False).add_to(base_map))

origin_ded_m.add_to(folium.FeatureGroup(name = 'Dedicated Origin Trip Count', show = False).add_to(base_map))

destination_ded_m.add_to(folium.FeatureGroup(name = 'Dedicated Destination Trip Count', show = False).add_to(base_map))

werner_m.add_to(folium.FeatureGroup(name = 'Werner Trip Count', show = False).add_to(base_map))

# legend = folium.raster_layers.ImageOverlay(name = 'Legend',
#                                                image = 'Legend.png', 
#                                                bounds = [[-38, -28], [40,60]], 
#                                                opacity = 0.5,
#                                                zindex = 1)

# legend.add_to(base_map)

from folium.plugins import FloatImage


FloatImage('https://raw.githubusercontent.com/kimberlyesmith/map/main/Legend2.PNG', bottom=5, left=10).add_to(base_map)

folium.LayerControl(sortLayers = False).add_to(base_map)


base_map


# In[ ]:





# In[ ]:


base_map.save('layered_heatmap_latest_2_26.html')


# In[ ]:





# In[ ]:



"""
origin_m = HeatMap(data=origin_map[['LATITUDE_NB', 'LONGITUDE_NB', 'VisitCount']].groupby(['LATITUDE_NB','LONGITUDE_NB']).sum().reset_index().values.tolist(),  
                   gradient={.4: 'yellow', 1: 'black', .65: 'orange'},  radius = 8, max_zoom=10)

destination_m = HeatMap(data=destination_map[['LATITUDE_NB', 'LONGITUDE_NB', 'VisitCount']].groupby(['LATITUDE_NB','LONGITUDE_NB']).sum().reset_index().values.tolist(),  
                        gradient={.4: 'aqua', 1: 'black', .65: 'blue'},  radius = 8, max_zoom=10)
"""

"""
origin_m.add_to(folium.FeatureGroup(name = 'Origin Trip Count').add_to(base_map))

destination_m.add_to(folium.FeatureGroup(name = 'Destination Trip Count').add_to(base_map))
"""


# In[ ]:


fuel_stations['Fuel Type Code'].unique()


# In[ ]:


from folium.plugins import FloatImage

# https://raw.githubusercontent.com/SECOORA/static_assets/master/maps/img/rose.png

url = (
    "https://github.com/kimberlyesmith/map/blob/main/Legend.png"
)

url2 = ("Legend.png")

m = folium.Map([-13, -38.15], zoom_start=10)

FloatImage(url, bottom=40, left=65).add_to(m)

m


# In[ ]:


m.save('test.png')


# In[ ]:





# In[ ]:





# In[ ]:




