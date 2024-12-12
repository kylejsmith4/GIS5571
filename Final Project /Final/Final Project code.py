import arcpy
import requests
import json
from arcgis.features import FeatureSet
from arcgis.geometry import SpatialReference
import os
import zipfile

# Update project folder and path
project_folder = r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final"
project_path = os.path.join(project_folder, "5571_Final.aprx")  
project = arcpy.mp.ArcGISProject(project_path)
map_obj = project.listMaps("Final_Project_Map")[0]

# LA County boundaries for project area; will be used to clip other data
la_co_boundary_api = "https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13"

# Download LA County boundary locally if it doesn't exist
la_co_boundary = r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\LA_co_boundary.shp"
if not arcpy.Exists(la_co_boundary):
    arcpy.management.CopyFeatures(la_co_boundary_api, la_co_boundary)

# Add the feature layer
layer_name = "LA_co_boundary"
map_obj = arcpy.MakeFeatureLayer_management(la_co_boundary, layer_name)

la_co_boundary

# Fire Zones
arcpy.management.MakeFeatureLayer(
    in_features="https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSZ_SRA_LRA_Combined/FeatureServer/0",
    out_layer="Fire_Zones_All_CA",
    where_clause="",
    workspace=None,
    field_info="OBJECTID OBJECTID VISIBLE NONE;SRA_Previous SRA_Previous VISIBLE NONE;SRA22_2 SRA22_2 VISIBLE NONE;FHSZ FHSZ VISIBLE NONE;FHSZ_Description FHSZ_Description VISIBLE NONE;FHSZ_7Class FHSZ_7Class VISIBLE NONE;Shape__Area Shape__Area VISIBLE NONE;Shape__Length Shape__Length VISIBLE NONE;Shape Shape VISIBLE NONE"
)

arcpy.analysis.Clip(
    in_features="https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/FHSZ_SRA_LRA_Combined/FeatureServer/0",
    clip_features="https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\clipped_fire_zones.shp",
    cluster_tolerance=None
)

arcpy.analysis.PairwiseDissolve(
    in_features=r"Fire Hazard Zones\clipped_fire_zones_all",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\clipped_fire_z_PairwiseDisso",
    dissolve_field=None,
    statistics_fields=None,
    multi_part="SINGLE_PART",
    concatenation_separator=""
)

# Fire Perimeters
arcpy.management.MakeFeatureLayer(
    in_features="https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/California_Historic_Fire_Perimeters/FeatureServer/0",
    out_layer="Historic_fire_maps_CA",
    where_clause="",
    workspace=None,
    field_info="OBJECTID OBJECTID VISIBLE NONE;YEAR_ YEAR_ VISIBLE NONE;STATE STATE VISIBLE NONE;AGENCY AGENCY VISIBLE NONE;UNIT_ID UNIT_ID VISIBLE NONE;FIRE_NAME FIRE_NAME VISIBLE NONE;INC_NUM INC_NUM VISIBLE NONE;ALARM_DATE ALARM_DATE VISIBLE NONE;CONT_DATE CONT_DATE VISIBLE NONE;CAUSE CAUSE VISIBLE NONE;C_METHOD C_METHOD VISIBLE NONE;OBJECTIVE OBJECTIVE VISIBLE NONE;GIS_ACRES GIS_ACRES VISIBLE NONE;COMMENTS COMMENTS VISIBLE NONE;COMPLEX_NAME COMPLEX_NAME VISIBLE NONE;IRWINID IRWINID VISIBLE NONE;FIRE_NUM FIRE_NUM VISIBLE NONE;COMPLEX_ID COMPLEX_ID VISIBLE NONE;DECADES DECADES VISIBLE NONE;Shape__Area Shape__Area VISIBLE NONE;Shape__Length Shape__Length VISIBLE NONE;Shape Shape VISIBLE NONE"
)

# Only need data from 1980 onwards
arcpy.analysis.PairwiseClip(
    in_features="CaliforniaFirePerimeters1980",
    clip_features=r"Study Area\LA_co_boundary",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\LACFirePerimeters1980",
    cluster_tolerance=None
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="California Fire Perimeters (1950+)",
    selection_type="NEW_SELECTION",
    where_clause="YEAR_ >= 1980",
    invert_where_clause=None
)

