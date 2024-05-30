bl_info = {
    "name": "Multiple Frame and Camera Selector",
    "author": "Victor Do",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Render Properties > Custom Render Panel",
    "description": "Allows specifying custom frames or frame ranges and multiple cameras for rendering in batches",
    "category": "Render",
}

import bpy
import os

class CameraSettings(bpy.types.PropertyGroup):
    """Group of properties representing a camera setting."""
    camera: bpy.props.PointerProperty(
        name="Camera",
        type=bpy.types.Object,
        description="Camera to use for rendering",
        poll=lambda self, obj: obj.type == 'CAMERA',
    )
    frame_ranges: bpy.props.StringProperty(
        name="Frame Ranges",
        description="Specify frames or frame ranges separated by commas. For example: 11,25,250 or 25-40",
        default="",
    )
    show_preview: bpy.props.BoolProperty(
        name="Show Preview",
        description="If checked, the render will show a preview (uses more ram)",
        default=False,
    )

class CustomRenderPanel(bpy.types.Panel):
    """Creates a Panel in the Render properties window"""
    bl_label = "Frame & Camera Selector - Render Panel"
    bl_idname = "RENDER_PT_custom"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        for i, cam_setting in enumerate(scene.cam_settings):
            box = layout.box()
            row = box.row()
            row.prop(cam_setting, "camera", text=f"Camera {i+1}")
            row.operator("scene.remove_cam_setting", text="", icon='X').index = i
            box.prop(cam_setting, "frame_ranges", text="Frames or Frame Ranges")
            box.prop(cam_setting, "show_preview", text="Show Preview")

        layout.operator("scene.add_cam_setting", text="Add Camera Setting")
        layout.operator("scene.render_frames", text="Render Frames")

class SCENE_OT_AddCamSetting(bpy.types.Operator):
    bl_idname = "scene.add_cam_setting"
    bl_label = "Add Camera Setting"

    def execute(self, context):
        context.scene.cam_settings.add()
        return {'FINISHED'}

class SCENE_OT_RemoveCamSetting(bpy.types.Operator):
    bl_idname = "scene.remove_cam_setting"
    bl_label = "Remove Camera Setting"
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.cam_settings.remove(self.index)
        return {'FINISHED'}

class SCENE_OT_RenderFrames(bpy.types.Operator):
    bl_idname = "scene.render_frames"
    bl_label = "Render Frames"

    def execute(self, context):
        scene = context.scene
        original_camera = scene.camera
        original_frame = scene.frame_current
        original_filepath = scene.render.filepath

        # Check if the original output path is a directory
        if not os.path.isdir(original_filepath):
            self.report({'ERROR'}, "The output path is not a directory.")
            return {'CANCELLED'}

        for cam_setting in scene.cam_settings:
            scene.camera = cam_setting.camera
            frame_ranges = cam_setting.frame_ranges.split(',')

            for frame_range in frame_ranges:
                if '-' in frame_range:
                    start_frame, end_frame = map(int, frame_range.split('-'))
                    for frame in range(start_frame, end_frame + 1):
                        scene.frame_set(frame)
                        scene.render.filepath = os.path.join(original_filepath, f"{cam_setting.camera.name}_frame{frame}")
                        if cam_setting.show_preview:
                            bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
                        else:
                            bpy.ops.render.render(write_still=True)
                else:
                    scene.frame_set(int(frame_range))
                    scene.render.filepath = os.path.join(original_filepath, f"{cam_setting.camera.name}_frame{frame_range}")
                    if cam_setting.show_preview:
                            bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
                        else:
                            bpy.ops.render.render(write_still=True)

        scene.camera = original_camera
        scene.frame_set(original_frame)
        scene.render.filepath = original_filepath

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CameraSettings)
    bpy.types.Scene.cam_settings = bpy.props.CollectionProperty(type=CameraSettings)
    bpy.utils.register_class(CustomRenderPanel)
    bpy.utils.register_class(SCENE_OT_AddCamSetting)
    bpy.utils.register_class(SCENE_OT_RemoveCamSetting)
    bpy.utils.register_class(SCENE_OT_RenderFrames)

def unregister():
    del bpy.types.Scene.cam_settings
    bpy.utils.unregister_class(CameraSettings)
    bpy.utils.unregister_class(CustomRenderPanel)
    bpy.utils.unregister_class(SCENE_OT_AddCamSetting)
    bpy.utils.unregister_class(SCENE_OT_RemoveCamSetting)
    bpy.utils.unregister_class(SCENE_OT_RenderFrames)

if __name__ == "__main__":
    register()
