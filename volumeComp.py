#  Copyright (c) 2020 Nicholas Deily


import numpy as np
from pycpd import RigidRegistration
from functools import partial
from scipy.spatial import distance
import argparse
import open3d as o3d
from vtkplotter import *
from vtkplotter.plotter import *
from point_cloud_funcs import *
from visualizer import *



def loadObject(file_path, thresholds=None):
    
    #Load object from file_path
    load_object = load(file_path)

    object_mesh = mesh.Mesh()
    
    #If object is loaded from a volume image or dicom series, isosurface the volume
    if isinstance(load_object, volume.Volume):
        
        load_object = load_object.gaussianSmooth(sigma=(.6, .6, .6)).medianSmooth(neighbours=(1,1,1))
        
        #Extract surface from given threshold values OR use automatic thresholding if no threshold is specified
        if thresholds is not None:
            object_mesh = load_object.isosurface(threshold= thresholds).extractLargestRegion().extractLargestRegion()
        else:
            object_mesh = load_object.isosurface().extractLargestRegion().extractLargestRegion()
        
        object_mesh
        
        if len(object_mesh.points()) > 1000000:
            object_mesh = object_mesh.decimate(N=100000, method='pro', boundaries=False)

    else:
        object_mesh = load_object.triangulate()
    return object_mesh




def compareMesh(src_mesh, tgt_mesh, tolerance):
    
    src_points = src_mesh.points(copy=True)
    tgt_points = tgt_mesh.points(copy=True)
    
    #Sample points over surface of both meshes
    src_samples = generateSamples(src_mesh, 2000)
    tgt_samples = generateSamples(tgt_mesh, 2000)

    hull_pt1, hull_pt2 = furthest_pts(src_samples)
    cnt_pnt = (hull_pt1+hull_pt2)/2
    src_points = src_points - cnt_pnt
    src_samples = src_samples - cnt_pnt
    pt_a, pt_b = furthest_pts(tgt_samples)
    orig_dist = pt_dist(pt_a, pt_b)
    new_dist = pt_dist(hull_pt1, hull_pt2)
    const_mult = orig_dist/new_dist
    src_points = src_points*const_mult
    src_samples = src_samples*const_mult
    
    
    vp = Plotter(interactive=0, axes=7, size='fullscreen', bg='bb')
    vp.legendBC = (0.22, 0.22, 0.22)
    vp.legendPos = 1
    txt = Text2D("Loading Models...", pos = 8, c='gray', s=1.31)
    vp += txt
    tgt_pts = Points(tgt_samples, r=6, c='deepskyblue', alpha= 1).legend("Target")
    vp += tgt_pts
    vp.show()
    txt.SetText(7, "Initiating Alignment")
    src_pts = Points(src_samples, r=6, c='yellow', alpha = 1).legend("Source")
    vp += src_pts
    vp.show()

    #Roughly align both meshes (global registration)
    spacing = np.mean(distance.pdist(src_samples))
    src_samples, src_points = perform_global_registration(src_samples,tgt_samples,src_points, spacing)

    
    txt.SetText(7, "Refining Alignment")
    vp.show()

    #Refine mesh alignment (local registration)
    cpd_ittr = 60
    callback = partial(visualize, vp=vp, pts = src_pts, text = txt, max_ittr = cpd_ittr)
    reg = RigidRegistration(max_iterations = cpd_ittr, **{ 'X': tgt_samples, 'Y': src_samples })
    src_samples, [s,R,t] = reg.register(callback)
    src_points = s*np.dot(src_points, R) + t
    src_pts.points(src_samples)

    
    vp.renderer.RemoveAllViewProps()
    txt.SetText(7, "Alignment Complete")
    vp.show()

    
    for i in range(360):
        if i == 60:
            txt.SetText(7, "")
        vp.camera.Azimuth(.75)
        vp.show()


    src_mesh.points(src_points)

    tgt_samples = generateSamples(tgt_mesh, 6000)
    txt.SetText(7,"Performing Added Surface Analysis...")
    vp.show()


    ratio = 2000/min(len(tgt_points), len(src_points))
    spacing = 3*spacing*ratio
    #Generate distances for heat map
    dists = distance.cdist(src_points,tgt_samples).min(axis=1)
    txt.SetText(7,"Press Q to Continue")
    vp.show(interactive=1)
    show_mesh(src_mesh, dists, vp, spacing/2, tolerance=tolerance)
    txt2 = Text2D("Displaying Input Object 1 \n \nUse slider to isolate \ndefective/added surfaces")
    vp += txt2
    vp.addGlobalAxes(axtype=8, c='white')
    vp.show(axes=8, interactive=1)
    txt.SetText(7,"Performing Missing Surface Analysis...")
    vp += txt
    vp.show(interactive=0)
    src_mesh.points(src_points)
    src_samples = generateSamples(src_mesh, 6000)
    #Generate distances for heat map
    dists = distance.cdist(tgt_points,src_samples).min(axis=1)
    show_mesh(tgt_mesh, dists, vp, spacing/2, tolerance=tolerance)
    txt2.SetText(2,"Displaying Input Object 2 \n \nUse slider to isolate \ndefective/missing surfaces")
    vp += txt2
    vp.addGlobalAxes(axtype=8, c='white')
    vp.show(axes=8, interactive=1)


def main(argv):

    src_mesh = loadObject(argv.filePath1, thresholds = argv.thresholds1)
    tgt_mesh = loadObject(argv.filePath2, thresholds = argv.thresholds2)
    compareMesh(src_mesh, tgt_mesh, tolerance=argv.errorTolerance)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Compares two objects to each other for geometric similarity. Accepts inputs of volume images, dicom series or mesh object. Input objects do not have to be the same type.')
    
    parser.add_argument('-f1', '--filePath1', type=str, help = "File path to input object: Accepts volume image (.tiff, .vti, .slc etc...), directory containing Dicom series, or mesh objects (.stl, .obj, .ply etc...)", required = True)
    
    parser.add_argument('-f2', '--filePath2', type=str, help = "File path to original object: Accepts volume image (.tiff, .vti, .slc etc...), directory containing Dicom series, or mesh objects (.stl, .obj, .ply etc...)", required = True)
    
    parser.add_argument('-t1', '--thresholds1', nargs='+', type=int, help = "Optional: Dual threshold values for feature extraction for input object. Ex: -200, 100, -500, 200")
    
    parser.add_argument('-t2', '--thresholds2', nargs='+', type=int, help = "Optional: Dual threshold values for feature extraction for original object. Ex: -200, 100, -500, 200")
    
    parser.add_argument('-et', '--errorTolerance', type=float, help = "Optional: Provide a maximum error tolerance for automatic error detection.")

    main(parser.parse_args())


