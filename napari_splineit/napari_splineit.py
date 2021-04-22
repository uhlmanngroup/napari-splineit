from enum import Enum
import pathlib
from magicgui import magicgui, magic_factory
import numpy as np
import time
import torch
import napari_splineit.splinegenerator as sg 
from napari_splineit.utils import phi_generator
from napari.qt import thread_worker
import napari

@magicgui(
        auto_call=True,
        basis={"choices": ["cubic", "linear"]}, 
)
def gui_basis(basis = "cubic"):
    return basis

@napari.Viewer.bind_key('w')
def spawn_instance(viewer: 'napari.Viewer'):
    mouse_position = viewer.cursor.position
    offset = np.array([[-10,0], [0,10], [10,0], [0, -10]])
    cp = mouse_position + offset
    objects_count = (len(viewer.layers)) // 3
    viewer.add_points(cp, size=3, name='control points ' + str(objects_count))
    cp = torch.from_numpy(cp).float()
    phi_generator(cp.shape[0], 500, 'cubic')
    phi = np.load('./phi_' + str(cp.shape[0]) + '.npy')
    phi = torch.from_numpy(phi)
    SplineContour = sg.SplineCurveSample(cp.shape[0],sg.B3(),True,cp)
    curve = SplineContour.sample(phi)
    curve = torch.cat([curve, torch.reshape(curve[0], (1,2))], axis = 0)
    viewer.add_shapes(curve, shape_type='path', edge_width=3,
                      edge_color='coral', face_color='royalblue', name='spline ' + str(objects_count))
    viewer.add_shapes(cp, shape_type='polygon', edge_width=2,
                      edge_color='teal', face_color='transparent', name='control polygon ' + str(objects_count))

@magic_factory(
    call_button=True,
    viewer={'visible': False, 'label': ' '},
    user_input={'mode': 'r', 'label': 'Input'},
    output={'mode': 'w', 'label': 'Output'},
        )
def napari_splineit(
    viewer : napari.Viewer,
    user_input: pathlib.Path,
    output: pathlib.Path,
        ):
    mode = napari_splineit._call_button.text
    
    if user_input.is_file():
        cp = np.load(user_input, allow_pickle = True)
        #ToDo: Need fix
        cp = cp.astype('int')
    else:
        cp = np.array([
            [[14,19], [14,35], [33,35], [33,19]],
            [[12,48], [14,66], [32,63], [35,43]],
            [[42,30], [41,65], [55,54], [63,35]]
        ])

    for i in range(len(cp)):
        viewer.add_points(cp[i], size=3, name='control points ' + str(i))

    cp = torch.from_numpy(cp).float()
    phi_generator(cp.shape[1], 500, 'cubic')

    phi = np.load('./phi_' + str(cp.shape[1]) + '.npy')
    phi = torch.from_numpy(phi)
    SplineContour = sg.SplineCurveSample(cp.shape[1],sg.B3(),True,cp)
    curve = SplineContour.sample(phi)
    curve = torch.cat([curve, torch.reshape(curve[:,0], (-1,1,2))], axis = 1)

    for i in range(len(cp)):
        viewer.add_shapes(curve[i], shape_type='path', edge_width=3,
                          edge_color='coral', face_color='royalblue', name='spline ' + str(i))
        
    for i in range(len(cp)):
        cp_polygon = viewer.add_shapes(cp[i], shape_type='polygon', edge_width=2,
                                       edge_color='teal', face_color='transparent', name='control polygon ' + str(i))
    
    objects_count = cp.shape[0]
    
    viewer.window.add_dock_widget(gui_basis) 
       
    get_cp(viewer, gui_basis, objects_count, output)
    
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
    
