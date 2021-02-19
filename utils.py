import numpy as np
import splinegenerator as sg

def wrapIndex(t, k, M, half_support):
    wrappedT = t - k
    t_left = t - half_support
    t_right = t + half_support
    if k < t_left:
        if t_left <= k + M <= t_right:
            wrappedT = t - (k + M)
    elif k > t + half_support:
        if t_left <= k - M <= t_right:
            wrappedT = t - (k - M)
    return wrappedT


def phi_generator(M, contoursize_max):
    ts = np.linspace(0, float(M), num=contoursize_max, endpoint=False)
    wrapped_indices = np.array([[wrapIndex(t, k, M, 2)
                                 for k in range(M)] for t in ts])
    vfunc = np.vectorize(sg.B3().value)
    phi = vfunc(wrapped_indices)     
    phi = phi.astype(np.float32)
    np.save('phi_' + str(M) + '.npy',phi)
    return
