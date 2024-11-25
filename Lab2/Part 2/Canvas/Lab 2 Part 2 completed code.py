import os
import requests
import zipfile
import arcpy
from arcpy.sa import *

# Ensure Spatial Analyst extension is available
arcpy.CheckOutExtension("Spatial")

# Define the project and map
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Set up the folder for Dory's project
Dory_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\L3\Dory"
os.makedirs(Dory_folder, exist_ok=True)
arcpy.env.workspace = Dory_folder
arcpy.env.overwriteOutput = True

# Set spatial reference (NAD 1983 UTM Zone 15N)
spatial_ref = arcpy.SpatialReference(26915)  # EPSG code for NAD83 UTM Zone 15N
arcpy.env.outputCoordinateSystem = spatial_ref

# Function to download and extract zip files
def download_and_extract(url, zip_path, extract_to):
    if not os.path.exists(extract_to):
        try:
            response = requests.get(url)
            with open(zip_path, 'wb') as file:
                file.write(response.content)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"Downloaded and extracted to {extract_to}")
        except Exception as e:
            print(f"Failed to download or extract {url}: {e}")
    else:
        print(f"Data already extracted at {extract_to}")

# Function to create a point feature class
def create_feature_class(folder, name, spatial_ref):
    path = os.path.join(folder, name)
    if not arcpy.Exists(path):
        arcpy.management.CreateFeatureclass(folder, name, "POINT", spatial_reference=spatial_ref)
        print(f"Feature class {name} created.")
    else:
        print(f"Feature class {name} already exists.")
    return path

# Create or get the map
if not any(m.name == "Dory_Map" for m in aprx.listMaps()):
    dory_map = aprx.listMaps()[0]  # Use the default map if 'createMap' is not available
    print("Using the default map.")
else:
    dory_map = aprx.listMaps("Dory_Map")[0]
    print("Map 'Dory_Map' already exists.")

# Coordinates for Dory's Farm and North Picnic Area
dory_farm_coords = (568098.33, 4886439.35)  # Easting, Northing in meters
north_picnic_coords = (576398.02, 4878390.42)

# Create feature class for Dory's Farm
dory_farm_start = create_feature_class(Dory_folder, "Dory_Farm_Start.shp", spatial_ref)

# Add point to Dory's Farm feature class
if int(arcpy.GetCount_management(dory_farm_start).getOutput(0)) == 0:
    if 'Name' not in [f.name for f in arcpy.ListFields(dory_farm_start)]:
        arcpy.management.AddField(dory_farm_start, "Name", "TEXT", field_length=50)
    with arcpy.da.InsertCursor(dory_farm_start, ['SHAPE@XY', 'Name']) as cursor:
        cursor.insertRow([dory_farm_coords, "Dory's Farm"])
    print(f"Added Dory's Farm point to {dory_farm_start}")
else:
    print(f"Dory's Farm point already exists in {dory_farm_start}")

dory_map.addDataFromPath(dory_farm_start)

# Create feature class for North Picnic Area
north_picnic_end = create_feature_class(Dory_folder, "North_Picnic_End.shp", spatial_ref)

# Add point to North Picnic feature class
if int(arcpy.GetCount_management(north_picnic_end).getOutput(0)) == 0:
    if 'Name' not in [f.name for f in arcpy.ListFields(north_picnic_end)]:
        arcpy.management.AddField(north_picnic_end, "Name", "TEXT", field_length=50)
    with arcpy.da.InsertCursor(north_picnic_end, ['SHAPE@XY', 'Name']) as cursor:
        cursor.insertRow([north_picnic_coords, "North Picnic"])
    print(f"Added North Picnic point to {north_picnic_end}")
else:
    print(f"North Picnic point already exists in {north_picnic_end}")

dory_map.addDataFromPath(north_picnic_end)

# Define the combined extent to cover both points with a buffer
buffer_distance = 5000  # in meters
XMin = min(dory_farm_coords[0], north_picnic_coords[0]) - buffer_distance
YMin = min(dory_farm_coords[1], north_picnic_coords[1]) - buffer_distance
XMax = max(dory_farm_coords[0], north_picnic_coords[0]) + buffer_distance
YMax = max(dory_farm_coords[1], north_picnic_coords[1]) + buffer_distance

# Set the environment extent
arcpy.env.extent = arcpy.Extent(XMin, YMin, XMax, YMax)

