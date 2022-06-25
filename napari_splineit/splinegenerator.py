import numpy as np
import torch
import math

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
    
    def getCoefsFromDenseContour(self, contourPoints):
        N = len(contourPoints)
        phi = np.zeros((N, self.M))
        if len(contourPoints.shape) == 1:
            r = np.zeros((N))
        elif len(contourPoints.shape) == 2:
            if (contourPoints.shape[1] == 2):
                r = np.zeros((N, 2))

        if self.closed:
            samplingRate = int(N / self.M)
            extraPoints = N % self.M
        else:
            samplingRate = int(N / (self.M - 1))
            extraPoints = N % (self.M - 1)

        for i in range(0, N):
            r[i] = contourPoints[i]

            if i == 0:
                t = 0
            elif t < extraPoints:
                t += 1.0 / (samplingRate + 1.0)
            else:
                t += 1.0 / samplingRate

            for k in range(0, self.M):
                if self.closed:
                    tval = self.wrapIndex(t, k)
                else:
                    tval = t - k
                if (tval > -self.halfSupport and tval < self.halfSupport):
                    basisFactor = self.splineGenerator.value(tval)
                else:
                    basisFactor = 0.0

                phi[i, k] += basisFactor

        if len(contourPoints.shape) == 1:
            c = np.linalg.lstsq(phi, r, rcond=None)

            self.coefs = np.zeros([self.M])
            for k in range(0, self.M):
                self.coefs[k] = c[0][k]
        elif len(contourPoints.shape) == 2:
            if (contourPoints.shape[1] == 2):
                cX = np.linalg.lstsq(phi, r[:, 0], rcond=None)
                cY = np.linalg.lstsq(phi, r[:, 1], rcond=None)

                self.coefs = np.zeros([self.M, 2])
                for k in range(0, self.M):
                    self.coefs[k] = np.array([cX[0][k], cY[0][k]])

        return self.coefs

    def getCoefsFromBinaryMask(self, binaryMask):
        from skimage import measure
        contours = measure.find_contours(binaryMask, 0)

        # if len(contours) > 1:
        #     raise RuntimeWarning(
        #         'Multiple objects were found on the binary mask. Only the first one will be processed.')

        coefs_list = []
        for i in range(len(contours)):
            coefs = self.getCoefsFromDenseContour(contours[i])
            coefs_list.append(coefs)
        return coefs_list

    def wrapIndex(self, t, k):
        wrappedT = t - k
        if k < t - self.halfSupport:
            if k + self.M >= t - self.halfSupport and k + self.M <= t + self.halfSupport:
                wrappedT = t - (k + self.M)
        elif k > t + self.halfSupport:
            if k - self.M >= t - self.halfSupport and k - self.M <= t + self.halfSupport:
                wrappedT = t - (k - self.M)
        return wrappedT
        
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
    
    def filterPeriodic(self, s):
        # This needs to be overloaded
        raise NotImplementedError(SplineGenerator.unimplementedMessage)
        return

class B1(SplineGenerator):
    def value(self, x):
        val = 0.0
        if 0 <= abs(x) and abs(x) < 1:
            val = 1.0 - abs(x)
        return val
    
    def filterPeriodic(self, s):
        return s
    
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
    
    def filterPeriodic(self, s):
        self.M = len(s)
        pole = -2.0 + math.sqrt(3.0)

        cp = np.zeros(self.M)
        for k in range(0, self.M):
            cp[0] += (s[(self.M - k) % self.M] * (pole ** k))
        cp[0] *= (1.0 / (1.0 - (pole ** self.M)))

        for k in range(1, self.M):
            cp[k] = s[k] + pole * cp[k - 1]

        cm = np.zeros(self.M)
        for k in range(0, self.M):
            cm[self.M - 1] += ((pole ** k) * cp[k])
        cm[self.M - 1] *= (pole / (1.0 - (pole ** self.M)))
        cm[self.M - 1] += cp[self.M - 1]
        cm[self.M - 1] *= (-pole)

        for k in range(self.M - 2, -1, -1):
            cm[k] = pole * (cm[k + 1] - cp[k])

        c = cm * 6.0

        eps = 1e-8
        c[np.where(abs(c) < eps)] = 0.0
        return c

    def support(self):
        return 4.0

