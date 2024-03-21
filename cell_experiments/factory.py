import random
import hashlib
import json


class Factory:

    """
    A class which represents a factory composed of zones, each having a labeling-system.

    Attributes
    ----------
    zones : list[int]
        the number of labeling systems on each zone

    Methods
    -------
    show()
        Pretty prints the generated factory

    create_label()
        Creates a randomly generated label which mimics the process of an object being randomly
        distributed to a labeling system for each zone in a sequential manner
    """

    def __init__(self, zones: list[int]):
        assert len(zones) > 0, "Factoy construction failed: no zones provided."
        self.zones = zones
        self.__factory = self.__generate_factory()

    def __generate_factory(self) -> dict:
        factory = {}
        n = 0
        for i in range(1, len(self.zones) + 1):
            for j in range(1, self.zones[i - 1] + 1):
                if f"zone {i}" not in factory:
                    factory[f"zone {i}"] = {}
                factory[f"zone {i}"][f"labeling-system {j}"] = ''.join(
                    hashlib.sha1((n + j).to_bytes(2, 'big')).hexdigest())
            n += self.zones[i - 1]
        return factory

    def __generate_zones(self) -> list[int]:
        return [int(zone * random.uniform(0.0, 1.0)) + 1 for zone in self.zones]

    def show(self) -> None:
        """Displays the factory with its associated zones, labeling systems (and respective labels)"""
        print(json.dumps({"Factory": self.__factory}, indent=4))

    def create_label(self) -> str:
        """Constructs a random label by sequentially choosing a labeling system of each zone of the factory

        Returns
        -------
        str
            a string representing a label
        """
        label = ""
        path = self.__generate_zones()
        for i in range(len(path)):
            label += self.__factory[f"zone {i + 1}"][f"labeling-system {path[i]}"] + "-"
        return label[:-1]