arcpy.conversion.ExportFeatures(
    in_features="California Fire Perimeters (1950+)",
    out_features=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\CaliforniaFirePerimeters1980",
    where_clause="",
    use_field_alias_as_name="NOT_USE_ALIAS",
    field_mapping='YEAR_ "Year" true true false 0 Short 0 0,First,#,California Fire Perimeters (1950+),YEAR_,-1,-1;STATE "State" true true false 2 Text 0 0,First,#,California Fire Perimeters (1950+),STATE,0,1;AGENCY "Agency" true true false 3 Text 0 0,First,#,California Fire Perimeters (1950+),AGENCY,0,2;UNIT_ID "Unit ID" true true false 3 Text 0 0,First,#,California Fire Perimeters (1950+),UNIT_ID,0,2;FIRE_NAME "Fire Name" true true false 34 Text 0 0,First,#,California Fire Perimeters (1950+),FIRE_NAME,0,33;INC_NUM "Local Incident Number" true true false 8 Text 0 0,First,#,California Fire Perimeters (1950+),INC_NUM,0,7;ALARM_DATE "Alarm Date" true true false 8 Date 0 1,First,#,California Fire Perimeters (1950+),ALARM_DATE,-1,-1;CONT_DATE "Containment Date" true true false 8 Date 0 1,First,#,California Fire Perimeters (1950+),CONT_DATE,-1,-1;CAUSE "Cause" true true false 0 Short 0 0,First,#,California Fire Perimeters (1950+),CAUSE,-1,-1;C_METHOD "Collection Method" true true false 0 Short 0 0,First,#,California Fire Perimeters (1950+),C_METHOD,-1,-1;OBJECTIVE "Management Objective" true true false 0 Short 0 0,First,#,California Fire Perimeters (1950+),OBJECTIVE,-1,-1;GIS_ACRES "GIS Calculated Acres" true true false 0 Float 0 0,First,#,California Fire Perimeters (1950+),GIS_ACRES,-1,-1;COMMENTS "Comments" true true false 100 Text 0 0,First,#,California Fire Perimeters (1950+),COMMENTS,0,99;COMPLEX_NAME "Complex Name" true true false 50 Text 0 0,First,#,California Fire Perimeters (1950+),COMPLEX_NAME,0,49;IRWINID "IRWIN ID" true true false 40 Text 0 0,First,#,California Fire Perimeters (1950+),IRWINID,0,39;FIRE_NUM "Fire Number (historical use)" true true false 8 Text 0 0,First,#,California Fire Perimeters (1950+),FIRE_NUM,0,7;COMPLEX_ID "Complex ID" true true false 40 Text 0 0,First,#,California Fire Perimeters (1950+),COMPLEX_ID,0,39;DECADES "DECADES" true true false 0 Long 0 0,First,#,California Fire Perimeters (1950+),DECADES,-1,-1;Shape__Area "Shape__Area" false true true 0 Double 0 0,First,#,California Fire Perimeters (1950+),Shape__Area,-1,-1;Shape__Length "Shape__Length" false true true 0 Double 0 0,First,#,California Fire Perimeters (1950+),Shape__Length,-1,-1',
    sort_field=None
)

arcpy.management.SelectLayerByLocation(
    in_layer="CaliforniaFirePerimeters1980",
    overlap_type="INTERSECT",
    select_features=r"Study Area\LA_co_boundary",
    search_distance=None,
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT"
)

# 2019 Land Use
Land_Use_2019 = "https://services5.arcgis.com/vYSHcRQuTn4O8o35/arcgis/rest/services/2019_Regional_Land_Use_Information_for_Los_Angeles_County/FeatureServer/0"

# Use MakeFeatureLayer for the layer name "Land_Use_2019_res"
layer_name = "Land_Use_2019_res"
arcpy.MakeFeatureLayer_management(Land_Use_2019, layer_name)

# Add the clipped shapefile to the map
map_obj.addDataFromPath(Land_Use_2019)

Land_Use_2019

# Manually set symbology for 'Land_Use_2019' based on 'LU19' field.
# Only values 1110–1150 are needed. Remove all others and group 1110–1150 
# as a single symbol colored light red.

