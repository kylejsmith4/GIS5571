#!/usr/bin/env python
# coding: utf-8

# ## Lab0 - Jupyter Notebooks in ArcOnline
# 
# 

# ### Load packages and dataset

# In[9]:


# Connect to ArcGIS Online
from arcgis.gis import GIS
gis = GIS("home")
from arcgis.features import FeatureLayer
from arcgis.features.analysis import create_buffers


# In[10]:


# Load Strategic_Highways_MN Feature Layer
Strategic_Highways_MN = FeatureLayer("https://services.arcgis.com/8df8p0NlLFEShl0r/arcgis/rest/services/Strategic_Highways/FeatureServer/0")


# ### Make Map & add Strategic_Highways_MN

# In[11]:


# Map centered on Minnesota
map1 = gis.map('Minnesota')
map1.zoom = 6
map1.height = '500px'
map1.width = '50%'

#Test the map
#map1


# In[12]:


# Add the Strategic_Highways_MN layer to the map
map1.add_layer(Strategic_Highways_MN)

#Test the map
#map1


# ### Make buffer & add to map

# In[13]:


# 5-mile buffer around the Strategic_Highways_MN polyline
input_layer = Strategic_Highways_MN

buffer_result = create_buffers(
    input_layer=input_layer,
    distances=[5],
    units="Miles",
    dissolve_type="Dissolve"
)


# In[14]:


# add the buffer to the map
map1.add_layer(buffer_result)


# ### Diaplay & save map

# In[15]:


# Display the map
map1


# In[8]:


# Save the map to ArcOnline
webmap_item = map1.save({
    'title': 'Buffer Map of Strategic Highways MN',
    'tags': 'buffers, strategic highways, Minnesota',
    'snippet': 'A 5-mile buffer around the Strategic Highways in Minnesota',
    'description': 'This map shows a 5-mile buffer around strategic highways in Minnesota.',
    'folder': None
})

# Print the web map URL
print(f"Map saved. You can view it here: {webmap_item.homepage}")


# ### Return to ArcOnline to view and analyze

# In[ ]:




