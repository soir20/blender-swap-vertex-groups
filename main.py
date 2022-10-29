import bpy

bl_info = {
    "name": "Swap Vertex Groups",
    "blender": (2, 80, 0),
    "category": "Rigging",
}


class SwapVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "swap_vert_group.swap"
    bl_label = "Swap Vertex Groups"

    def execute(self, context):
        obj = context.object

        group1 = context.object.selected_vertex_group1
        group2 = context.object.selected_vertex_group2
        if group1 == group2:
            self.report({"INFO"}, "Cannot swap group with itself")
            self.report({"DEBUG"}, "Cancelling swap because group 1 and group 2 are both %d" % group1)
            return {"CANCELLED"}

        for vertex in obj.data.vertices:
            for group_elm in vertex.groups:
                weight = group_elm.weight

                if group_elm.group == group1:
                    obj.vertex_groups[group1].add([vertex.index], weight, "SUBTRACT")
                    obj.vertex_groups[group2].add([vertex.index], weight, "ADD")
                elif group_elm.group == group2:
                    obj.vertex_groups[group1].add([vertex.index], weight, "ADD")
                    obj.vertex_groups[group2].add([vertex.index], weight, "SUBTRACT")

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


# And now we can use this list everywhere in Blender. Here is a small example panel.
class SwapVertexGroupsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Swap Vertex Groups"
    bl_idname = "DATA_PT_swap_vertex_groups"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    selected_index1 = 0
    selected_index2 = 0

    def draw(self, context):
        layout = self.layout

        obj = context.object
        layout.template_list("VERTEX_GROUPS_UL_selector", "first", obj, "vertex_groups", obj,
                             "selected_vertex_group1")
        layout.template_list("VERTEX_GROUPS_UL_selector", "second", obj, "vertex_groups", obj,
                             "selected_vertex_group2")

        row = layout.row()
        row.operator("swap_vert_group.swap")


def register():
    bpy.utils.register_class(SwapVertexGroupsOperator)
    bpy.utils.register_class(VERTEX_GROUPS_UL_selector)
    bpy.utils.register_class(SwapVertexGroupsPanel)


def unregister():
    bpy.utils.unregister_class(SwapVertexGroupsOperator)
    bpy.utils.unregister_class(VERTEX_GROUPS_UL_selector)
    bpy.utils.unregister_class(SwapVertexGroupsPanel)


if __name__ == "__main__":
    bpy.types.Object.selected_vertex_group1 = bpy.props.IntProperty()
    bpy.types.Object.selected_vertex_group2 = bpy.props.IntProperty()
    register()
