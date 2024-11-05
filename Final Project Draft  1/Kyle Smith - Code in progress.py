import arcpy
import requests
import json
from arcgis.features import FeatureSet
from arcgis.geometry import SpatialReference
import os

# Set up the ArcGIS Pro project and map
project_path = r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.aprx"
project = arcpy.mp.ArcGISProject(project_path)
map_obj = project.listMaps("LA_County_Final_Project_Map")[0]

project_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt"

# LA County Boundaries .... Project Area and use to clip other data 
la_co_boundary_api = "https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13"

# Add the Feature Layer to the map
layer_name = "LA_co_boundary"
arcpy.MakeFeatureLayer_management(la_co_boundary_api, layer_name)

# Verify layer existence in map before adding
if layer_name not in layer_names:
    map_obj.addDataFromPath(la_co_boundary_api)

print("Feature layer 'LA_co_boundary' added to the map.")



# Manually set symbology for 'LA_County_Boundary.shp' - county lines

# Fire Zones REST API URL
fire_zones_api = "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSZ_SRA_LRA_Combined/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Fire_Zones_All_CA"
layer_name = "Fire_Zones_All_CA"
arcpy.MakeFeatureLayer_management(fire_zones_api, layer_name)

#Clip 'Fire_Zones_All_CA to the LA County boundary

clipped_fire_zones = 'C:\\Mac\\Home\\Documents\\ArcGIS\\Projects\\5571_final_pjt\\clipped_fire_zones.shp'

# Clip the fire zones dataset to the LA County boundary
arcpy.analysis.Clip(in_features=fire_zones_api, clip_features=la_co_boundary_api, out_feature_class=clipped_fire_zones)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(clipped_fire_zones)

clipped_fire_zones

# Create a separate Feature Class for each 'Moderate', 'High', & 'Very High'

clipped_fire_zones = 'C:\\Mac\\Home\\Documents\\ArcGIS\\Projects\\5571_final_pjt\\clipped_fire_zones.shp'

Moderate_Fire_Zone = os.path.join(project_folder, "Moderate_Fire_Zone.shp")
High_Fire_Zone = os.path.join(project_folder, "High_Fire_Zone.shp")
Very_High_Fire_Zone = os.path.join(project_folder, "Very_High_Fire_Zone.shp")

# Create separate feature classes based on FHSZ values

# Moderate Zones (FHSZ = 1)
arcpy.Select_analysis(
    in_features=clipped_fire_zones,
    out_feature_class=Moderate_Fire_Zone,
    where_clause="FHSZ = 1"
    )
print("Feature class for 'Moderate_Fire_Zone' created at:", Moderate_Fire_Zone)

# HIgh Zones (FHSZ = 2)
arcpy.Select_analysis(
    in_features=clipped_fire_zones,
    out_feature_class=High_Fire_Zone,
    where_clause="FHSZ = 2"
    )
print("Feature class for 'High_Fire_Zone' created at:", High_Fire_Zone)

# Very High Zones (FHSZ = 3)
arcpy.Select_analysis(
    in_features=clipped_fire_zones,
    out_feature_class=Very_High_Fire_Zone,
    where_clause="FHSZ = 3"
    )
print("Feature class for 'Very_High_Fire_Zone' created at:", Very_High_Fire_Zone)

# Manually set symbology based on 'FHSZ' value ...

### Value 1 = Label "Moderate" & color yellow
### Value 2 = Label "High" & color orange
### Value 3 = Label "Very High" & color red



# Historic Fire Maps
historic_fire_maps_api = "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/California_Historic_Fire_Perimeters/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Historic_fire_maps_CA"
layer_name = "Historic_fire_maps_CA"
arcpy.MakeFeatureLayer_management(historic_fire_maps_api, layer_name)

