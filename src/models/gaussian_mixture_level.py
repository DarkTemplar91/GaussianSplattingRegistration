
class GaussianMixtureModel:
    def __init__(self, xyz = [], colors = [], opacities = [], covariance = [], features = []):
        self.xyz = xyz
        self.covariance = covariance
        self.colors = colors
        self.opacities = opacities
        self.features = features
