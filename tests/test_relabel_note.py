"""bin/build.py's relabel_note: a relabelled record's members.tsv note
names its source record's name, and NCBI's where that differs.

    python3 -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin"))
from build import relabel_note  # noqa: E402

TOP = ["Eukaryota", "Metazoa", "Nematoda", "Chromadorea", "Rhabditida"]


class RelabelNote(unittest.TestCase):
    def test_source_name(self):
        src = TOP + ["Tylenchulidae", "Paratylenchus", "Paratylenchus paralatescens"]
        self.assertEqual(relabel_note(src, src),
                         "relabelled (curation/overrides.tsv): source name Paratylenchus paralatescens")

    def test_ncbi_name_too(self):
        src = TOP + ["Rhabditidae", "Oscheius", "Oscheius microvilli"]
        ncbi = TOP + ["Rhabditidae", "Caenorhabditis", "Caenorhabditis microvilli"]
        self.assertEqual(relabel_note(src, ncbi),
                         "relabelled (curation/overrides.tsv): source name Oscheius microvilli, "
                         "NCBI name Caenorhabditis microvilli")

    def test_genus_level(self):
        src = TOP + ["Strongylidae", "Cloacina", ""]
        self.assertEqual(relabel_note(src, src),
                         "relabelled (curation/overrides.tsv): source name Cloacina")


if __name__ == "__main__":
    unittest.main()
