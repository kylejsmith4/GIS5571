#Make map "NDAWN_Map"
#Make new GDB "NDAWN_L3.gdb"

import pandas as pd
import arcpy
import requests
import csv
import numpy as np
import matplotlib.pyplot as plt

# Define file paths and variables
api_url = r"https://ndawn.ndsu.nodak.edu/table.csv?station=78&station=111&station=98&station=162&station=174&station=142&station=164&station=138&station=161&station=9&station=160&station=224&station=159&station=10&station=229&station=118&station=56&station=165&station=11&station=12&station=58&station=13&station=84&station=218&station=55&station=179&station=7&station=186&station=87&station=14&station=15&station=96&station=191&station=16&station=210&station=201&station=137&station=124&station=143&station=17&station=85&station=226&station=140&station=134&station=18&station=136&station=219&station=65&station=104&station=99&station=192&station=19&station=227&station=129&station=20&station=101&station=166&station=178&station=81&station=21&station=97&station=22&station=75&station=184&station=2&station=211&station=172&station=139&station=158&station=23&station=157&station=220&station=62&station=86&station=24&station=89&station=126&station=223&station=167&station=93&station=183&station=90&station=25&station=205&station=83&station=107&station=156&station=77&station=26&station=155&station=70&station=127&station=144&station=27&station=173&station=132&station=28&station=195&station=185&station=29&station=30&station=154&station=31&station=187&station=102&station=32&station=119&station=4&station=217&station=80&station=33&station=59&station=153&station=105&station=82&station=225&station=34&station=198&station=72&station=135&station=35&station=76&station=120&station=209&station=141&station=109&station=36&station=207&station=79&station=193&station=71&station=212&station=37&station=38&station=189&station=39&station=130&station=73&station=188&station=40&station=41&station=54&station=228&station=69&station=194&station=145&station=214&station=113&station=128&station=42&station=43&station=103&station=171&station=116&station=196&station=88&station=114&station=3&station=163&station=200&station=216&station=64&station=115&station=168&station=67&station=175&station=146&station=170&station=197&station=44&station=206&station=133&station=106&station=100&station=121&station=45&station=46&station=61&station=66&station=181&station=74&station=213&station=60&station=199&station=125&station=176&station=177&station=8&station=180&station=204&station=47&station=221&station=122&station=108&station=5&station=152&station=48&station=151&station=147&station=68&station=169&station=49&station=50&station=91&station=182&station=117&station=63&station=150&station=51&station=6&station=222&station=52&station=92&station=112&station=131&station=123&station=95&station=53&station=203&station=190&station=208&station=57&station=149&station=148&station=202&station=215&station=110&variable=mdmxt&variable=mdmnt&variable=mdavt&year=2024&ttype=monthly&quick_pick=1_m&begin_date=2023-11&count=12"
csv_path = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_all_30_days.csv"
cleaned_csv_path = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_cleaned_30_days.csv"
gdb_name = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_L3.gdb"
NDAWN_table = "NDAWN_Data_30day_temps"
ndawn_fc = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_Stations.shp"
x_field = "Longitude"
y_field = "Latitude"


