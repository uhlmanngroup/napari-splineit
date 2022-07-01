import numpy as np
from . import splinegenerator as sg


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


def phi_generator_impl(M, contoursize_max, gui_basis):
    ts = np.linspace(0, float(M), num=contoursize_max, endpoint=False)
    wrapped_indices = np.array(
        [[wrapIndex(t, k, M, 2) for k in range(M)] for t in ts]
    )
    if gui_basis == "linear":
        basis = sg.B1()
    elif gui_basis == "cubic":
        basis = sg.B3()
    else:
        raise RuntimeError(f"unknown basis: `{gui_basis}`")
    vfunc = np.vectorize(basis.value)
    phi = vfunc(wrapped_indices)
    phi = phi.astype(np.float32)
    return phi


def phi_generator(M, contoursize_max, gui_basis):
    phi = phi_generator_impl(M, contoursize_max, gui_basis)
    np.save("phi_" + str(M) + ".npy", phi)


def getCoefsFromKnots(knots, gui_basis):
    if gui_basis == "linear":
        basis = sg.B1()
    elif gui_basis == "cubic":
        basis = sg.B3()
    else:
        raise RuntimeError(f"unknown basis: `{gui_basis}`")
    knots = np.array(knots)
    coefsX = basis.filterPeriodic(knots[:, 0])
    coefsY = basis.filterPeriodic(knots[:, 1])
    coefs = np.hstack(
        (np.array([coefsX]).transpose(), np.array([coefsY]).transpose())
    )
    return coefs
