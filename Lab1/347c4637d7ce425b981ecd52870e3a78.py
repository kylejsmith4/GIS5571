#!/usr/bin/env python
# coding: utf-8

# # GIS 5571 Lab 1
# 
# ## Kyle Smith, smi02542@umn.edu
# 
# ----

# #### Python packages

# In[244]:


# !pip install arcgis
# !pip install shapely
# !pip install ipywidgets 


# In[3]:


import os
import json
import requests
import zipfile
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from osgeo import ogr
from pyproj import Transformer
from shapely import wkt
from arcgis.gis import GIS
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.geometry import Geometry, Polyline, SpatialReference
from arcgis.mapping import WebMap
from arcgis.widgets import MapView
import shapefile
import ipywidgets  as widgets
import warnings

gis = GIS()

warnings.simplefilter(action='ignore', category=FutureWarning)


# # * Download three datasets (one from each API), convert to spatially enabled databases & same coordinate reference system

# #### 1. Minnesota Geospatial Commons API (Strategic_Highways)

# Dataset: National Highway System, Truck Network, and Strategic Highway Network - https://gisdata.mn.gov/dataset/trans-federal-routes
# Specifically, I will use the "Strategic_Highway_Network_in_Minnesota" feature service, which only includes roads identified as priority routes for national defense purposes. 

# In[246]:


# Use CKAN to search MN Geospatial Commons for "trans-federal-routes" 
api = "https://gisdata.mn.gov/api/3/action/package_search?q=trans-federal-routes"

# Request to GET from the API
response = requests.get(api)

# Load the JSON extracted from API search results 
json_data = response.json()

# Find the path in JSON for 'trans-federal-routes'
zip_url = json_data['result']['results'][0]['resources'][0]['url']
zip_url

# Download the zip file
zip_file_path = 'trans_federal_routes.zip'
with requests.get(zip_url, stream=True) as r:
    with open(zip_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            
# Extract the ZIP file
extraction_path = "trans_federal_routes_data"
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extraction_path)

# List the extracted files
extracted_files = os.listdir(extraction_path)
#extracted_files

# looking for .... trans_federal_routes_data/Strategic_Highway_Network_in_Minnesota.shp
file_path = 'trans_federal_routes_data/Strategic_Highway_Network_in_Minnesota.shp'

# Make a Spatially Enabled DataFrame and check it
sdf_Strategic_Highways = pd.DataFrame.spatial.from_featureclass(file_path)
#sdf_Strategic_Highways.head()

#geometry is in SHAPE column
#Make it spatial and set sr
sdf_Strategic_Highways = pd.DataFrame.spatial.from_df(sdf_Strategic_Highways, geometry_column='SHAPE', sr=4326)
sdf_Strategic_Highways.head()


# In[247]:


print("Spatial Reference = ", sdf_Strategic_Highways.spatial.sr)


# In[248]:


# Save as CSV
sdf_Strategic_Highways.to_csv('/home/smi02542/Lab_1__MNGeo_Strategic_Highways.csv', index=False)


# #### 2. REST API (mn_counties)

# Dataset: County boundaries in Minnesota (polygons) - https://webgis.dot.state.mn.us/65agsf1/rest/services/sdw_govnt/COUNTY/FeatureServer/0

# In[249]:


# REST API URL
api = 'https://webgis.dot.state.mn.us/65agsf1/rest/services/sdw_govnt/COUNTY/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=pjson'


# Request data from the API
r = requests.get(api)
data = r.json()

# Create a FeatureSet from the JSON data
fs = FeatureSet.from_dict(data)

# Create a Spatially Enabled DataFrame from the FeatureSet
sdf_mn_counties = fs.sdf


# Project the DataFrame to WGS 84 (WKID 4326)
if sdf_mn_counties.spatial.sr is None:
    sdf_mn_counties.spatial.set_geometry('SHAPE', sr={'wkid': 4326}) 
sdf_mn_counties.spatial.project(4326)

print("Spatial Reference = ", sdf_mn_counties.spatial.sr)


# In[250]:


sdf_mn_counties.head()


# In[251]:


#make a csv
sdf_mn_counties.to_csv('/home/smi02542/Lab_1__REST_MN_counties.csv', index=False)


# #### 3. NDAWN

# Using available data from NDAWN, find the monthly average max temp and annual monthly min temp for a 96 month period at a NDAWN site in north Minnesota and south Minnesota
# 
#     -- NDAWN Station: Humboldt, MN (Station ID 4) - site in north Minnesota 
#     -- NDAWN Station: Becker, MN (Station ID 118) - site in south Minnesota 

# In[252]:


#Call api from NDAWN
api = 'https://ndawn.ndsu.nodak.edu/table.csv?station=118&station=4&variable=mdmxt&variable=mdmnt&year=2024&ttype=monthly&quick_pick=4_y&begin_date=2019-01&count=12'
#api is comma delimited csv file

#view api path on web (JSON) as it does not open as a data frame in current form


#columns / rows appear to be missalligned because raw NDAWNS csv header rows are merged
#To fix, skip rows 0, 1, 2, 4
#Column headers are row 3

#Pandas create a data frame and skip rows  0, 1, 2, 4
df = pd.read_csv(api, skiprows=[0, 1, 2, 4])

#For simplicity, Can also skip/drop columns 3,7,8,10,11 
df = df.drop(df.columns[[3,7,8,10,11]], axis=1)

NDAWN_station_data = pd.DataFrame(df)
#NDAWN_station_data



#View NDAWN_station_data
#Should be 96 rows and columns: Name / Latitude / Longitude / year / Month / Max / Min 
#NDAWN_station_data

