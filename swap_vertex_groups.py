import bpy

bl_info = {
    "name": "Swap Vertex Groups",
    "description": "Swaps vertices between user-selected vertex groups.",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "category": "Rigging",
    "location": "Properties > Object Data > Swap Vertex Groups",
    "doc_url": "https://github.com/soir20/blender-swap-vertex-groups/",
    "tracker_url": "https://github.com/soir20/blender-swap-vertex-groups/issues/",
    "support": "COMMUNITY",
}


def get_object_pose(obj):
    if obj is None:
        return None

    pose = obj.pose
    parent = obj.parent

    while pose is None and parent is not None:
        pose = parent.pose
        parent = parent.parent

    return pose


class SwapVertexGroupsOperator(bpy.types.Operator):
    """Swaps the active object's vertices between the selected vertex groups"""
    bl_idname = "swap_vert_group.swap"
    bl_label = "Swap Vertex Groups"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        pose = get_object_pose(context.object)
        return pose is not None and len(pose.bones) > 0 and context.object.type == "MESH"

    def execute(self, context):
        obj = context.object
        original_mode = obj.mode
        pose = get_object_pose(obj)
        bones = [] if pose is None else pose.bones

        bpy.ops.object.mode_set(mode="OBJECT")

        group1_name = bones[obj.selected_vertex_group1].name
        group2_name = bones[obj.selected_vertex_group2].name

        if group1_name == group2_name:
            self.report({"INFO"}, f"Cannot swap group {group1_name} with itself")
            return {"CANCELLED"}

        # Create group 1 and group 2 if needed.
        if group1_name not in obj.vertex_groups:
            obj.vertex_groups.new(name=group1_name)

        if group2_name not in obj.vertex_groups:
            obj.vertex_groups.new(name=group2_name)

        group1 = obj.vertex_groups[group1_name]
        group2 = obj.vertex_groups[group2_name]

        # Swap weights.
        num_vertices_changed = 0
        num_vertices_by_group = {}
        for vertex in obj.data.vertices:
            weights = {}

            # Get the weights to assign for group1 and group2.
            for group_elm in vertex.groups:
                weight = group_elm.weight

                group_name = obj.vertex_groups[group_elm.group].name
                num_vertices_by_group[group_name] = num_vertices_by_group.get(group_name, 0) + 1

                if not obj.swap_selected_only or vertex.select:
                    if group_name == group1_name:
                        group1.remove([vertex.index])
                        num_vertices_by_group[group1_name] = num_vertices_by_group.get(group_name, 0) - 1
                        weights[group2] = weight
                    elif group_name == group2_name:
                        group2.remove([vertex.index])
                        num_vertices_by_group[group2_name] = num_vertices_by_group.get(group_name, 0) - 1
                        weights[group1] = weight

            # Assign the new weights.
            for (group, weight) in weights.items():
                group.add([vertex.index], weight, "ADD")
                num_vertices_by_group[group.name] = num_vertices_by_group.get(group.name, 0) + 1

            if len(weights) > 0:
                num_vertices_changed += 1

        # Remove empty group1.
        if num_vertices_by_group.get(group1_name, 0) == 0:
            obj.vertex_groups.remove(group1)

        # Remove empty group2.
        if num_vertices_by_group.get(group2_name, 0) == 0:
            obj.vertex_groups.remove(group2)

        bpy.ops.object.mode_set(mode=original_mode)

        self.report({"INFO"}, f"Swapped vertex groups for {num_vertices_changed} vertices")

        return {"FINISHED"}


class VERTEX_GROUPS_UL_selector(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use "getattr(active_data, active_propname)").
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don"t
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # draw_item must handle the three layout types... Usually "DEFAULT" and "COMPACT" can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The latter also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
        # "GRID" layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class SwapVertexGroupsPanel(bpy.types.Panel):
    """Panel to select vertex groups that will be swapped"""
    bl_label = "Swap Vertex Groups"
    bl_idname = "DATA_PT_swap_vertex_groups"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        obj = context.object
        pose = get_object_pose(obj)

        self.draw_list(obj, pose, "Group 1", "first", "selected_vertex_group1")
        self.draw_list(obj, pose, "Group 2", "second", "selected_vertex_group2")

        row = self.layout.row()
        row.prop(obj, "swap_selected_only")
        row = self.layout.row()
        row.operator(SwapVertexGroupsOperator.bl_idname)

    def draw_list(self, obj, pose, group_name, list_id, active_index_property):
        layout = self.layout

        split_factor = 0.3
        split = layout.split(factor=split_factor)
        col = split.column()
        col.alignment = "RIGHT"
        col.label(text=group_name)
        col = split.column()
        col.template_list("VERTEX_GROUPS_UL_selector", list_id, pose, "bones", obj,
                          active_index_property)


def register():
    bpy.types.Object.selected_vertex_group1 = bpy.props.IntProperty(name="First selected vertex group")
    bpy.types.Object.selected_vertex_group2 = bpy.props.IntProperty(name="Second selected vertex group")

    # This is not an operator property because the redo panel does not display from the object data panel.
    bpy.types.Object.swap_selected_only = bpy.props.BoolProperty(name="Swap selected vertices only")

    bpy.utils.register_class(SwapVertexGroupsOperator)
    bpy.utils.register_class(VERTEX_GROUPS_UL_selector)
    bpy.utils.register_class(SwapVertexGroupsPanel)


def unregister():
    del bpy.types.Object.selected_vertex_group1
    del bpy.types.Object.selected_vertex_group2
    del bpy.types.Object.swap_selected_only
    bpy.utils.unregister_class(SwapVertexGroupsOperator)
    bpy.utils.unregister_class(VERTEX_GROUPS_UL_selector)
    bpy.utils.unregister_class(SwapVertexGroupsPanel)


if __name__ == "__main__":
    register()