# Create an extent polygon to clip data
extent_polygon_path = os.path.join(Dory_folder, "Extent_Polygon.shp")
if not arcpy.Exists(extent_polygon_path):
    extent_array = arcpy.Array([
        arcpy.Point(XMin, YMin),
        arcpy.Point(XMin, YMax),
        arcpy.Point(XMax, YMax),
        arcpy.Point(XMax, YMin),
        arcpy.Point(XMin, YMin)  # Close the polygon
    ])
    extent_polygon = arcpy.Polygon(extent_array, spatial_ref)
    arcpy.management.CreateFeatureclass(
        out_path=Dory_folder,
        out_name="Extent_Polygon.shp",
        geometry_type="POLYGON",
        spatial_reference=spatial_ref
    )
    with arcpy.da.InsertCursor(extent_polygon_path, ["SHAPE@"]) as cursor:
        cursor.insertRow([extent_polygon])
    print(f"Extent polygon created at {extent_polygon_path}")
else:
    print(f"Extent polygon already exists at {extent_polygon_path}")

# Land Use - Avoid Farm fields
land_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/biota_landcover_nlcd_mn_2016/tif_biota_landcover_nlcd_mn_2016.zip"
land_zip_path = os.path.join(Dory_folder, "landcover.zip")
land_extract_dir = os.path.join(Dory_folder, "land_use_extracted")
download_and_extract(land_url, land_zip_path, land_extract_dir)

land_raster_path = os.path.join(land_extract_dir, "NLCD_2016_Land_Cover.tif")

# Check spatial reference
desc_original = arcpy.Describe(land_raster_path)
print(f"Spatial Reference of land_raster_path: {desc_original.spatialReference.name}")

if desc_original.spatialReference.name == "Unknown":
    arcpy.management.DefineProjection(
        land_raster_path,
        coordinate_system=spatial_ref
    )
    print("Spatial reference defined for land_raster_path.")
else:
    print("Spatial reference already defined for land_raster_path.")

# Define output path for reclassified farm fields raster
farm_fields_reclass_path = os.path.join(Dory_folder, "Farm_Reclassified.tif")

# Reclassify land cover to identify farm fields
if not arcpy.Exists(farm_fields_reclass_path):
    remap = RemapValue([
        [81, 10],  # Pasture/Hay
        [82, 10],  # Cultivated Crops
        [11, 1], [12, 1], [21, 1], [22, 1], [23, 1], [24, 1], [31, 1], [41, 1], [42, 1],
        [43, 1], [52, 1], [71, 1], [90, 1], [95, 1]
    ])
    farm_fields_reclass = Reclassify(land_raster_path, "Value", remap, "NODATA")
    farm_fields_reclass.save(farm_fields_reclass_path)
    print(f"Farm fields reclassified and saved to {farm_fields_reclass_path}")
else:
    print(f"Farm fields reclassified raster already exists at {farm_fields_reclass_path}")

dory_map.addDataFromPath(farm_fields_reclass_path)

# Hydrology - Dory doesn't like crossing water bodies if there isn't a bridge
hydro_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/water_dnr_hydrography/shp_water_dnr_hydrography.zip"
bridge_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dot/trans_bridges/shp_trans_bridges.zip"

# Paths for downloads
hydro_zip_path = os.path.join(Dory_folder, "hydrography.zip")
hydro_extract_dir = os.path.join(Dory_folder, "hydrography_extracted")
bridge_zip_path = os.path.join(Dory_folder, "bridges.zip")
bridge_extract_dir = os.path.join(Dory_folder, "bridges_extracted")

# Download and extract hydrology and bridge data
download_and_extract(hydro_url, hydro_zip_path, hydro_extract_dir)
download_and_extract(bridge_url, bridge_zip_path, bridge_extract_dir)

# List shapefiles in the extracted directories
hydro_shapefiles = [f for f in os.listdir(hydro_extract_dir) if f.endswith('.shp')]
bridge_shapefiles = [f for f in os.listdir(bridge_extract_dir) if f.endswith('.shp')]

# Verify and set the shapefile paths
if hydro_shapefiles:
    hydro_shapefile_path = os.path.join(hydro_extract_dir, hydro_shapefiles[0])
else:
    raise FileNotFoundError("No shapefile found in hydrography data.")

if bridge_shapefiles:
    bridge_shapefile_path = os.path.join(bridge_extract_dir, bridge_shapefiles[0])
else:
    raise FileNotFoundError("No shapefile found in bridge data.")

# Clip hydrology and bridge data to the target area
hydro_clipped_path = os.path.join(Dory_folder, "Hydro_Clipped.shp")
bridge_clipped_path = os.path.join(Dory_folder, "Bridges_Clipped.shp")

if not arcpy.Exists(hydro_clipped_path):
    arcpy.analysis.Clip(
        in_features=hydro_shapefile_path,
        clip_features=extent_polygon_path,
        out_feature_class=hydro_clipped_path
    )
    print(f"Hydrography data clipped and saved to {hydro_clipped_path}")
else:
    print(f"Hydrography data already clipped at {hydro_clipped_path}")

if not arcpy.Exists(bridge_clipped_path):
    arcpy.analysis.Clip(
        in_features=bridge_shapefile_path,
        clip_features=extent_polygon_path,
        out_feature_class=bridge_clipped_path
    )
    print(f"Bridge data clipped and saved to {bridge_clipped_path}")
else:
    print(f"Bridge data already clipped at {bridge_clipped_path}")

# Paths for raster outputs
water_raster_path = os.path.join(Dory_folder, "Water_Raster.tif")
water_reclass_path = os.path.join(Dory_folder, "Water_Reclassified.tif")
bridge_raster_path = os.path.join(Dory_folder, "Bridges_Raster.tif")
adjusted_water_reclass_path = os.path.join(Dory_folder, "Adjusted_Water_Reclassified.tif")

# Get cell size from an existing raster (e.g., farm_fields_reclass_path)
cell_size = arcpy.management.GetRasterProperties(farm_fields_reclass_path, "CELLSIZEX").getOutput(0)

# Add "wb_code" field to hydrology data, if it doesn't exist
wb_code_field = "wb_code"
if wb_code_field not in [f.name for f in arcpy.ListFields(hydro_clipped_path)]:
    arcpy.management.AddField(hydro_clipped_path, wb_code_field, "SHORT")
    print(f"Added field '{wb_code_field}' to hydrology data.")

# Water body class to code per metadata
wb_class_mapping = {
    'Artificial Basin': 1, 'Drained Lakebed': 2, 'Drained Wetland': 3,
    'Fish Hatchery Pond': 4, 'Industrial Waste Pond': 5, 'Inundation Area': 6,
    'Intermittent Water': 7, 'Island or Land': 8, 'Lake or Pond': 9,
    'Mine or Gravel Pit': 10, 'Natural Ore Mine': 11, 'Natural Taconite/Ore Mine': 12,
    'Partially Drained Lakebed': 13, 'Partially Drained Wetland': 14, 'Reservoir': 15,
    'Riverine island': 16, 'Riverine polygon': 17, 'Sewage/Filtration Pd': 18,
    'Tailings Pond': 19, 'Wetland': 20
}

# Update 'wb_code' field in hydrology data based on mapping
with arcpy.da.UpdateCursor(hydro_clipped_path, ['wb_class', wb_code_field]) as cursor:
    for row in cursor:
        row[1] = wb_class_mapping.get(row[0], 99)  # Use 99 for unknown types
        cursor.updateRow(row)
print("Updated 'wb_code' field in hydrology data.")

# Convert hydrology data to raster using wb_code as value
if not arcpy.Exists(water_raster_path):
    arcpy.conversion.PolygonToRaster(
        in_features=hydro_clipped_path,
        value_field=wb_code_field,
        out_rasterdataset=water_raster_path,
        cell_assignment="MAXIMUM_COMBINED_AREA",
        priority_field=None,
        cellsize=cell_size
    )
    print(f"Water raster created at {water_raster_path}")
else:
    print(f"Water raster already exists at {water_raster_path}")

# Check spatial reference of water_raster_path
desc = arcpy.Describe(water_raster_path)
print(f"Spatial Reference of water_raster_path: {desc.spatialReference.name}")

if desc.spatialReference.name == "Unknown":
    arcpy.management.DefineProjection(
        water_raster_path,
        coordinate_system=spatial_ref
    )
    print("Spatial reference defined for water_raster_path.")
else:
    print("Spatial reference already defined for water_raster_path.")

# Convert water raster to integer type if needed
data_type = arcpy.GetRasterProperties_management(water_raster_path, "VALUETYPE").getOutput(0)
print(f"Raster Value Type: {data_type}")

