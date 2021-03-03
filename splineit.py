import napari
from napari.qt import thread_worker
import torch
import numpy as np
import splinegenerator as sg
from utils import phi_generator
from PIL import Image
import time

def cp_addition(cp_current):
    cp_old = cp_current[:-1]
    new_element = cp_current[-1]

    delta = []
    delta2 = []

    for i in range(len(cp_old)):
        delta.append(cp_old[i] - new_element)
        delta2. append(cp_old[i] - cp_old[i-1])
 
    delta = np.linalg.norm(delta, axis = 1)
    delta = np.repeat(delta, 2)
    delta = np.roll(delta, -1)
    delta = np.reshape(delta, (-1,2))
    delta = np.sum(delta, axis = 1)
    
    delta2 = np.linalg.norm(delta2, axis = 1)
    delta2 = np.roll(delta2, -1)
    
    delta /= delta2
   
    cp_current  = np.insert(cp_old, np.argmin(delta) + 1, new_element, axis = 0)
    return cp_current

with napari.gui_qt():    
    #cell = np.zeros((64,64))
    cell = Image.open('./data/bbbc038.tif')
    cell = np.array(cell)
    viewer = napari.Viewer()
    layer = viewer.add_image(cell)
    
    cp = np.array([[73,34], [40,51], [43,65], [36,81], [82,102], [115,78]])
    viewer.add_points(cp, size=2, name='control points')
    cp = torch.from_numpy(cp).float()

    phi_generator(len(cp), 500)

    phi = np.load('./phi_' + str(len(cp)) + '.npy')
    phi = torch.from_numpy(phi)
    SplineContour = sg.SplineCurveSample(len(cp),sg.B3(),True,cp)
    curve = SplineContour.sample(phi)
    curve = torch.cat([curve, torch.reshape(curve[0], (1,2))],0)

    spline = viewer.add_shapes(curve, shape_type='path', edge_width=0.5,
                              edge_color='coral', face_color='royalblue', name='spline')
    
    cp_polygon = viewer.add_shapes(cp, shape_type='polygon', edge_width=0.2,
                              edge_color='teal', face_color='transparent', name='control polygon')

    def update_layers(cp):
        cp = torch.from_numpy(cp).float()
        phi_generator(len(cp), 500)
        phi = np.load('./phi_' + str(len(cp)) + '.npy')
        phi = torch.from_numpy(phi)
        SplineContour = sg.SplineCurveSample(len(cp),sg.B3(),True,cp)
        curve = SplineContour.sample(phi)
        curve = torch.cat([curve, torch.reshape(curve[0], (1,2))],0)
        
        spline.selected_data = set(range(spline.nshapes))
        spline.remove_selected()

        spline.add(
            [curve],
            shape_type='path',
        ) 
        
        cp_polygon.selected_data = set(range(cp_polygon.nshapes))
        cp_polygon.remove_selected()

        cp_polygon.add(
            [cp],
            shape_type='polygon',
        ) 

    @thread_worker(connect={'yielded': update_layers})
    def get_cp():
        cp_old = viewer.layers[1].data.copy()
        m_old = len(cp_old)
        while True:             
            m_current = len(viewer.layers[1].data)
            if m_old < m_current:               
                viewer.layers[1].data = cp_addition(viewer.layers[1].data) 
            m_old = m_current           
            cp_current = viewer.layers[1].data.copy()           
            
            if np.array_equal(cp_old, cp_current):
                pass
            else:
                cp_old = cp_current.copy()
                yield cp_current            
            time.sleep(0.1)            
    get_cp()
