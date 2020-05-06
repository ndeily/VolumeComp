# Overview
A python based tool for analyzing the geometric similarity of two 3D objects. Input objects can be in the form of a mesh (.stl, .obj, .ply etc.), dicom series (folder containing .dcm files), or volume image (.tiff, .vti, .slc etc.)

**Process:**  
**1.** Objects are loaded and mesh surfaces are constructed for volume-image inputs  
**2.** Objects are aligned using point set registration  
**3.** Heatmaps are generated and displayed in the error isolation tool (see examples below) 

# Setup
The following external packages are required:  
**numpy**  
**scipy**  
**matplotlib**  
**VTK**  
**vtkplotter**  
**pycpd**  
**Open3D**  
**point_cloud_utils**  

# Usage
Invoke `volumeComp.py` with the following arguments:

`-f1`: (Required) The filepath to the source object (object comparison is performed on)  
`-f2`: (Required) The filepath to the target object (original object that the source object is compared to)  
Note: For a dicom series, the filepath should point to the directory containing the .dcm files

`-t1`: (Optional) Threshold values for feature extraction for source object if a volume image or dicom series is specified   
`-t2`: (Optional) Threshold values for feature extraction for target object if a volume image or dicom series is specified   
Note: Dual thresholding is supported


# Examples
Compare a modified bone mesh with hollowed-out internal regions to its original model:  
```
python volumeComp.py -f1 "./Examples/bone_modified.stl" -f2 "./Examples/bone_tgt.stl" 
```
<p align="center">
    <img  src="https://user-images.githubusercontent.com/54589801/81141083-5ff77600-8f20-11ea-9ae5-e1df37984010.gif">
</p>


Compare CT scans of a 3D printed trachea to its original 3D model:  
```
python volumeComp.py -f1 "./Examples/trachea_scans" -f2 "./Examples/trachea.obj" -t1 -720 100
```
<p align="center">
    <img  src="https://user-images.githubusercontent.com/54589801/81140773-7a7d1f80-8f1f-11ea-80b7-5ddaa2d5594f.gif">
</p>

# Automatic Error Detection (Beta)

Optionally add a maximum error tolerance using the `-et` argument to automatically detect and highlight error regions

**Example:**
```
python volumeComp.py -f1 "./Examples/trachea_scans" -f2 "./Examples/trachea.obj" -t1 -720 100 -et 2.15
```
