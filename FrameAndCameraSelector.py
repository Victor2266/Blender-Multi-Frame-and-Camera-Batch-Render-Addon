bl_info = {
    "name": "Multiple Frame and Camera Selector",
    "author": "Victor Do",
    "version": (2, 2),
    "blender": (2, 80, 0),
    "location": "Render Properties > Custom Render Panel",
    "description": "Allows specifying custom frames or frame ranges and multiple cameras for rendering in batches",
    "category": "Render",
}

import bpy
import os
import time

class CameraSettings(bpy.types.PropertyGroup):
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
        description="If checked, the render will show a preview (uses more RAM)",
        default=True,
    )

class CustomRenderPanel(bpy.types.Panel):
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
        layout.operator("render.my_operator", text="Render Frames")

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

class RenderJob:
    def __init__(self, index, cam_setting):
        self.index = index
        self.cam_setting = cam_setting
        self.frames = []
        self.is_running = False
        self.is_cancelled = False

    def start(self, context):
        scene = context.scene
        scene.camera = self.cam_setting.camera
        frame_ranges = self.cam_setting.frame_ranges.split(',')
        
        for frame_range in frame_ranges:
            if '-' in frame_range:
                start_frame, end_frame = map(int, frame_range.split('-'))
                self.frames.extend(range(start_frame, end_frame + 1))
            else:
                self.frames.append(int(frame_range))
        self.original_filepath = scene.render.filepath
        self.render_next_frame(context)
        
        bpy.app.handlers.render_cancel.append(self.render_cancel_handler)

    def render_next_frame(self, context):
        if self.frames and not self.is_cancelled:
            frame = self.frames.pop(0)
            scene = context.scene
            scene.frame_set(frame)
            # Get the file extension based on the render settings
            file_format = scene.render.image_settings.file_format
            file_extension = '.png' if file_format == 'PNG' else '.jpg' if file_format == 'JPEG' else '.bmp' if file_format == 'BMP' else '.tiff' if file_format == 'TIFF' else '.exr' if file_format == 'OPEN_EXR' else ''
            check_filepath = os.path.join(self.original_filepath, f"{self.cam_setting.camera.name}_frame{frame}{file_extension}")
            filepath = os.path.join(self.original_filepath, f"{self.cam_setting.camera.name}_frame{frame}")
            scene.render.filepath = filepath

            # Check if the file already exists and if overwrite is disabled
            if not scene.render.use_overwrite and os.path.isfile(bpy.path.abspath(check_filepath)):
                print("MFCBR --- " +f"Skipping frame {frame} with {self.cam_setting.camera.name} because it has already been rendered")
                # Skip this frame and move to the next one
                def set_is_running_true():
                    self.is_running = True
                
                bpy.app.timers.register(set_is_running_true)
                
                bpy.app.timers.register(lambda: self.render_next_frame(bpy.context), first_interval=1.0)
            else:
                bpy.app.handlers.render_post.append(self.render_post_handler)
                print("MFCBR --- " +f"Started rendering frame {frame} with {self.cam_setting.camera.name}")
                def set_is_running_true():
                    self.is_running = True
                
                bpy.app.timers.register(set_is_running_true)

                bpy.ops.render.render('INVOKE_DEFAULT' if self.cam_setting.show_preview else 'EXEC_DEFAULT', write_still=True)
        else:
            self.finish()

    def render_cancel_handler(self, scene, dummy):
        bpy.app.handlers.render_cancel.remove(self.render_cancel_handler)
        print("MFCBR --- Cancel Render")
        def set_is_cancelled_true():
            self.is_cancelled = True
        
        bpy.app.timers.register(set_is_cancelled_true)

    def render_post_handler(self, scene, dummy):
        bpy.app.handlers.render_post.remove(self.render_post_handler)
        print("MFCBR --- Finished rendering a frame POST")
        if (not self.is_cancelled):
            bpy.app.timers.register(lambda: self.render_next_frame(bpy.context), first_interval=1.0)



    def finish(self):
        def set_is_running_false():
            self.is_running = False
            bpy.context.scene.render.filepath = self.original_filepath
            print(f"MFCBR --- Finished rendering all frames with {self.cam_setting.camera.name}")

        bpy.app.timers.register(set_is_running_false)


class RenderOperator(bpy.types.Operator):
    bl_idname = "render.my_operator"
    bl_label = "Render Operator"

    _timer = None
    _jobs = []
    _current_job = None

    def execute(self, context):
        self._jobs = [RenderJob(i, cam_setting) for i, cam_setting in enumerate(context.scene.cam_settings)]
        print(self._jobs)
        self._current_job = None

        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            #print("MFCBR --- TIMER EVENT TRIGGERED.")
            #print("MFCBR --- " +self._jobs)
            #print("MFCBR --- " +self._current_job)
            #if self._current_job is not None:
            #    print("MFCBR --- " +self._current_job.is_running)
            #    print("MFCBR --- " +self._current_job.is_cancelled)
                
            if self._current_job is not None and self._current_job.is_cancelled:
                return self.cancel(context)

            if self._current_job is None or not self._current_job.is_running:
                if self._jobs:
                    self._current_job = self._jobs.pop(0)
                    self._current_job.start(context)
                else:
                    return self.cancel(context)
            

        return {'PASS_THROUGH'}


    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        if self._current_job:
            self._current_job.finish()
        print("MFCBR --- All Camera Jobs Completed.")
        return {'CANCELLED'}

def register():
    bpy.utils.register_class(CameraSettings)
    bpy.types.Scene.cam_settings = bpy.props.CollectionProperty(type=CameraSettings)
    bpy.utils.register_class(CustomRenderPanel)
    bpy.utils.register_class(SCENE_OT_AddCamSetting)
    bpy.utils.register_class(SCENE_OT_RemoveCamSetting)
    bpy.utils.register_class(RenderOperator) 

def unregister():
    del bpy.types.Scene.cam_settings
    bpy.utils.unregister_class(CameraSettings)
    bpy.utils.unregister_class(CustomRenderPanel)
    bpy.utils.unregister_class(SCENE_OT_AddCamSetting)
    bpy.utils.unregister_class(SCENE_OT_RemoveCamSetting)
    bpy.utils.unregister_class(RenderOperator) 

if __name__ == "__main__":
    register()
