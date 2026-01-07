bl_info = {
    "name": "CAD Precision Transform",
    "author": "OpenAI",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > CAD Precision",
    "description": "Deterministic numeric transforms with optional pivot overrides",
    "category": "3D View",
}

import bpy
import bmesh
from mathutils import Matrix, Vector


class CADPrecisionProperties(bpy.types.PropertyGroup):
    move_vector: bpy.props.FloatVectorProperty(
        name="Move",
        size=3,
        unit="LENGTH",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0),
        description="Translation distance",
    )
    rotate_vector: bpy.props.FloatVectorProperty(
        name="Rotate",
        size=3,
        unit="ROTATION",
        subtype="EULER",
        default=(0.0, 0.0, 0.0),
        description="Rotation in radians",
    )
    scale_vector: bpy.props.FloatVectorProperty(
        name="Scale",
        size=3,
        subtype="XYZ",
        default=(1.0, 1.0, 1.0),
        description="Scale factors",
    )
    axis_x: bpy.props.BoolProperty(name="X", default=True)
    axis_y: bpy.props.BoolProperty(name="Y", default=True)
    axis_z: bpy.props.BoolProperty(name="Z", default=True)
    space: bpy.props.EnumProperty(
        name="Space",
        items=[
            ("WORLD", "World", "Use world space"),
            ("LOCAL", "Local", "Use object local space"),
        ],
        default="WORLD",
    )
    use_pivot_override: bpy.props.BoolProperty(
        name="Use Pivot Override",
        default=False,
        description="Use the stored pivot override instead of the object origin",
    )
    pivot_override: bpy.props.FloatVectorProperty(
        name="Pivot Override",
        size=3,
        subtype="XYZ",
        default=(0.0, 0.0, 0.0),
    )


def active_axis_mask(props):
    return Vector(
        (
            1.0 if props.axis_x else 0.0,
            1.0 if props.axis_y else 0.0,
            1.0 if props.axis_z else 0.0,
        )
    )


def get_pivot(context, props):
    if props.use_pivot_override:
        return Vector(props.pivot_override)
    if context.object:
        return context.object.matrix_world.translation.copy()
    return Vector((0.0, 0.0, 0.0))


def build_space_matrix(obj, props):
    if props.space == "LOCAL" and obj is not None:
        return obj.matrix_world.to_3x3()
    return Matrix.Identity(3)


def apply_transform_object(obj, matrix, pivot):
    translation = Matrix.Translation(pivot)
    obj.matrix_world = translation @ matrix @ translation.inverted() @ obj.matrix_world


def apply_transform_edit(obj, matrix, pivot):
    bm = bmesh.from_edit_mesh(obj.data)
    for vert in bm.verts:
        vert.co = matrix @ (vert.co - pivot) + pivot
    bmesh.update_edit_mesh(obj.data)


def perform_transform(context, matrix, pivot):
    obj = context.object
    if obj is None:
        return
    if context.mode == "EDIT_MESH":
        apply_transform_edit(obj, matrix, pivot)
    else:
        apply_transform_object(obj, matrix, pivot)


class CAD_OT_set_pivot_from_selection(bpy.types.Operator):
    bl_idname = "cad_precision.set_pivot_from_selection"
    bl_label = "Set Pivot From Selection"
    bl_description = "Set pivot override from selected mesh element"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cad_precision
        obj = context.object
        if obj is None or obj.type != "MESH" or context.mode != "EDIT_MESH":
            self.report({"WARNING"}, "Select a mesh in Edit Mode")
            return {"CANCELLED"}

        bm = bmesh.from_edit_mesh(obj.data)
        selection = [v for v in bm.verts if v.select]
        if selection:
            coord = sum((v.co for v in selection), Vector()) / len(selection)
            props.pivot_override = obj.matrix_world @ coord
            props.use_pivot_override = True
            return {"FINISHED"}

        edges = [e for e in bm.edges if e.select]
        if edges:
            coords = []
            for edge in edges:
                coords.extend([edge.verts[0].co, edge.verts[1].co])
            coord = sum(coords, Vector()) / len(coords)
            props.pivot_override = obj.matrix_world @ coord
            props.use_pivot_override = True
            return {"FINISHED"}

        faces = [f for f in bm.faces if f.select]
        if faces:
            coord = sum((f.calc_center_median() for f in faces), Vector()) / len(faces)
            props.pivot_override = obj.matrix_world @ coord
            props.use_pivot_override = True
            return {"FINISHED"}

        self.report({"WARNING"}, "No mesh elements selected")
        return {"CANCELLED"}


