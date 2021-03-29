import numpy as np
import torch

class SplineCurve:
    def __init__(self, M, splineGenerator, closed, coefs):
        if M >= splineGenerator.support():
            self.M = M
        else:
            raise RuntimeError('M must be greater or equal than the spline generator support size.')
            return

        self.splineGenerator = splineGenerator
        self.halfSupport = self.splineGenerator.support() / 2.0
        self.closed = closed
        self.coefs = coefs
        
class SplineCurveSample(SplineCurve):
    def sample(self, phi): 
        contour_points = torch.matmul(phi, self.coefs)
        return contour_points    

class SplineGenerator:
    unimplementedMessage = 'This function is not implemented.'

    def value(self, x):
        # This needs to be overloaded
        raise NotImplementedError(unimplementedMessage)
        return

    def support(self):
        # This needs to be overloaded
        raise NotImplementedError(unimplementedMessage)
        return

class B1(SplineGenerator):
    def value(self, x):
        val = 0.0
        if 0 <= abs(x) and abs(x) < 1:
            val = 1.0 - abs(x)
        return val
    
    def support(self):
        return 2.0

class B2(SplineGenerator):
    def value(self, x):
        val = 0.0
        if -1.5 <= x and x <= -0.5:
            val = 0.5 * (x ** 2) + 1.5 * x + 1.125
        elif -0.5 < x and x <= 0.5:
            val = -x * x + 0.75
        elif 0.5 < x and x <= 1.5:
            val = 0.5 * (x ** 2) - 1.5 * x + 1.125
        return val

    def support(self):
        return 3.0

class B3(SplineGenerator):
    def value(self, x):
        val = 0.0
        if 0 <= abs(x) and abs(x) < 1:
            val = 2.0 / 3.0 - (abs(x) ** 2) + (abs(x) ** 3) / 2.0
        elif 1 <= abs(x) and abs(x) <= 2:
            val = ((2.0 - abs(x)) ** 3) / 6.0
        return val

    def support(self):
        return 4.0