# Clip to fire zone - data in valleys and metro area not needed
arcpy.analysis.PairwiseClip(
    in_features=r"Land Use Residential\Land_Use_2019_res",
    clip_features=r"Fire Hazard Zones\clipped_fire_z_PairwiseDisso",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Land_Use_2019_r_PairwiseClip",
    cluster_tolerance=None
)

# Pairwise dissolve
arcpy.analysis.PairwiseDissolve(
    in_features="Land_Use_2019_res",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Land_Use_2019__PairwiseDisso",
    dissolve_field=None,
    statistics_fields=None,
    multi_part="MULTI_PART",
    concatenation_separator=""
)

# Intersect 2019 Land Use with Fire_Zones_All polygons 
arcpy.analysis.Intersect(
    in_features=r"Land_Use_2019__PairwiseDisso #;'Fire Hazard Zones\clipped_fire_z_PairwiseDisso' #",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Land_Use_2019__Pai_Intersect",
    join_attributes="ALL",
    cluster_tolerance=None,
    output_type="INPUT"
)

# Wildland Urban Interface
arcpy.management.MakeFeatureLayer(
    in_features="https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_WUI_2020_01/MapServer/0",
    out_layer="WUI_all",
    where_clause="",
    workspace=None,
    field_info="OBJECTID OBJECTID VISIBLE NONE;SRA_Previous SRA_Previous VISIBLE NONE;SRA22_2 SRA22_2 VISIBLE NONE;FHSZ FHSZ VISIBLE NONE;FHSZ_Description FHSZ_Description VISIBLE NONE;FHSZ_7Class FHSZ_7Class VISIBLE NONE;Shape__Area Shape__Area VISIBLE NONE;Shape__Length Shape__Length VISIBLE NONE;Shape Shape VISIBLE NONE"
)

arcpy.analysis.Clip(
    in_features="https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_WUI_2020_01/MapServer/0",
    clip_features="https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\clipped_UWI.shp",
    cluster_tolerance=None
)

# Vegetation
arcpy.management.MakeFeatureLayer(
    in_features="https://services1.arcgis.com/X1hcdGx5Fxqn4d0j/arcgis/rest/services/Vegetation/FeatureServer/4",
    out_layer="Vegetation_all",
    where_clause="",
    workspace=None,
    field_info="OBJECTID OBJECTID VISIBLE NONE;SRA_Previous SRA_Previous VISIBLE NONE;SRA22_2 SRA22_2 VISIBLE NONE;FHSZ FHSZ VISIBLE NONE;FHSZ_Description FHSZ_Description VISIBLE NONE;FHSZ_7Class FHSZ_7Class VISIBLE NONE;Shape__Area Shape__Area VISIBLE NONE;Shape__Length Shape__Length VISIBLE NONE;Shape Shape VISIBLE NONE"
)

arcpy.analysis.Clip(
    in_features="https://services1.arcgis.com/X1hcdGx5Fxqn4d0j/arcgis/rest/services/Vegetation/FeatureServer/4",
    clip_features="https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13",
    out_feature_class="Vegetation_LAC_clip",
    cluster_tolerance=None
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Vegetation_LAC_clip",
    selection_type="NEW_SELECTION",
    where_clause="WHR13NAME = 'Shrub'",
    invert_where_clause=None
)

arcpy.management.CalculateField(
    in_table="Vegetation_LAC_clip",
    field="Risk_Score",
    expression="5",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

arcpy.management.CalculateField(
    in_table="Vegetation_LAC_clip",
    field="Risk_Score",
    expression="4",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Vegetation_LAC_clip",
    selection_type="NEW_SELECTION",
    where_clause="WHR13NAME = 'Herbaceous'",
    invert_where_clause=None
)

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb"):
    out_raster = arcpy.sa.Reclassify(
        in_raster="Vegetation_LAC_clip",
        reclass_field="Risk_Score",
        remap="1 1;2 2;3 3;4 4;5 5",
        missing_values="DATA"
    )
    out_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Reclass_Vegetation")

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Vegetation_LAC_clip",
    selection_type="NEW_SELECTION",
    where_clause="WHR13NAME IN ('Desert Woodland', 'Conifer Woodland', 'Hardwood Woodland')",
    invert_where_clause=None
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Vegetation_LAC_clip",
    selection_type="NEW_SELECTION",
    where_clause="WHR13NAME IN ('Conifer Forest')",
    invert_where_clause=None
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Vegetation_LAC_clip",
    selection_type="NEW_SELECTION",
    where_clause="WHR13NAME IN ('Wetland', 'Water', 'Agriculture')",
    invert_where_clause=None
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Vegetation_LAC_clip",
    selection_type="NEW_SELECTION",
    where_clause="WHR13NAME IN ('Conifer Woodland', 'Desert Woodland', 'Hardwood Woodland')",
    invert_where_clause=None
)