if data_type != '1':  # If the raster is not integer type
    water_raster_int_path = os.path.join(Dory_folder, "Water_Raster_Int.tif")
    if not arcpy.Exists(water_raster_int_path):
        arcpy.management.CopyRaster(
            in_raster=water_raster_path,
            out_rasterdataset=water_raster_int_path,
            pixel_type="8_BIT_UNSIGNED"
        )
        print(f"Converted water raster to integer at {water_raster_int_path}")
    else:
        print(f"Integer water raster already exists at {water_raster_int_path}")
    water_raster_path = water_raster_int_path  # Update the path
else:
    print("Water raster is already integer type.")

# Build raster attribute table if needed
water_raster = arcpy.Raster(water_raster_path)
if not water_raster.hasRAT:
    arcpy.management.BuildRasterAttributeTable(water_raster_path, "Overwrite")
    print("Raster attribute table built.")
else:
    print("Raster attribute table already exists.")

# Reclassify water bodies
if not arcpy.Exists(water_reclass_path):
    remap = RemapValue([
        [1, 8], [2, 2], [3, 2], [4, 10], [5, 15],
        [6, 6], [7, 5], [8, 1], [9, 12], [10, 10],
        [11, 10], [12, 10], [13, 3], [14, 3], [15, 10],
        [16, 1], [17, 8], [18, 15], [19, 12], [20, 7],
        [99, 8]
    ])
    water_reclass = Reclassify(water_raster_path, "Value", remap)
    water_reclass.save(water_reclass_path)
    print(f"Reclassified water raster saved at {water_reclass_path}")
else:
    print(f"Reclassified water raster already exists at {water_reclass_path}")

dory_map.addDataFromPath(water_reclass_path)

# Slope / Elevation - Dory wants to take the path that is the most gradual in terms of slope
slope_url = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/elev_30m_digital_elevation_model/fgdb_elev_30m_digital_elevation_model.zip"
slope_zip_path = os.path.join(Dory_folder, "elevation.zip")
slope_extract_dir = os.path.join(Dory_folder, "elevation_extracted")
download_and_extract(slope_url, slope_zip_path, slope_extract_dir)

# Set paths to DEM data
dem_gdb_path = os.path.join(slope_extract_dir, "elev_30m_digital_elevation_model.gdb")
dem_dataset_name = "digital_elevation_model_30m"
dem_path = os.path.join(dem_gdb_path, dem_dataset_name)

# Ensure the DEM dataset exists
if not arcpy.Exists(dem_path):
    print(f"DEM dataset not found at {dem_path}")
else:
    print(f"DEM dataset found at {dem_path}")

# Clip DEM to the target area using the extent polygon
dem_clipped_path = os.path.join(Dory_folder, "DEM_Clipped.tif")
if not arcpy.Exists(dem_clipped_path):
    arcpy.management.Clip(
        in_raster=dem_path,
        out_raster=dem_clipped_path,
        in_template_dataset=extent_polygon_path,
        clipping_geometry="ClippingGeometry",
        nodata_value="-9999",
        maintain_clipping_extent="NO_MAINTAIN_EXTENT"
    )
    print(f"Clipped DEM saved at {dem_clipped_path}")
else:
    print(f"Clipped DEM already exists at {dem_clipped_path}")

# Add clipped DEM to the map
dory_map.addDataFromPath(dem_clipped_path)

# Calculate slope from the clipped DEM
slope_raster_path = os.path.join(Dory_folder, "Slope.tif")
if not arcpy.Exists(slope_raster_path):
    slope_raster = Slope(
        in_raster=dem_clipped_path,
        output_measurement="DEGREE",
        z_unit="METER",
        method="PLANAR"
    )
    slope_raster.save(slope_raster_path)
    print(f"Slope raster saved at {slope_raster_path}")
else:
    print(f"Slope raster already exists at {slope_raster_path}")

# Add slope raster to the map
dory_map.addDataFromPath(slope_raster_path)

# Reclassify slope values based on degrees
slope_reclass_path = os.path.join(Dory_folder, "Slope_Reclass.tif")

# Reclassify slope based on defined values
if not arcpy.Exists(slope_reclass_path):
    slope_raster = Raster(slope_raster_path)
    reclassified_slope = Con(
        (slope_raster >= 0) & (slope_raster < 5), 1,
        Con((slope_raster >= 5) & (slope_raster < 15), 3,
            Con((slope_raster >= 15) & (slope_raster < 30), 5,
                Con((slope_raster >= 30) & (slope_raster <= 90), 10, 10))))
    reclassified_slope.save(slope_reclass_path)
    print(f"Reclassified slope raster saved at {slope_reclass_path}")