#NDAWN api
api_url = r"https://ndawn.ndsu.nodak.edu/table.csv?station=78&station=111&station=98&station=162&station=174&station=142&station=164&station=138&station=161&station=9&station=160&station=224&station=159&station=10&station=229&station=118&station=56&station=165&station=11&station=12&station=58&station=13&station=84&station=218&station=55&station=179&station=7&station=186&station=87&station=14&station=15&station=96&station=191&station=16&station=210&station=201&station=137&station=124&station=143&station=17&station=85&station=226&station=140&station=134&station=18&station=136&station=219&station=65&station=104&station=99&station=192&station=19&station=227&station=129&station=20&station=101&station=166&station=178&station=81&station=21&station=97&station=22&station=75&station=184&station=2&station=211&station=172&station=139&station=158&station=23&station=157&station=220&station=62&station=86&station=24&station=89&station=126&station=223&station=167&station=93&station=183&station=90&station=25&station=205&station=83&station=107&station=156&station=77&station=26&station=155&station=70&station=127&station=144&station=27&station=173&station=132&station=28&station=195&station=185&station=29&station=30&station=154&station=31&station=187&station=102&station=32&station=119&station=4&station=217&station=80&station=33&station=59&station=153&station=105&station=82&station=225&station=34&station=198&station=72&station=135&station=35&station=76&station=120&station=209&station=141&station=109&station=36&station=207&station=79&station=193&station=71&station=212&station=37&station=38&station=189&station=39&station=130&station=73&station=188&station=40&station=41&station=54&station=228&station=69&station=194&station=145&station=214&station=113&station=128&station=42&station=43&station=103&station=171&station=116&station=196&station=88&station=114&station=3&station=163&station=200&station=216&station=64&station=115&station=168&station=67&station=175&station=146&station=170&station=197&station=44&station=206&station=133&station=106&station=100&station=121&station=45&station=46&station=61&station=66&station=181&station=74&station=213&station=60&station=199&station=125&station=176&station=177&station=8&station=180&station=204&station=47&station=221&station=122&station=108&station=5&station=152&station=48&station=151&station=147&station=68&station=169&station=49&station=50&station=91&station=182&station=117&station=63&station=150&station=51&station=6&station=222&station=52&station=92&station=112&station=131&station=123&station=95&station=53&station=203&station=190&station=208&station=57&station=149&station=148&station=202&station=215&station=110&variable=mdmxt&variable=mdmnt&variable=mdavt&year=2024&ttype=monthly&quick_pick=1_m&begin_date=2023-11&count=12"

#api is comma delimited csv file
#columns / rows appear to be missalligned because raw NDAWNS csv header rows are merged
#To fix, skip rows 0, 1, 2, 4
#Column headers are row 3

#Pandas create a data frame and skip rows  0, 1, 2, 4
df = pd.read_csv(api_url, skiprows=[0, 1, 2, 4])
df = pd.DataFrame(df)
df 

df.to_csv (cleaned_csv_path, index=False)

#Convert the CSV to a Feature Class
csv_path = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_all_30_days.csv"
gdb_name = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_L3.gdb"
ndawn_fc = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_Stations.shp"

spatial_reference = arcpy.SpatialReference(4326)

# Create points 
arcpy.management.XYTableToPoint(
    in_table=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_station_data_cleaned.csv",
    out_feature_class=ndawn_fc,
    x_field="Longitude",
    y_field="Latitude",
    coordinate_system=spatial_reference
)

# Feature Class 
aprx = arcpy.mp.ArcGISProject("CURRENT")
map_obj = aprx.listMaps()[3] 
map_obj.addDataFromPath(ndawn_fc)

print(f"Feature class created and added to map: {ndawn_fc}")

# Add to map "NDAWN_Map"
# Symbolize and add labels to map in ArcGIS Pro 

# IDW Max Temps - from ArcPro Geoprocessing Tool

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb"):
    out_raster = arcpy.sa.Idw(
        in_point_features="NDAWN_Stations",
        z_field="Avg_Max_Te",
        cell_size=0.021010908,
        power=2,
        search_radius="VARIABLE 12",
        in_barrier_polyline_features=None
    )

out_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Idw_NDAWN_Max")

# IDW Min Temps - from ArcPro Geoprocessing Tool

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb"):
    out_raster = arcpy.sa.Idw(
        in_point_features="NDAWN_Stations",
        z_field="Avg_Min_Te",
        cell_size=0.021010908,
        power=2,
        search_radius="VARIABLE 12",
        in_barrier_polyline_features=None
    )

out_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Idw_NDAWN_Min")

# Ordinary Kringling - Max Temps - from ArcPro Geoprocessing Tool

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb"):
    out_surface_raster = arcpy.sa.Kriging(
        in_point_features="NDAWN_Stations",
        z_field="Avg_Max_Te",
        kriging_model="Spherical # # # #",
        cell_size=0.021010908,
        search_radius="VARIABLE 12",
        out_variance_prediction_raster=None
    )

out_surface_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Kriging_NDAWN_Max")