arcpy.management.CalculateField(
    in_table="Vegetation_LAC_clip",
    field="Risk_Score",
    expression="4",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

arcpy.management.CalculateField(
    in_table="Vegetation_LAC_clip",
    field="Risk_Score",
    expression="3",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

arcpy.management.CalculateField(
    in_table="Vegetation_LAC_clip",
    field="Risk_Score",
    expression="2",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

arcpy.management.CalculateField(
    in_table="Vegetation_LAC_clip",
    field="Risk_Score",
    expression="1",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

# Red Flag Warning
arcpy.management.MakeFeatureLayer(
    in_features="https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/RFW_Days_2004_2019/FeatureServer/0",
    out_layer="RFW_all",
    where_clause="",
    workspace=None,
    field_info="OBJECTID OBJECTID VISIBLE NONE;SRA_Previous SRA_Previous VISIBLE NONE;SRA22_2 SRA22_2 VISIBLE NONE;FHSZ FHSZ VISIBLE NONE;FHSZ_Description FHSZ_Description VISIBLE NONE;FHSZ_7Class FHSZ_7Class VISIBLE NONE;Shape__Area Shape__Area VISIBLE NONE;Shape__Length Shape__Length VISIBLE NONE;Shape Shape VISIBLE NONE"
)

arcpy.analysis.Clip(
    in_features="https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/RFW_Days_2004_2019/FeatureServer/0",
    clip_features="https://dpw.gis.lacounty.gov/dpw/rest/services/PW_Open_Data/MapServer/13",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_final_pjt\clipped_RFW.shp",
    cluster_tolerance=None
)

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb"):
    out_raster = arcpy.sa.Reclassify(
        in_raster="LAC_RFW_raster",
        reclass_field="Value",
        remap="0 18 1;18 49 2;49 77 3;77 92 4;92 124 5",
        missing_values="DATA"
    )
    out_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Reclass_RFW")

arcpy.conversion.FeatureToRaster(
    in_features="RFW_2004_2019_LAC_Clip",
    field="Total",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\LAC_RFW_raster",
    cell_size=30
)

arcpy.analysis.Clip(
    in_features="Verified_RFW_2004_2019",
    clip_features=r"Study Area\LA_co_boundary",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Verified_RFW_2004_2019_Clip",
    cluster_tolerance=None
)

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Verified_RFW_2004_2019",
    selection_type="NEW_SELECTION",
    where_clause="County <> 'Los Angeles'",
    invert_where_clause=None
)

# Slope
arcpy.management.MakeFeatureLayer(
    in_features="viz.USGS30m_slope.tif",
    out_layer="DEM_LACounty",
    where_clause="",
    workspace=None,
    field_info="OBJECTID OBJECTID VISIBLE NONE;SRA_Previous SRA_Previous VISIBLE NONE;SRA22_2 SRA22_2 VISIBLE NONE;FHSZ FHSZ VISIBLE NONE;FHSZ_Description FHSZ_Description VISIBLE NONE;FHSZ_7Class FHSZ_7Class VISIBLE NONE;Shape__Area Shape__Area VISIBLE NONE;Shape__Length Shape__Length VISIBLE NONE;Shape Shape VISIBLE NONE"
)

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb"):
    out_raster = arcpy.sa.Slope(
        in_raster="output_USGS30m.tif",
        output_measurement="DEGREE",
        z_factor=1,
        method="PLANAR",
        z_unit="METER",
        analysis_target_device="GPU_THEN_CPU"
    )
    out_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Slope_output1")

arcpy.management.Resample(
    in_raster="Reclass_Slope_ok",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Reclass_Slope_ok_Resample",
    cell_size="30 30",
    resampling_type="NEAREST"
)

with arcpy.EnvManager(scratchWorkspace=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb"):
    out_raster = arcpy.sa.Reclassify(
        in_raster="Surface_10n11",
        reclass_field="VALUE",
        remap="0 3 1;3 8 2;8 14 3;14 22 4;22 77.473396 5",
        missing_values="DATA"
    )
    out_raster.save(r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Reclass_Slope")

    arcpy.management.Clip(
        in_raster="Slope_30n1201",
        rectangle="6060556.35951749 1347588.29433819 6883412.20177957 2160253.97137102",
        out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Slope_30n1201",
        in_template_dataset=r"Study Area\LA_co_boundary",
        nodata_value="3.4e+38",
        clipping_geometry="NONE",
        maintain_clipping_extent="NO_MAINTAIN_EXTENT"
    )

arcpy.management.ProjectRaster(
    in_raster="Slope_Vaild",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Slope_Projected",
    out_coor_system='PROJCS["NAD_1983_California_Teale_Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",-4000000.0],PARAMETER["Central_Meridian",-120.0],PARAMETER["Standard_Parallel_1",34.0],PARAMETER["Standard_Parallel_2",40.5],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
    resampling_type="NEAREST",
    cell_size="30 30",
    geographic_transform=None,
    Registration_Point=None,
    in_coor_system='GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
    vertical="NO_VERTICAL"
)

# MCDA
arcpy.analysis.Statistics(
    in_table="c3class_LU2019_PairwiseInter_SummarizeWithin",
    out_table=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\c3class_LU2019_Pa_Statistics",
    statistics_fields="FHSZ MEAN;FHSZ MEDIAN;FHSZ STD;Risk_Normalized_13 MEAN;Risk_Normalized_13 MEDIAN;Risk_Normalized_13 STD",
    case_field=None,
    concatenation_separator=""
)

arcpy.management.CalculateField(
    in_table="c3class_LU2019_PairwiseInter_SummarizeWithin",
    field="Risk_Normalized_13",
    expression="!MEAN_Raster_3class_MIN_MAX! * 3  /  5",
    expression_type="PYTHON3",
    code_block="",
    field_type="TEXT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

arcpy.gapro.SummarizeWithin(
    summarized_layer=r"Final\c3class_LU2019_PairwiseInter",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\c3class_LU2019_PairwiseInter_SummarizeWithin",
    polygon_or_bin="POLYGON",
    bin_type="",
    bin_size=None,
    summary_polygons="clipped_fire_zones",
    sum_shape="ADD_SUMMARY",
    shape_units="",
    standard_summary_fields="Raster_3class_MIN_MAX MEAN Count",
    weighted_summary_fields=None,
    group_by_field=None,
    add_minority_majority="NO_MIN_MAJ",
    add_percentages=None,
    group_by_summary=None
)

arcpy.analysis.SummarizeWithin(
    in_polygons="clipped_fire_zones",
    in_sum_features=r"Final\3class_polygons",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\RiskScores_FireZones_Summary",
    keep_all_polygons="KEEP_ALL",
    sum_fields=None,
    sum_shape="ADD_SHAPE_SUM",
    shape_unit="SQUAREKILOMETERS",
    group_field=None,
    add_min_maj="NO_MIN_MAJ",
    add_group_percent="NO_PERCENT",
    out_group_table=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Risk_Score_Summary"
)

arcpy.analysis.SummarizeWithin(
    in_polygons="clipped_fire_zones",
    in_sum_features=r"Final\c3class_LU2019_PairwiseInter",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\RiskScores_FireZones_Summary",
    keep_all_polygons="KEEP_ALL",
    sum_fields="Raster_3class_MIN_MAX Max",
    sum_shape="ADD_SHAPE_SUM",
    shape_unit="SQUAREKILOMETERS",
    group_field=None,
    add_min_maj="NO_MIN_MAJ",
    add_group_percent="NO_PERCENT",
    out_group_table=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Risk_Score_Summary"
)

arcpy.analysis.SpatialJoin(
    target_features="clipped_fire_zones",
    join_features=r"Final\c3class_LU2019_PairwiseInter",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Join_3class_points_FireZones",
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    field_mapping=r'FID_RasterT_RasterC1 "FID_RasterT_RasterC1" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FID_RasterT_RasterC1,-1,-1;Id "Id" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,Id,-1,-1;gridcode "gridcode" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,gridcode,-1,-1;FID_LU_2019_LA_res_FeatureToPoin "FID_LU_2019_LA_res_FeatureToPoin" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FID_LU_2019_LA_res_FeatureToPoin,-1,-1;PID19 "PID19" true true false 13 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,PID19,0,12;APN19 "APN19" true true false 10 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,APN19,0,9;COUNTY "COUNTY" true true false 14 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,COUNTY,0,13;COUNTY_ID "COUNTY_ID" true true false 3 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,COUNTY_ID,0,2;CITY "CITY" true true false 22 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,CITY,0,21;CITY_ID "CITY_ID" true true false 5 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,CITY_ID,0,4;MULTIPART "MULTIPART" true true false 2 Short 0 0,First,#,Final\c3class_LU2019_PairwiseInter,MULTIPART,-1,-1;STACK "STACK" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,STACK,-1,-1;ACRES "ACRES" true true false 8 Double 0 0,First,#,Final\c3class_LU2019_PairwiseInter,ACRES,-1,-1;SLOPE "SLOPE" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,SLOPE,-1,-1;GEOID20 "GEOID20" true true false 15 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,GEOID20,0,14;GP19_CITY "GP19_CITY" true true false 57 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,GP19_CITY,0,56;GP19_SCAG "GP19_SCAG" true true false 4 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,GP19_SCAG,0,3;DEN_AVG "DEN_AVG" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,DEN_AVG,-1,-1;DEN_MIN "DEN_MIN" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,DEN_MIN,-1,-1;DEN_MAX "DEN_MAX" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,DEN_MAX,-1,-1;FAR_AVG "FAR_AVG" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FAR_AVG,-1,-1;FAR_MIN "FAR_MIN" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FAR_MIN,-1,-1;FAR_MAX "FAR_MAX" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FAR_MAX,-1,-1;YEAR_GP "YEAR_GP" true true false 8 Date 0 1,First,#,Final\c3class_LU2019_PairwiseInter,YEAR_GP,-1,-1;SP_INDEX "SP_INDEX" true true false 2 Short 0 0,First,#,Final\c3class_LU2019_PairwiseInter,SP_INDEX,-1,-1;SP_NAME "SP_NAME" true true false 100 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,SP_NAME,0,99;SP19_CITY "SP19_CITY" true true false 58 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,SP19_CITY,0,57;SP19_SCAG "SP19_SCAG" true true false 4 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,SP19_SCAG,0,3;DEN_AVG_SP "DEN_AVG_SP" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,DEN_AVG_SP,-1,-1;DEN_MIN_SP "DEN_MIN_SP" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,DEN_MIN_SP,-1,-1;DEN_MAX_SP "DEN_MAX_SP" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,DEN_MAX_SP,-1,-1;FAR_AVG_SP "FAR_AVG_SP" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FAR_AVG_SP,-1,-1;FAR_MIN_SP "FAR_MIN_SP" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FAR_MIN_SP,-1,-1;FAR_MAX_SP "FAR_MAX_SP" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,FAR_MAX_SP,-1,-1;YEAR_SP "YEAR_SP" true true false 8 Date 0 1,First,#,Final\c3class_LU2019_PairwiseInter,YEAR_SP,-1,-1;ZN19_CITY "ZN19_CITY" true true false 49 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,ZN19_CITY,0,48;ZN19_SCAG "ZN19_SCAG" true true false 4 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,ZN19_SCAG,0,3;LU19 "LU19" true true false 4 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,LU19,0,3;YEAR "YEAR" true true false 2 Short 0 0,First,#,Final\c3class_LU2019_PairwiseInter,YEAR,-1,-1;LU_19_Description "LU_19_Description" true true false 255 Text 0 0,First,#,Final\c3class_LU2019_PairwiseInter,LU_19_Description,0,254;Field "Field" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,Field,-1,-1;Size "Size" true true false 8 Double 0 0,First,#,Final\c3class_LU2019_PairwiseInter,Size,-1,-1;ORIG_FID "ORIG_FID" true true false 4 Long 0 0,First,#,Final\c3class_LU2019_PairwiseInter,ORIG_FID,-1,-1;Raster_3class "Raster_3class" true true false 4 Float 0 0,First,#,Final\c3class_LU2019_PairwiseInter,Raster_3class,-1,-1;Risk_Score "Risk_Score" true true false 8 Double 0 0,First,#,Final\c3class_LU2019_PairwiseInter,Risk_Score,-1,-1;Raster_3class_MIN_MAX "Raster_3class_MIN_MAX" true true false 8 Double 0 0,First,#,Final\c3class_LU2019_PairwiseInter,Raster_3class_MIN_MAX,-1,-1;SRA_Previo "SRA_Previo" true true false 254 Text 0 0,First,#,clipped_fire_zones,SRA_Previo,0,253;SRA22_2 "SRA22_2" true true false 254 Text 0 0,First,#,clipped_fire_zones,SRA22_2,0,253;FHSZ "FHSZ" true true false 5 Long 0 5,First,#,clipped_fire_zones,FHSZ,-1,-1;FHSZ_Descr "FHSZ_Descr" true true false 254 Text 0 0,First,#,clipped_fire_zones,FHSZ_Descr,0,253;FHSZ_7Clas "FHSZ_7Clas" true true false 254 Text 0 0,First,#,clipped_fire_zones,FHSZ_7Clas,0,253;Shape__Are "Shape__Are" true true false 19 Double 0 0,First,#,clipped_fire_zones,Shape__Are,-1,-1;Shape__Len "Shape__Len" true true false 19 Double 0 0,First,#,clipped_fire_zones,Shape__Len,-1,-1;RiskScore "RiskScore" true true false 19 Double 0 0,First,#,clipped_fire_zones,RiskScore,-1,-1',
    match_option="INTERSECT",
    search_radius=None,
    distance_field_name="",
    match_fields=None
)

# Sensitivity Analysis and Verification
arcpy.analysis.SpatialJoin(
    target_features=r"Final\c3class_LU2019_PairwiseInter",
    join_features="clipped_fire_zones",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Join_3class_points_FireZones",
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    field_mapping=r'...[field mapping truncated for brevity]...',
    match_option="INTERSECT",
    search_radius=None,
    distance_field_name="",
    match_fields=None
)

arcpy.management.Clip(
    in_raster="Scenario1",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Scenario1Project_Clip1",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="ClippingGeometry",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="Scenario2",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Scenario2Project_Clip1",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="ClippingGeometry",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="Scenario3",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Scenario3Project_Clip1",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="ClippingGeometry",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="ScenarioProject",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\ScenarioProject_Clip1",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="ClippingGeometry",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="Scenario1",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Scenario1Project_Clip",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="Scenario2",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Scenario2Project_Clip",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="Scenario3",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Scenario3Project_Clip",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Clip(
    in_raster="ScenarioProject",
    rectangle="97436.9400597716 -577997.101474175 216620.594849032 -352271.135548009",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\ScenarioProject_Clip",
    in_template_dataset="LA_co_boundary",
    nodata_value="3.4e+38",
    clipping_geometry="NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.analysis.PairwiseDissolve(
    in_features="3class_polygons",
    out_feature_class=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\LU_2019_LA_res_PairwiseDisso",
    dissolve_field=None,
    statistics_fields=None,
    multi_part="MULTI_PART",
    concatenation_separator=""
)

arcpy.sa.ExtractValuesToPoints(
    in_point_features="LU_2019_LA_res_FeatureToPoin",
    in_raster="RasterC_2",
    out_point_features=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Extract_LU_20191",
    interpolate_values="NONE",
    add_attributes="ALL"
)

arcpy.management.Clip(
    in_raster="Raster_3class",
    rectangle="97743.9877892527 -475468.809831029 215901.383855222 -356020.730800204",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Residential_Risk_Points_clip",
    in_template_dataset=r"Study Area\Study_Area_Polygons",
    nodata_value="3.4e+38",
    clipping_geometry="NONE",
    maintain_clipping_extent="NO_MAINTAIN_EXTENT"
)

arcpy.management.Resample(
    in_raster="Slope_output1",
    out_raster=r"C:\Mac\Home\Documents\ArcGIS\Projects\5571_Final\5571_Final.gdb\Slope_Projected_2",
    cell_size="30 30",
    resampling_type="BILINEAR"
)