# Now, calculate the mean of Max Temp and Min Temp for each station, and round to two decimal points so cleaner
# Group by 'Station Name' and calculate the mean for 'Avg Max Temp' and 'Avg Min Temp', rounding to 2 decimal places
sdf_grouped = df.groupby('Station Name')[['Avg Max Temp', 'Avg Min Temp', 'Latitude', 'Longitude']].mean().round(5)

#sdf_grouped

#convert latitude and longitude to point geometry
sdf_NDAWN = GeoAccessor.from_xy(sdf_grouped, x_column='Longitude', y_column='Latitude', sr=4326)
sdf_NDAWN


# So the average max temperature for the 96 month period at Humboldt, MN (north Minnesota) is about 5.23 degrees cooler then the the average max temperature for Becker, MN (south Minnesota). 
# Further, the average min termperature for the 96 month period at Becker, MN (south Minnesota) is about 6.87 degrees warmer then the the average min temperature for Humboldt, MN (north Minnesota).
# 
# Mind blown?

# In[253]:


#Fully monthly Station data for the two sites can be downloaded to a csv
NDAWN_station_data.to_csv('/home/smi02542/Lab_1_NDAWN_station_data.csv', index=False)

#Station averages can be downloaded to a csv
sdf_NDAWN.to_csv('/home/smi02542/Lab_1__NDAWNS_merged.csv', index=False)

print("Spatial Reference = ", sdf_NDAWN.spatial.sr)


# # * Spatially join two of the three datasets

# I want to spatially join Minnesota Counties and NDAWN - Becker & Humboldt, MN datasets. From the joined database, I can identify the county names for each of the NDAWN sites used here. 
# 
#       sdf_mn_counties 
#         -polygon geometry in column = 'SHAPE'{"rings}
#         -county name in column = 'COUNTY_NAME'
# 
#       sdf_NDAWN
#         -station name in column = 'Station Name'
#         -point geometry in column = 'SHAPE'
#         
#       Find NDAWN points that are within sdf_mn_counties polygons
# 

# In[254]:


#sdf_NDAWN.head()
#sdf_mn_counties.head()


# In[255]:


#Ensure both dataframes are spatially enabled
sdf_mn_counties.spatial.set_geometry('SHAPE')
sdf_NDAWN.spatial.set_geometry('SHAPE')


# In[256]:


# Reset indexes
sdf_mn_counties = sdf_mn_counties.reset_index()
sdf_NDAWN = sdf_NDAWN.reset_index()


# In[257]:


# Do the spatial join ... NDAWN points  within sdf_mn_counties 

spatial_join = sdf_NDAWN.spatial.join(sdf_mn_counties, how='left', op='within')
spatial_join.spatial.set_geometry('SHAPE')
print("Minnesota County name for selected NDAWN sites:")
print(spatial_join[['Station Name', 'COUNTY_NAME']])


# In[258]:


#spatial_join.head()
#sdf_NDAWN.columns
#sdf_mn_counties.columns


# To summarize...
# 
# The two NDAWN sites in Minnesota choosen for this project are:
#     
#         -- Becker, MN is in Sherburne County, Minnesota
#         -- Humboldt, MN is in Kittson County, Minnesota

# # * Print head of the table showing the merged attributes

# In[259]:


spatial_join


# In[260]:


#Saved spatial joined table
spatial_join.to_csv('/home/smi02542/Lab_1__Joined_Set.csv', index=False)


# # * Save the integrated dataset to a geodatabase

# In[261]:


# Save the Statial Join DataFrame to geodatabase
#spatial_join

Lab_1__Joined_Set = spatial_join
feature_class_name = 'Lab_1__Joined_Set'  
output_path_join = spatial_join.spatial.to_featureclass(location=f'/home/smi02542/Lab_1__Joined_Set.gdb/{feature_class_name}')
output_path_join


# In[4]:


#View map at: https://umn.maps.arcgis.com/apps/mapviewer/index.html?webmap=9370a56b1f634d50a94a9534bca2ba4d
# Title: Lab 1 map  | Type: Web Map | Owner: smi02542_UMN
item = gis.content.get("9370a56b1f634d50a94a9534bca2ba4d")
item


# # * Saved files from this notebook

# #### 1. Minnesota Geospatial Commons API (Strategic_Highways)

# In[205]:


print("Spatial Reference = ", sdf_Strategic_Highways.spatial.sr)


# csv at '/home/smi02542/Lab_1__Joined_Set.gdb/Lab_1__MNGeo_Strategic_Highways.csv'

# In[206]:


sdf_Strategic_Highways.head()


# #### 2. REST API (mn_counties)

# In[207]:


print("Spatial Reference = ", sdf_mn_counties.spatial.sr)


# csv at /home/smi02542/Lab_1__Joined_Set.gdb/Lab_1__REST_MN_counties.csv

# In[191]:


sdf_mn_counties.head()


# #### 3. NDAWN

# In[ ]:


print("Spatial Reference = ", sdf_NDAWN.spatial.sr)


# csv at 
# 
# /home/smi02542/Lab_1__Joined_Set.gdb/Lab_1_NDAWN_station_data.csv
# /home/smi02542/Lab_1__Joined_Set.gdb/Lab_1__NDAWNS_merged.csv

# In[204]:


NDAWN_station_data.head()


# In[193]:


sdf_NDAWN.head()


# #### Spatial Join

# In[211]:


print("Spatial Reference = ", spatial_join.spatial.sr)


# csv & shp at 
# 
# /home/smi02542/Lab_1__Joined_Set.gdb/Lab_1__Joined_Set.csv
# /home/smi02542/Lab_1__Joined_Set.gdb/Lab_1__Joined_Set.shp

# In[194]:


spatial_join.head()

