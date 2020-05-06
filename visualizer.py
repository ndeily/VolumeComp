#  Copyright (c) 2020 Nicholas Deily


from vtkplotter import *
import numpy as np
from scipy.spatial import distance
from point_cloud_funcs import *
import vtk



def visualize(iteration, error, X, Y, vp, pts, text, max_ittr):
    if iteration > 0:
        pct = round((iteration/max_ittr)*100)
        text.SetText(7,"Refining Alignment: {}%".format(pct))
        pts.points(Y)
        vp.show()



def show_mesh(input_mesh, dists, plotter, spacing, tolerance = None):
    
    #vp2 = Plotter(bg = 'bb', size='fullscreen')
    vp2 = plotter
    plotter.clear()
    if tolerance is not None:
        try:
            poly_data = input_mesh.polydata()
            sil = vtk.vtkPolyDataSilhouette()
            sil.SetInputData(poly_data)
            sil.SetCamera(vp2.camera)
            silMapper = vtk.vtkPolyDataMapper()
            silMapper.SetInputConnection(sil.GetOutputPort())
            mesh1 = mesh.Mesh(alpha=0.21)
            mesh1.lw(3).c('w').SetMapper(silMapper)
            
            vp2 += mesh1
            
            pts = input_mesh.points()
            def_pts = []
            for i, dist in enumerate(dists):
                if dist > tolerance:
                    def_pts.append(pts[i])
            arr = np.array(def_pts)
            arr = removeOutliers(arr, spacing)
            cl = cluster(arr, radius=spacing)
            err_num = 0
            sph_arr = []
            for pt_cl in cl.GetParts():
                err_num += 1
                cl_pts = pt_cl.points()
                hull_pt1, hull_pt2 = furthest_pts(cl_pts)
                cnt_pnt = (hull_pt1+hull_pt2)/2
                rdi = 1*pt_dist(cnt_pnt, hull_pt2)
                sp = shapes.Sphere(cnt_pnt, rdi, c=(1,0,0), alpha = .15, quads = True).wireframe(.5)
                sph_arr.append(sp)
                vp2 += sp
            
            
            txt = Text2D("Detected {} Object Defect".format(err_num), pos = 8, c='gray', s=1.31)
            vp2 += txt
            vp2.show(interactive=1)
        except AttributeError as error:
            print("Error during automatic error detection:", error)

                
    vp2.clear()
    

    input_mesh.pointColors(dists,cmap = 'jet')

    
    input_mesh.addScalarBar(title="Divergence", pos=(0, 0.24), titleFontSize=16, titleYOffset=25)

    
    def slider(widget, event):
        value = widget.GetRepresentation().GetValue()
        cuttoff = round(value*900)
        hidden = np.full((cuttoff), 0.0)
        show =  np.full((900-cuttoff), 1)
        opacities = np.concatenate((hidden, show), axis=None)
        input_mesh.pointColors(dists, cmap = 'jet', alpha =opacities)
    

    vp2.addSlider2D(slider, xmin=0.0, xmax=1, value=0.0, showValue=False, pos=[(0.9, 1), (0.9, 0)], c='lightgray')
    ambient, diffuse, specular = .4, 1., 0.
    specularPower, specularColor= 20, 'white'
    input_mesh.lighting('default', ambient, diffuse, specular, specularPower, specularColor)
    
    vp2 += input_mesh
    

    
    




