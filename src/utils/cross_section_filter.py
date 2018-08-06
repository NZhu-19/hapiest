from typing import Tuple, List


# class CrossSectionMeta:
#     def __init__(self, id):
#         self.id = id
#     def get_name(self):
#         raise Exception("Not implemented")

class CrossSectionFilter:

    # Map molecule name to a list of dictionaries, which contain meta info about available cross sections.
    XSC_META = {
        'MOLiCuLi': [
            {
                'temperature': 100.0,
                'pressure': 0.0,
                'wn_range': (0.51, 1000.0)
            },
        ]
    }

    def __init__(self, molecule: str, wn_range: Tuple[float, float] = None, pressure_range: Tuple[float, float] = None,
                 temp_range: Tuple[float, float] = None):
        self.molecule = molecule
        self.wn_range = wn_range
        self.temp_range = temp_range
        self.pressure_range = pressure_range

    def get_cross_sections(self) -> List[dict]:
        if self.molecule not in CrossSectionFilter.XSC_META:
            return []
        return list(map(self.passes, CrossSectionFilter.XSC_META[self.molecule]))

    def passes(self, meta):
        return      (self.pressure_range == None or (meta['pressure'] > self.pressure_range[0] and meta['pressure'] < self.pressure_range[1])) \
                and (self.temp_range == None or (meta['temperature'] > self.temp_range[0] and meta['temperature'] < self.temp_range[1])) \
                and (self.wn_range == None or (meta['wn_range'][0] < self.wn_range[0] and meta['wn_range'][1] > self.wn_range[1]))
