

class GaussianMixtureLevel:

    def __init__(self, xyz, covariance, colors, opacity, weight = 1):
        self.xyz = xyz.detach().clone()
        self.opacity = opacity.detach().clone()
        self.covariance = covariance.detach().clone()
        self.features_dc = colors.detach().clone()
        self.weight = weight