# Ordinary Kringling - Min Temps - from ArcPro Geoprocessing Tool

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb"):
    out_surface_raster = arcpy.sa.Kriging(
        in_point_features="NDAWN_Stations",
        z_field="Avg_Min_Te",
        kriging_model="Spherical # # # #",
        cell_size=0.021010908,
        search_radius="VARIABLE 12",
        out_variance_prediction_raster=None
    )

out_surface_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Kriging_NDAWN_Min")

# LPI - Max Temp - from ArcPro Geoprocessing Tool

arcpy.ga.LocalPolynomialInterpolation(
    in_features="NDAWN_Stations_MaxTemps",
    z_field="Avg_Max_Te",
    out_ga_layer="Avg_Max_Te",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\lpi_NDAWN_Max",
    cell_size=0.021010908,
    power=1,
    search_neighborhood="NBRTYPE=Standard S_MAJOR=3.42563109432527 S_MINOR=3.42563109432527 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
    kernel_function="EXPONENTIAL",
    bandwidth=None,
    use_condition_number="NO_USE_CONDITION_NUMBER",
    condition_number=None,
    weight_field=None,
    output_type="PREDICTION"
)

out_surface_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\lpi_NDAWN_Max")

# LPI - Min Temp - from ArcPro Geoprocessing Tool

arcpy.ga.LocalPolynomialInterpolation(
    in_features="NDAWN_Stations_MinTemps",
    z_field="Avg_Min_Te",
    out_ga_layer="Avg_Min_Te",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\lpi_NDAWN_Min",
    cell_size=0.021010908,
    power=1,
    search_neighborhood="NBRTYPE=Standard S_MAJOR=3.42563109432527 S_MINOR=3.42563109432527 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
    kernel_function="EXPONENTIAL",
    bandwidth=None,
    use_condition_number="NO_USE_CONDITION_NUMBER",
    condition_number=None,
    weight_field=None,
    output_type="PREDICTION"
)

out_surface_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\lpi_NDAWN_Min")

#Validation_Layer (true values ... Avg_Max_Temp attribute)
NDAWN_Stations = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\NDAWN\NDAWN_Stations.shp"

Validate_LPI = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Validate_LPI"
Validate_Kringing = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Validate_Kringing"
Validate_IDW =r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Validate_IDW"

#Rasters for Max Temps
r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Idw_NDAWN_Max"
r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Kriging_NDAWN_Max"
r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\lpi_NDAWN_Max"


# Make Data Validation feature classes for each  - Extract Values to points (geoprocessing tool)

#LPI
arcpy.sa.ExtractValuesToPoints(
    in_point_features="NDAWN_Stations",
    in_raster="lpi_NDAWN_Max",
    out_point_features=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Validate_LPI",
    interpolate_values="INTERPOLATE",
    add_attributes="VALUE_ONLY"
)

Validate_LPI

#Kringing
arcpy.sa.ExtractValuesToPoints(
    in_point_features="NDAWN_Stations_Validation",
    in_raster="Kriging_NDAWN_Max",
    out_point_features=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Validate_Kringing",
    interpolate_values="INTERPOLATE",
    add_attributes="VALUE_ONLY"
)

Validate_Kringing

#IDW
arcpy.sa.ExtractValuesToPoints(
    in_point_features="NDAWN_Stations_Validation",
    in_raster="Idw_NDAWN_Max",
    out_point_features=r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\L3.gdb\Validate_IDW",
    interpolate_values="INTERPOLATE",
    add_attributes="VALUE_ONLY"
)


Validate_IDW

#Calculate Error


# New attribute .... Error = (Avg Max - RasterValue)


#LPI
arcpy.management.CalculateField(
    in_table="Validate_LPI",
    field="Error",
    expression="!Avg_Max_Te! - !RASTERVALU!",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

#Kringing
arcpy.management.CalculateField(
    in_table="Validate_Kringing",
    field="Error",
    expression="!Avg_Max_Te! - !RASTERVALU!",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

#IDW
arcpy.management.CalculateField(
    in_table="Validate_IDW",
    field="Error",
    expression="!Avg_Max_Te! - !RASTERVALU!",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)
