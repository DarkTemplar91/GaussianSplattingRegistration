

class GaussianMixtureModel:
    def __init__(self):
        self.cluster_level = 0
        self.hem_reduction = 0
        self.distance_delta = 0
        self.color_delta = 0
        self.xyz = []
        self.covariance = []
        self.colors = []