class CAD_OT_clear_pivot_override(bpy.types.Operator):
    bl_idname = "cad_precision.clear_pivot_override"
    bl_label = "Clear Pivot Override"
    bl_description = "Clear the pivot override"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cad_precision
        props.use_pivot_override = False
        return {"FINISHED"}


class CAD_OT_move(bpy.types.Operator):
    bl_idname = "cad_precision.move"
    bl_label = "CAD Move"
    bl_description = "Move with numeric input"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cad_precision
        axis_mask = active_axis_mask(props)
        move = Vector(props.move_vector) * axis_mask
        space_matrix = build_space_matrix(context.object, props)
        matrix = Matrix.Translation(space_matrix @ move)
        pivot = get_pivot(context, props)
        perform_transform(context, matrix, pivot)
        return {"FINISHED"}


class CAD_OT_rotate(bpy.types.Operator):
    bl_idname = "cad_precision.rotate"
    bl_label = "CAD Rotate"
    bl_description = "Rotate with numeric input"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cad_precision
        axis_mask = active_axis_mask(props)
        rotation = Vector(props.rotate_vector) * axis_mask
        space_matrix = build_space_matrix(context.object, props)
        matrix = (
            Matrix.Rotation(rotation.x, 4, space_matrix @ Vector((1, 0, 0)))
            @ Matrix.Rotation(rotation.y, 4, space_matrix @ Vector((0, 1, 0)))
            @ Matrix.Rotation(rotation.z, 4, space_matrix @ Vector((0, 0, 1)))
        )
        pivot = get_pivot(context, props)
        perform_transform(context, matrix, pivot)
        return {"FINISHED"}


class CAD_OT_scale(bpy.types.Operator):
    bl_idname = "cad_precision.scale"
    bl_label = "CAD Scale"
    bl_description = "Scale with numeric input"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cad_precision
        scale = Vector(props.scale_vector)
        scale = Vector(
            (
                scale.x if props.axis_x else 1.0,
                scale.y if props.axis_y else 1.0,
                scale.z if props.axis_z else 1.0,
            )
        )
        space_matrix = build_space_matrix(context.object, props)
        matrix = (
            space_matrix
            @ Matrix.Diagonal((scale.x, scale.y, scale.z, 1.0))
            @ space_matrix.inverted()
        )
        pivot = get_pivot(context, props)
        perform_transform(context, matrix, pivot)
        return {"FINISHED"}


class CAD_PT_panel(bpy.types.Panel):
    bl_label = "CAD Precision"
    bl_idname = "CAD_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CAD Precision"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cad_precision

        layout.label(text="Transform Space")
        layout.prop(props, "space", expand=True)

        layout.label(text="Active Axes")
        row = layout.row(align=True)
        row.prop(props, "axis_x")
        row.prop(props, "axis_y")
        row.prop(props, "axis_z")

        layout.separator()
        layout.label(text="Move")
        layout.prop(props, "move_vector")
        layout.operator("cad_precision.move", text="Apply Move")

        layout.separator()
        layout.label(text="Rotate")
        layout.prop(props, "rotate_vector")
        layout.operator("cad_precision.rotate", text="Apply Rotate")

        layout.separator()
        layout.label(text="Scale")
        layout.prop(props, "scale_vector")
        layout.operator("cad_precision.scale", text="Apply Scale")

        layout.separator()
        layout.label(text="Pivot Override")
        layout.prop(props, "use_pivot_override")
        layout.prop(props, "pivot_override")
        row = layout.row(align=True)
        row.operator("cad_precision.set_pivot_from_selection", text="Set From Selection")
        row.operator("cad_precision.clear_pivot_override", text="Clear")


classes = (
    CADPrecisionProperties,
    CAD_OT_set_pivot_from_selection,
    CAD_OT_clear_pivot_override,
    CAD_OT_move,
    CAD_OT_rotate,
    CAD_OT_scale,
    CAD_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cad_precision = bpy.props.PointerProperty(type=CADPrecisionProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cad_precision


if __name__ == "__main__":
    register()