def update_layers(updates):
    viewer = updates[0]    
    idx = updates[1]
    gui_basis = updates[2]
    
    idx_cp = 'control points ' + str(idx)
    idx_spline = 'spline ' + str(idx)
    idx_control_polygon = 'control polygon ' + str(idx)
    
    if (gui_basis == 'linear'):
        basis = sg.B1()
    elif (gui_basis == 'cubic'):
        basis = sg.B3()
    
    cp = viewer.layers[idx_cp].data    
    cp = torch.from_numpy(cp).float()
    phi_generator(len(cp), 500, gui_basis)
    phi = np.load('./phi_' + str(len(cp)) + '.npy')
    phi = torch.from_numpy(phi)
    SplineContour = sg.SplineCurveSample(len(cp),basis,True,cp)
    curve = SplineContour.sample(phi)
    curve = torch.cat([curve, torch.reshape(curve[0], (1,2))],0)
    
    spline = viewer.layers[idx_spline]
    spline.selected_data = set(range(spline.nshapes))
    spline.remove_selected()

    spline.add(
        [curve],
        shape_type='path',
    ) 
    
    cp_polygon = viewer.layers[idx_control_polygon]
    cp_polygon.selected_data = set(range(cp_polygon.nshapes))
    cp_polygon.remove_selected()

    cp_polygon.add(
        [cp],
        shape_type='polygon',
    ) 
    
    viewer.active_layer = viewer.layers[idx_cp] 
    
@thread_worker(connect={'yielded': update_layers})
def get_cp(viewer, gui_basis, objects_count, output):
    cp_old = []
    m_old = []
    
    #ToDo: generalize object count 
    objects_count = (len(viewer.layers))//3
    
    for i in range(objects_count):
        idx_cp = 'control points ' + str(i)
        cp_old.append(viewer.layers[idx_cp].data.copy())
        m_old.append(viewer.layers[idx_cp].data.shape[0]) 
    basis_old = gui_basis.basis.value
    
    while True:             
        objects_count = (len(viewer.layers))//3
        
        basis_current = gui_basis.basis.value
        if basis_old == basis_current:
            pass
        else:
            basis_old = basis_current
            yield [viewer, 0, basis_current]     
        
        m_current = []
        for i in range(objects_count):
            idx_object = 'control points ' + str(i)
            m_current.append(viewer.layers[idx_object].data.shape[0])
        
        if len(m_current) > len(m_old):
            m_old.append(m_old[0])
        
        idx_m_update = list(map(np.less,m_old,m_current))
        idx_m_update = np.where(np.array(idx_m_update) == 1)[0]
        if len(idx_m_update) != 0:
            viewer.layers['control points ' + str(idx_m_update[0])].data = cp_addition(viewer.layers
                                                                           ['control points ' + str(idx_m_update[0])].data) 
            m_old = m_current.copy() 
        #because len of cp current is more, so equal not working
        cp_current = []
        for i in range(objects_count):
            idx_object = 'control points ' + str(i)
            cp_current.append(viewer.layers[idx_object].data.copy())
        
        if len(cp_current) > len(cp_old):
            cp_old.append(cp_old[0])
        
        idx_cp_update = list(map(np.array_equal,cp_old,cp_current))
        idx_cp_update = np.where(np.array(idx_cp_update) == 0)[0]
        if len(idx_cp_update) != 0: 
            cp_old = cp_current.copy()
            yield [viewer, idx_cp_update[0], basis_current]    
            
        time.sleep(0.1)
        
        if output is not None:
            np.save( output, np.array(cp_current, dtype = object))
            
        @viewer.mouse_drag_callbacks.append
        def track_mouse_click(viewer, event):
            yield
            if event.type == 'mouse_release':
                mouse_position = np.asarray(event.position)
                mouse_position = np.round(mouse_position).astype(int)
                
                objects_count = (len(viewer.layers))//3
                idx_active_layer = np.zeros(objects_count).astype('int')
                for i in range(objects_count):
                    cp_list = viewer.layers['control points ' + str(i)].data            
                    for j in range(len(cp_list)):
                        #ToDo: include a tolerance region of cp_list to compare
                        if(np.array_equal(mouse_position, cp_list[j])):
                            idx_active_layer[i] = 1
                            break                      
                    if np.count_nonzero(idx_active_layer) > 0:
                        break

                idx_active_layer = np.where(idx_active_layer)[0]

                if (len(idx_active_layer)) > 0:
                    idx_active_layer = idx_active_layer[0]
                    viewer.active_layer = viewer.layers['control points ' + str(idx_active_layer)]