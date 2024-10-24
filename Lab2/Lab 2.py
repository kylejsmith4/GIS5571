import arcpy
import os
import urllib.request

#Make folder for Lab 2 Part 1

Lab_2_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1"
os.makedirs(Lab_2_folder, exist_ok=True)
Lab_2_folder

# Make folder for Lidar data
Lidar_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar"
os.makedirs(Lidar_folder, exist_ok=True)

# Define local directory and file paths
local_directory = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar"
url = "https://resources.gisdata.mn.gov/pub/data/elevation/lidar/examples/lidar_sample/las/4342-12-05.las"
las_file_path = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\4342-12-05.las"

# Download 
las_file_path, _ = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\4342-12-05.las"


# Convert LAS file to DEM
dem_output = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\dem_output.tif"

# LAS dataset to DEM with 1m resolution
dem_output = arcpy.conversion.LasDatasetToRaster(
    in_las_dataset=las_file_path,  # Use the downloaded LAS file path
    out_raster=dem_output,         # Output raster file
    value_field="ELEVATION",
    interpolation_type="BINNING AVERAGE LINEAR",
    data_type="FLOAT",
    sampling_type="CELLSIZE",
    sampling_value=1,
    z_factor=1
)

# Print output path
print(f"DEM created at: {dem_output}")

las_dataset = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\4342-12-05.las"
dem_output = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\dem_output.tif"
output_tin = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\output_tin"

# Create TIN from DEM
output_tin = arcpy.ddd.RasterTin(
    in_raster=dem_output,  
    out_tin=output_tin,    
    z_tolerance=10.68,
    max_points=1500000,
    z_factor=1
)

output_tin

dem_output = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\dem_output.tif"
pdf_dem = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\dem_map.pdf"

# Load Arc pro
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Create a new map 
dem_map = aprx.createMap("DEM Map")
layer = dem_map.addDataFromPath(dem_output)
# Remove existing ESRI standard basemaps
for lyr in dem_map.listLayers():
    if lyr.isBasemapLayer:
        dem_map.removeLayer(lyr)


# layout
layout = aprx.listLayouts()[0]  

# Map frame
map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]  
map_frame.map = dem_map


# Export the layout to PDF 
layout.exportToPDF(pdf_dem, resolution=300)

pdf_dem

output_tin = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\output_tin"
pdf_tin = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\tin_map.pdf"

# Load Arc pro
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Create a new map 
tin_map = aprx.createMap("TIN Map")
layer = tin_map.addDataFromPath(output_tin)


# Remove existing ESRI standard basemaps
for lyr in tin_map.listLayers():
    if lyr.isBasemapLayer:
        tin_map.removeLayer(lyr)


# layout
layout = aprx.listLayouts()[1]  

# Map frame
map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]  
map_frame.map = tin_map


# Export the layout to PDF 
layout.exportToPDF(pdf_tin, resolution=100)

pdf_tin


a. Downloads .LAS files from MN DNR 
b. Converts the .LAS file into both a DEM and a TIN
c. Saves the new DEM and TIN to disk
d. Exports PDFs of the DEM and TIN with correct visualization

las_file_path = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar\4342-12-05.las"


LAS File 4342-12-05.las 
Location C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Lidar 
Elevation 246.53 m 
Coordinates 93.8627929°W 44.6349912°N




import requests
import zipfile
import os
import arcpy

#Make folder for Prism
Prism_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism"
os.makedirs(Prism_folder, exist_ok=True)
#Prism_folder  

# PRISM data
url = "https://ftp.prism.oregonstate.edu/normals/monthly/4km/ppt/PRISM_ppt_30yr_normal_4kmM4_all_bil.zip"
output_zip = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_all_bil.zip"

# Download zip file
response = requests.get(url)
with open(output_zip, 'wb') as file:
    file.write(response.content)

# Extract zip
extract_to = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism"
with zipfile.ZipFile(output_zip, 'r') as zip_ref:
    zip_ref.extractall(extract_to)
    
#extract_to

output_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism"

prism_bil_file_paths = [
    os.path.join(extract_to, f"PRISM_ppt_30yr_normal_4kmM4_{str(i).zfill(2)}_bil.bil")
    for i in range(1, 13)
]

# Loop through each and convert to point shapefile
for bil_file in prism_bil_file_paths:
    base_name = os.path.basename(bil_file).replace('.bil', '.shp')
    output_shapefile = os.path.join(output_folder, base_name)

    try:
        arcpy.conversion.RasterToPoint(
            in_raster=bil_file,
            out_point_features=output_shapefile,
            raster_field="Value"
        )
        print(f"Successfully converted {bil_file} to {output_shapefile}")
    except Exception as e:
        print(f"Error converting {bil_file}: {e}")
        
        
# this task takes a long time        
        
        

#List of shapefiles newly converted from .bil
shapefile_list = ["C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_01_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_02_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_03_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_04_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_05_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_06_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_07_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_08_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_09_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_10_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_11_bil.shp",
                  "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_ppt_30yr_normal_4kmM4_12_bil.shp"]
                  

output_merged_shapefile = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\Merged_PRISM.shp"

output_merged_shapefile = arcpy.management.Merge(shapefile_list, output_merged_shapefile)
output_merged_shapefile
    
# this task also takes a long time        
    

output_merged_shapefile = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\Merged_PRISM.shp"


arcpy.management.AddField(output_merged_shapefile, "Year", "LONG")
arcpy.management.AddField(output_merged_shapefile, "Date", "DATE")

# Populate the Year and Date fields
with arcpy.da.UpdateCursor(output_merged_shapefile, ["Year", "Date"]) as cursor:
    year = 1991
    for row in cursor:
        row[0] = year
        row[1] = f"{year}-01-01"
        cursor.updateRow(row)
        year += 1
        if year > 2020:
            year = 1991
            
# this task also takes a long time        
            

output_merged_shapefile = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\Merged_PRISM.shp"
Merged_PRISM_spatial = "C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\Merged_PRISM_spatial.shp"

# WGS 1984
input_coordinate_system = arcpy.SpatialReference(4326)  
arcpy.management.DefineProjection(output_merged_shapefile, input_coordinate_system)

# NAD83 / UTM Zone 15N
coordinate_system = arcpy.SpatialReference(26915)  
arcpy.management.Project(output_merged_shapefile, Merged_PRISM_spatial, coordinate_system)


# this task also takes a long time        


Merged_PRISM_spatial = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\Merged_PRISM_spatial.shp"
prism_st_cube = r"C:\Mac\Home\Documents\ArcGIS\Projects\Lab 2.1\Prism\PRISM_st_cube.nc"

# Create the Time-Space Cube from defined locations
arcpy.stpm.CreateSpaceTimeCubeDefinedLocations(
    in_features=Merged_PRISM_spatial,
    output_cube=prism_st_cube,
    location_id="pointid", 
    temporal_aggregation="NO_TEMPORAL_AGGREGATION",
    time_field="Date",  
    time_step_interval="1 Years", 
    time_step_alignment="START_TIME", 
    reference_time=None,  
    variables="grid_code ZEROS",  
    summary_fields=None, 
    in_related_table=None, 
    related_location_id=None  
)


prism_st_cube

# this task also takes a long time 



#### This is where I am stuck .... loading the cube to annimation