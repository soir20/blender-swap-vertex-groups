# Blender Swap Vertex Groups Plugin
Blender plugin to swap vertices between user-selected vertex groups.

![UI example](example.jpg "UI Panel in Blender")

## Installation
1. Download and unzip this repository.
2. Edit > Preferences > Addons > Install
3. Choose `swap_vertex_groups.py` from the unzipped folder.
4. Click the checkbox next to the addon name to enable it.

## Usage
The swapping panel is listed in the object data tab in the properties window. Select one vertex group/bone from each list and press "Swap Vertex Groups" to swap their vertices.

Vertex swapping is not available for objects without a pose and non-mesh objects.