#Clip 'Historic_fire_maps_CA' to the LA County boundary
la_co_boundary_api = "https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13"
clipped_historic_fires = 'C:\\Mac\\Home\\Documents\\ArcGIS\\Projects\\5571_final_pjt\\clipped_historic_fires.shp'

# Clip the historic fires dataset to the LA County boundary
arcpy.analysis.Clip(in_features=historic_fire_maps_api, clip_features=la_co_boundary_api, out_feature_class=clipped_historic_fires)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(clipped_historic_fires)

clipped_historic_fires    

# Manually set symbology for 'clipped_historic_fires'
# Remove 'Historic_fire_maps_CA' 

# Current Fire Maps
current_fire_maps_api = "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/CA_Perimeters_NIFC_FIRIS_public_view/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Current_fire_maps_CA"
layer_name = "Current_fire_maps_CA"
arcpy.MakeFeatureLayer_management(current_fire_maps_api, layer_name)

#Clip 'Current_fire_maps_CA' to the LA County boundary
la_co_boundary_api = "https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13"
clipped_current_fires = 'C:\\Mac\\Home\\Documents\\ArcGIS\\Projects\\5571_final_pjt\\clipped_current_fires.shp'

# Clip the current fires dataset to the LA County boundary
arcpy.analysis.Clip(in_features=current_fire_maps_api, clip_features=la_co_boundary_api, out_feature_class=clipped_current_fires)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(clipped_current_fires)

clipped_current_fires    

# Manually set symbology for 'clipped_current_fires  '
# Remove 'Current_fire_maps_CA' 

# Merge / Join / Union ‘Historic Fire Maps’ and ‘Current Fire Maps’

#2012 Land Use


Land_Use_2012 = "https://services5.arcgis.com/YzWImMY4GtDcMxOx/arcgis/rest/services/2016_Land_Use_Information_for_Los_Angeles_County2/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Land_Use_2012"
layer_name = "Land_Use_2012"
arcpy.MakeFeatureLayer_management(Land_Use_2012, layer_name)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(Land_Use_2012)

Land_Use_2012

# Manually set symbology for 'Land_Use_2012' based on 'LU12' field ... 
### 'LU12' Values '1110 - 1150' only need. Remove all others and group 'LU12' Values '1110 - 1150' as a single symbology colored light green 

#2016 Land Use


Land_Use_2016 = "https://services5.arcgis.com/YzWImMY4GtDcMxOx/arcgis/rest/services/2016_Land_Use_Information_for_Los_Angeles_County2/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Land_Use_2016"
layer_name = "Land_Use_2016"
arcpy.MakeFeatureLayer_management(Land_Use_2016, layer_name)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(Land_Use_2016)

Land_Use_2016

# Manually set symbology for 'Land_Use_2016' based on 'LU16' field ... 
### 'LU16' Values '1110 - 1150' only need. Remove all others and group 'LU12' Values '1110 - 1150' as a single symbology colored light green 

#2019 Land Use


Land_Use_2019 = "https://services5.arcgis.com/vYSHcRQuTn4O8o35/arcgis/rest/services/2019_Regional_Land_Use_Information_for_Los_Angeles_County/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Land_Use_2019"
layer_name = "Land_Use_2019"
arcpy.MakeFeatureLayer_management(Land_Use_2019, layer_name)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(Land_Use_2019)

Land_Use_2019

# Manually set symbology for 'Land_Use_2019' based on 'LU19' field ... 
### 'LU19' Values '1110 - 1150' only need. Remove all others and group 'LU19' Values '1110 - 1150' as a single symbology colored light red 



#### Remove LU Fiel



# Draw 1 mile buffer around each fire zone (moderate, high, very high)

# Input and output paths
clipped_fire_zones = r'C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\clipped_fire_zones.shp'
Moderate_Fire_Zone_Buffer = r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.gdb\Moderate_Fire_Zone_Buffer"

# Create a 1-mile buffer around Moderate Fire Zone
arcpy.analysis.PairwiseBuffer(
    in_features="Pairwise Buffer Input Features (Polygons)",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.gdb\Moderate_Fire_Zone_Buffer",
    buffer_distance_or_field="1 MilesInt",
    dissolve_option="ALL",
    dissolve_field=None,
    method="PLANAR",
    max_deviation="0 Meters"
)

# Create a 1-mile buffer around High Fire Zone

arcpy.analysis.PairwiseBuffer(
    in_features=r"Fire_Zones\High_Fire_Zone",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.gdb\High_Fire_Zone_Buffer",
    buffer_distance_or_field="1 MilesInt",
    dissolve_option="ALL",
    dissolve_field=None,
    method="PLANAR",
    max_deviation="0 Meters"
)

# Create a 1-mile buffer around Very High Fire Zone

arcpy.analysis.PairwiseBuffer(
    in_features=r"Fire_Zones\Very_High_Fire_Zone",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.gdb\Very_High_Fire_Zone_Buffer",
    buffer_distance_or_field="1 MilesInt",
    dissolve_option="ALL",
    dissolve_field=None,
    method="PLANAR",
    max_deviation="0 Meters"
)

# Create a 1-mile buffer around ALL Fire Zones layer 'clipped_fire_zones'

arcpy.analysis.PairwiseBuffer(
    in_features=r"Fire_Zones\Very_High_Fire_Zone",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.gdb\clipped_Fire_Zone_Buffer",
    buffer_distance_or_field="1 MilesInt",
    dissolve_option="ALL",
    dissolve_field=None,
    method="PLANAR",
    max_deviation="0 Meters"
)

# Adjust symbology of buffer layers in Arc Pro

#select only residential LU polygons within that buffer for use in analysis as areas beyond 1 mile from a fire zone are not likely to be impacted


Land_Use_2012 = "https://services5.arcgis.com/YzWImMY4GtDcMxOx/arcgis/rest/services/2016_Land_Use_Information_for_Los_Angeles_County2/FeatureServer/0"
Land_Use_2016 = "https://services5.arcgis.com/YzWImMY4GtDcMxOx/arcgis/rest/services/2016_Land_Use_Information_for_Los_Angeles_County2/FeatureServer/0"
Land_Use_2019 = "https://services5.arcgis.com/YzWImMY4GtDcMxOx/arcgis/rest/services/2019_Land_Use_Information_for_Los_Angeles_County2/FeatureServer/0"

clipped_Fire_Zone_Buffer = "C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\5571_final_pjt.gdb\clipped_Fire_Zone_Buffer"


# Select LU_12 residential polygons within the buffer
arcpy.management.SelectLayerByLocation(
    in_layer=r"Land_Use\Land_Use_2012",
    overlap_type="INTERSECT",
    select_features=r"Fire_Zones\clipped_Fire_Zone_Buffer",
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)

# Select LU_16 residential polygons within the buffer
arcpy.management.SelectLayerByLocation(
    in_layer=r"Land_Use\Land_Use_2016",
    overlap_type="INTERSECT",
    select_features=r"Fire_Zones\clipped_Fire_Zone_Buffer",
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)


# Select LU_19 residential polygons within the buffer
arcpy.management.SelectLayerByLocation(
    in_layer=r"Land_Use\Land_Use_2019",
    overlap_type="INTERSECT",
    select_features=r"Fire_Zones\clipped_Fire_Zone_Buffer",
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)

# Select LU_16 residential polygons within the buffer
arcpy.management.SelectLayerByLocation(
    in_layer=r"Land_Use\Land_Use_2016",
    overlap_type="INTERSECT",
    select_features="Select Layer By Location Selecting Features (Polygons)",
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)





# Data Paths:



#Intersect Residential Areas with each Fire Zone in each year

arcpy.Intersect_analysis(["Selected_Residential_Land_Use", "Selected_Fire_Hazard_Zones"], "Intersected_Risk_Residential")


