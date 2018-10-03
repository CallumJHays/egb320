class DetectionResult():

    # rectangular bounds of detected object.

    # coords <tuple<tuple<int, int>, tuple<int, int>>>
    # pixel coords of lower left and upper-right corners of bounding box rect, respectively
    coords = (None, None)

    # bitmask <np.array<uint8>?>
    # bitmask of the solution 
    bitmask = None

    def __init__(self, coords, bitmask=None):
        self.coords = coords
        self.bitmask = bitmask