else:
    print(f"Reclassified slope raster already exists at {slope_reclass_path}")

# Add reclassified slope raster to the map
dory_map.addDataFromPath(slope_reclass_path)

# Ensure that the input rasters exist
for raster_path in [slope_reclass_path, farm_fields_reclass_path, water_reclass_path]:
    if not arcpy.Exists(raster_path):
        raise FileNotFoundError(f"Input raster not found: {raster_path}")

# Set the environment extent, cell size, and snap raster to match the input rasters
arcpy.env.extent = arcpy.Describe(slope_reclass_path).extent
arcpy.env.cellSize = arcpy.Describe(slope_reclass_path).meanCellWidth
arcpy.env.snapRaster = slope_reclass_path

# Calculate the weighted cost surface
cost_surface_weighted_path = os.path.join(Dory_folder, "Dory_Cost_Surface_Weighted.tif")
if not arcpy.Exists(cost_surface_weighted_path):
    cost_surface_weighted = (0.5 * Raster(slope_reclass_path) +
                             0.3 * Raster(farm_fields_reclass_path) +
                             0.2 * Raster(water_reclass_path))
    cost_surface_weighted.save(cost_surface_weighted_path)
    print(f"Saved cost surface raster at {cost_surface_weighted_path}")
else:
    print(f"Cost surface raster already exists at {cost_surface_weighted_path}")

# Add the cost surface to the map
dory_map.addDataFromPath(cost_surface_weighted_path)

# Recalculate statistics for cost surface raster
arcpy.management.CalculateStatistics(cost_surface_weighted_path)

# Paths for cost distance and backlink rasters
cost_distance_raster_path = os.path.join(Dory_folder, "Cost_Distance.tif")
backlink_raster_path = os.path.join(Dory_folder, "Backlink.tif")

# Compute cost distance
if not arcpy.Exists(cost_distance_raster_path):
    try:
        out_cost_distance = CostDistance(
            in_source_data=dory_farm_start,
            in_cost_raster=cost_surface_weighted_path,
            out_backlink_raster=backlink_raster_path
        )
        out_cost_distance.save(cost_distance_raster_path)
        print(f"Cost Distance saved at {cost_distance_raster_path}")
    except arcpy.ExecuteError:
        print("Error in CostDistance:")
        print(arcpy.GetMessages())
else:
    print("Cost Distance raster already exists.")

# Recalculate statistics for cost distance and backlink rasters
arcpy.management.CalculateStatistics(cost_distance_raster_path)
arcpy.management.CalculateStatistics(backlink_raster_path)

# Verify that destination point is within cost distance raster extent
destination_extent = arcpy.Describe(north_picnic_end).extent
cost_distance_extent = arcpy.Describe(cost_distance_raster_path).extent

if cost_distance_extent.contains(destination_extent):
    print("Destination point is within the cost distance raster extent.")
else:
    print("Destination point is outside the cost distance raster extent. Please adjust the extent.")

# Run CostPath
least_cost_path_raster_path = os.path.join(Dory_folder, "Least_Cost_Path.tif")
if not arcpy.Exists(least_cost_path_raster_path):
    try:
        out_least_cost_path = CostPath(
            in_destination_data=north_picnic_end,
            in_cost_distance_raster=cost_distance_raster_path,
            in_cost_backlink_raster=backlink_raster_path,
            path_type="EACH_CELL"
        )
        out_least_cost_path.save(least_cost_path_raster_path)
        print(f"Least-Cost Path saved at {least_cost_path_raster_path}")
    except arcpy.ExecuteError:
        print("Error in CostPath:")
        print(arcpy.GetMessages())
else:
    print("Least-Cost Path raster already exists.")

# Add the least-cost path to the map
if arcpy.Exists(least_cost_path_raster_path):
    try:
        dory_map.addDataFromPath(least_cost_path_raster_path)
        print("Least-Cost Path raster added to the map.")
    except Exception as e:
        print(f"Failed to add Least-Cost Path raster to the map: {e}")
else:
    print("Least-Cost Path raster does not exist. Cannot add to the map.")

# Reset environment extent and cell size to default
arcpy.env.extent = None
arcpy.env.cellSize = None
arcpy.env.snapRaster = None

print("Script completed successfully.")




