import pickle
from abc import ABC, abstractmethod



class DetectionModel(ABC):

    # apply <np.array<uint8> -> DetectionResult>
    @abstractmethod
    def apply(self, img):
        pass


    @staticmethod
    def load(path):
        return pickle.load(open(path, 'rb'))


    def save(self, path):
        pickle.dump(self, open(path, 'wb'), -1)