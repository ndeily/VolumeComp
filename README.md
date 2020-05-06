# VolumeComp
Python based program for comparing volume objects (or volume images) for geometric similarity. 

VolumeComp takes 2 volume objects in the form of a mesh (.stl, .obj, .ply etc.), dicom series (folder containing .dcm files), or volume image (.tiff, .vti, .slc etc.), and displays a visual comparison for error isolation.

# Setup
The following external packages are required: **numpy**,**scipy**, **matplotlib**, **VTK**, **vtkplotter**, **pycpd**, **Open3D**, and **point_cloud_utils**

# Usage
Invoke with the following arguments:

`-f1`: (Required) The filepath to the source object (object comparison is performd on)

`-f2`: (Required) The filepath to the target object (original object that the source object is compared to)

Note: For dicom series, filepaths should point to the directory containing the series

`-t1`: (Optional) Threshold values for feature extraction for source object if a volume image or dicom series is specified 

`-t12`: (Optional) Threshold values for feature extraction for target object if a volume image or dicom series is specified 

Ex: `-t1 100, 400`

Ex: `-t2 -200, 100, -500, 200` (dual thresholding)


## Examples:
Compare a modified bone mesh object to its original model:
```
python volumeComp.py -f1 "./Examples/bone_modified.stl" -f2 "./Examples/bone_tgt.stl" 
```
<p align="center">
![demo3](https://user-images.githubusercontent.com/54589801/81141083-5ff77600-8f20-11ea-9ae5-e1df37984010.gif)
</p>

Compare CT scans of a 3D printed trachea to its original 3D model:
```
python volumeComp.py -f1 "./Examples/trachea_scans" -f2 "./Examples/trachea.obj" -t1 -720 100
```
<p align="center">
![demo1](https://user-images.githubusercontent.com/54589801/81140773-7a7d1f80-8f1f-11ea-80b7-5ddaa2d5594f.gif)
</p>


## Automatic Error Detection (Beta)

Optionally add a maximum error tolerance using the `-et` argument to automatically detect and highlight error regions in the source mesh or missing regions

Example:
```
python volumeComp.py -f1 "./Examples/trachea_scans" -f2 "./Examples/trachea.obj" -t1 -720 100
```
