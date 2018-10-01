class DetectionResult():

    # rectangular bounds of detected object.

    # x <tuple<int, int>>
    # the beginning and end x positions of the object within the image
    x = (None, None)

    # y <tuple<int, int>>
    # the beginning and end y positions of the object within the image
    y = (None, None)

    # bitmask <np.array<uint8>>
    # bitmask of the solution 
    bitmask = None

    def __init__(self, x, y, bitmask):
        self.x = x
        self.y = y
        self.bitmask = bitmask