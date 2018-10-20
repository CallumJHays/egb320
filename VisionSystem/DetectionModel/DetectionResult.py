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

    
    def area(self):
        ((x1, y1), (x2, y2)) = self.coords
        return (x2 - x1) * (y2 - y1)