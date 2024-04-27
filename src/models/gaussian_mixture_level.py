
class GaussianMixtureModel:
    def __init__(self, xyz = [], covariance = [], colors = [], opacities = [], features = []):
        self.cluster_level = 0
        self.hem_reduction = 0
        self.distance_delta = 0
        self.color_delta = 0
        self.xyz = xyz
        self.covariance = covariance
        self.colors = colors
        self.opacities = opacities
        self.features = features
