#  Copyright (c) 2020 Nicholas Deily


import open3d as o3d
import numpy as np
import copy
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist
import point_cloud_utils as pcu
from scipy.spatial import distance


def generateSamples(mesh, num):
    vertices = mesh.points()
    faces = np.asarray(mesh.faces())
    samples = pcu.sample_mesh_lloyd(vertices, faces, num)
    return samples

def pt_dist(pt_a, pt_b):
    return(np.sqrt(np.sum((pt_a-pt_b)**2, axis=0)))

def spherical(pt):
    x,y,z       = pt
    r       =  np.sqrt(x*x + y*y + z*z)
    theta   =  np.arccos(z/r)*(180/ np.pi)
    phi     =  np.arctan2(y,x)*(180/ np.pi)
    return [r,theta,phi]

def furthest_pts(points):
    hullpoints = points
    hdist = []
    if len(points) < 400:
        hdist = cdist(points, points, metric='euclidean')
    else:
        hull = ConvexHull(points)
        hullpoints = points[hull.vertices,:]
        hdist = cdist(hullpoints, hullpoints, metric='euclidean')
    
    bestpair = np.unravel_index(hdist.argmax(), hdist.shape)

    hull_pts = np.asarray([hullpoints[bestpair[1]],hullpoints[bestpair[0]]])
    hull_pts = hull_pts.astype('float64') 
    hull_pts.view('f8,f8,f8').sort(order=['f1'], axis=0)
    hull_pt1 = hull_pts[0]
    hull_pt2 = hull_pts[1]

    return hull_pt1, hull_pt2

def preprocess_point_cloud(pcd, voxel_size):
    pcd_down = pcd.voxel_down_sample(voxel_size)
    radius_normal = voxel_size * 5
    pcd_down.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))
    radius_feature = voxel_size * 5
    pcd_fpfh = o3d.registration.compute_fpfh_feature(pcd_down, o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def prepare_point_clouds(sourcePts, targtPts, voxel_size):

    source = o3d.geometry.PointCloud()
    source.points = o3d.utility.Vector3dVector(sourcePts)
    target = o3d.geometry.PointCloud()
    target.points = o3d.utility.Vector3dVector(targtPts)
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
    return source, target, source_down, target_down, source_fpfh, target_fpfh



def execute_fast_global_registration(source_down, target_down, source_fpfh,
                                     target_fpfh, voxel_size, iterations = None):
    distance_threshold = voxel_size * 0.5
    if iterations != None:
        result = o3d.registration.registration_fast_based_on_feature_matching( source_down, target_down, source_fpfh, target_fpfh,o3d.registration.FastGlobalRegistrationOption(maximum_correspondence_distance=distance_threshold, iteration_number= 15))
        return result
    else:
        result = o3d.registration.registration_fast_based_on_feature_matching( source_down, target_down, source_fpfh, target_fpfh,o3d.registration.FastGlobalRegistrationOption(maximum_correspondence_distance=distance_threshold))
        return result


def perform_global_registration(source, target, source_points, spacing):

    size = spacing/24

    source, target, source_down, target_down, source_fpfh, target_fpfh = \
        prepare_point_clouds(source, target, size)

    result_fast = execute_fast_global_registration(source_down, target_down,
                                                   source_fpfh, target_fpfh, size)

    pts_cloud = o3d.geometry.PointCloud()
    pts_cloud.points = o3d.utility.Vector3dVector(source_points)
    
    return_samples = source.transform(result_fast.transformation)
    return_pts = pts_cloud.transform(result_fast.transformation)
    src_samples = np.asarray(return_samples.points)
    src_points = np.asarray(return_pts.points)
    
    return src_samples,src_points
