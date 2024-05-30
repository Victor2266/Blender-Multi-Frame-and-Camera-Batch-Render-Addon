
# Blender-Multi-Frame-and-Camera-Selector

## Description:

This is my code for a blender addon that allows me to select specific frames and cameras to render from automatically. 

Have you ever wanted to automate the tedious process of rendering from specific frames or frame ranges and having to switch the active camera?

For example, when you make an animation and want to use render certain frames from different camera angles?

With this add-on, the active camera will automatically be swapped so you can render frame 42 from as many camera angles as you like all at the press of a single button.

## Instructions:

You can specify individual frames by entering the frame numbers separated by commas 
- (e.g., 11,25,250).

You can specify ranges of frames by entering the start and end frames separated by a dash 
- (e.g., 25-40).

If you want to specify both individual frames and ranges, you can do so by separating them with commas
- (e.g., 11,25,250,25-40).

Make sure you set the output path to a directory and not a file.

**WIP**
You can enable or disable the render preview, disabling this option will save a bit on RAM depending on the resolution of the image preview. Disabling this option will also lock up blender until the render is finished.
