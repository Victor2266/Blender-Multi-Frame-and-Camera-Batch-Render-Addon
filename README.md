
# Blender Addon: Multi-Frame-and-Camera-Batch-Renderer

## Description:

This is my code for a blender addon that allows me to select specific frames and cameras to render from all at once. 

Have you ever wanted to automate the tedious process of rendering from specific frames or frame ranges and having to switch the active camera?

For example, when you make an animation and want to render certain frames from different camera angles?

With this add-on, the active camera will automatically be swapped so you can render any frame range from as many camera angles as you like all at the press of a single button.

## Instructions:

The Panel is found in the Render Properties Tab on the right.

You can specify individual frames by entering the frame numbers separated by commas 
- (e.g., 1,25,250).

You can specify ranges of frames by entering the start and end frames separated by a dash 
- (e.g., 25-40).

If you want to specify both individual frames and ranges, you can do so by separating them with commas
- (e.g., 11,25,250,25-40).
  
![image](https://github.com/Victor2266/Blender-Multi-Frame-and-Camera-Selector-Addon/assets/46388269/e5324d3f-6c3b-48d2-8b25-683441a6a0ea)

Make sure you set the output path to a directory and not a file.

If you disable overwriting then it will skip the existing frames in the output directory (only works for .png .jpg .bmp .tiff .exr files for now). 
![image](https://github.com/Victor2266/Blender-Multi-Frame-and-Camera-Selector-Addon/assets/46388269/09ecede9-445a-430c-aea3-1a84ea13b5b5)

You probably want to disable Persistent Data under the performance options of Blender because if you are taking photos from multiple angles you want Blender to recalculate the amount of VRAM it needs for each angle instead of always using VRAM when it doesn't need to and eventually running out.
![image](https://github.com/Victor2266/Blender-Multi-Frame-and-Camera-Selector-Addon/assets/46388269/15149de3-90c5-42b9-b78a-9f1722ff3f69)


**WIP**
You can enable or disable the render preview window for each camera, disabling this option will save on some RAM depending on the resolution of the image preview. Disabling this option will also lock up Blender until the render is finished so you'd have to close Blender to cancel a render partway through.
The implementation of previews is a hacky solution that seems to work for me, disable the preview if it doesn't work.

## Installation:
Just Download this repo as a zip file and install it like any other blender add-on. 
![image](https://github.com/Victor2266/Blender-Multi-Frame-and-Camera-Selector-Addon/assets/46388269/40889a38-0aab-4a96-af62-46404082b76f)
![image](https://github.com/Victor2266/Blender-Multi-Frame-and-Camera-Selector-Addon/assets/46388269/2c5a01ee-ae0b-4bf5-9851-304a6cad0253)

Works as of Blender version 4.1.0
