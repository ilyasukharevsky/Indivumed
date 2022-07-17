import os
import re
import json
from typing import List, Type

PATH_RE = re.compile("^(?P<case_id>[\w\d]+)-(?P<sample_label>[\w\d-]+)\/(?P<data_type>[\w]+)"
                     "\/(?P<barcode>[\w]+)_(\w+)_(\w+)-(\w+)_(?P<marker_forward>[a-zA-Z]+)-"
                     "(?P<marker_reverse>[a-zA-Z]+)_L(?P<lane>[\d]+)_(.+)fastq.gz$")
JSON_INDENT = 4


class FatalError(Exception):
    pass


class DataExtractor:
    def __init__(self, i_json: str, o_json: str):
        self._path_check(i_json)
        self.o_json = o_json
        self.paths = self._set_paths(i_json)
        self.meta_data = dict()

    def _set_paths(self, i_json: str) -> List[str]:
        with open(i_json) as i_paths:
            paths = json.load(i_paths)
        if type(paths) is not list or any(type(path) is not str for path in paths):
            raise FatalError("Input JSON contains wrong data type.")
        return paths

    def _path_check(self, i_json: str) -> None:
        if not os.path.exists(i_json):
            raise IOError("The JSON file {} does not exist.".format(i_json))

    def _extract_meta_data(self) -> None:
        for path in self.paths:
            match = PATH_RE.match(path)
            if not match:
                print("The path {} is corrupted, ignoring.".format(path))
            else:
                self._register_meta_data(path, match)

    def _register_meta_data(self, path: str, match: re.Match):
        sample_id = "{}-{}".format(match.group("case_id"), match.group("sample_label"))
        if sample_id in self.meta_data:
            self._add_new_lane_to_existing_sample(path, match, sample_id)
        else:
            self._register_new_sample(path, match, sample_id)

    def _register_new_sample(self, path: str, match: re.Match, sample_id: str) -> None:
        meta_data = {"case_id": match.group("case_id"),
                     "sample_label": match.group("sample_label"),
                     "sample_id": sample_id,
                     "data_type": match.group("data_type"),
                     "lanes": [self._get_new_lane(match, path)]
                     }
        self.meta_data[sample_id] = meta_data

    def _add_new_lane_to_existing_sample(self, path: str, match: re.Match, sample_id: str) -> None:
        new_lane = self._get_new_lane(match, path)
        self.meta_data[sample_id]["lanes"].append(new_lane)

    def _get_new_lane(self, match: re.Match, path: str) -> dict:
        new_lane = {"path": path,
                    "lane": int(match.group("lane")),
                    "marker_forward": match.group("marker_forward"),
                    "marker_reverse": match.group("marker_reverse"),
                    "barcode": match.group("barcode")
                    }
        return new_lane

    def _output_meta_data(self) -> None:
        with open(self.o_json, "w") as o_file:
            output = list(self.meta_data.values())
            json.dump(output, o_file, indent=JSON_INDENT)

    def run(self):
        self._extract_meta_data()
        self._output_meta_data()
