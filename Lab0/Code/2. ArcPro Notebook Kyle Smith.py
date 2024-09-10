import arcpy

arcpy.env.workspace = r'C:\Mac\Home\Downloads\shp_trans_federal_routes'

#upload dataset - Strategic Highway Network in MN

#Feature Server: https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/Strategic_Highways/FeatureServer/0
#Saved locally and accessed here:
data = r'C:\Mac\Home\Downloads\shp_trans_federal_routes\Strategic_Highway_Network_in_Minnesota.shp'

#I want to save the new buffer file here and name it "Buffer.shp":
buffer = r'C:\Mac\Home\Downloads\shp_trans_federal_routes\Buffer.shp'

#Per guidance at 'help(arcpy.analysis.Buffer)', here are the details for the buffer. 
#I want a 5 mile buffer around the highway polylines in the Strategic Highway Network in MN dataset 
arcpy.Buffer_analysis(
    
    # Input (dataset)
    in_features=data, 
    
     # Output (buffer)
    out_feature_class=buffer,   
    
    # Buffer details
    buffer_distance_or_field="5 Miles")

# Export to ArcPro 
export=r'C:\Mac\Home\Downloads\shp_trans_federal_routes\Buffer_Export.shp'

#"Buffer_Export" automatically appears as a layer in my Contents pane 


