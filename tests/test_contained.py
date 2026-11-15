"""bin/build.py's contained_pairs: a named record lying exactly inside a
named record of another species is flagged; one inside its own species,
or beside a shared or unnamed record, is not.

    python3 -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin"))
from build import contained_counts, contained_pairs  # noqa: E402

# The Contracaecum case of nf-amphid-pipeline's leave-out benchmark: an
# ogmorhini record two bases shorter than a rudolphii record, one base
# missing at each end.
LONG = "ACGTTGCAAGTCCATGGCTAGCTTAGCGATCGGATCCTTAGGCATGCAATCGTAGGCTTACGATCGA"
SHORT = LONG[1:-1]


def rec(species, genus, status="named", grade="complete"):
    return {"species": species, "genus": genus, "species_status": status, "grade": grade}


class ContainedPairs(unittest.TestCase):
    def test_other_species_inside(self):
        seqs = {"long": LONG, "short": SHORT}
        tax = {"long": rec("Contracaecum rudolphii", "Contracaecum"),
               "short": rec("Contracaecum ogmorhini", "Contracaecum", grade="near_complete")}
        self.assertEqual(contained_pairs(seqs, tax), [("short", "long")])

    def test_missing_one_end_only(self):
        seqs = {"long": LONG, "short": LONG[:-5]}
        tax = {"long": rec("A b", "A"), "short": rec("A c", "A")}
        self.assertEqual(contained_pairs(seqs, tax), [("short", "long")])

    def test_same_species_not_flagged(self):
        seqs = {"long": LONG, "short": SHORT}
        tax = {"long": rec("A b", "A"), "short": rec("A b", "A")}
        self.assertEqual(contained_pairs(seqs, tax), [])

    def test_one_edit_not_flagged(self):
        mid = len(SHORT) // 2
        short = SHORT[:mid] + ("A" if SHORT[mid] != "A" else "C") + SHORT[mid + 1:]
        seqs = {"long": LONG, "short": short}
        tax = {"long": rec("A b", "A"), "short": rec("A c", "A")}
        self.assertEqual(contained_pairs(seqs, tax), [])

    def test_shared_and_unnamed_not_flagged(self):
        seqs = {"long": LONG, "short": SHORT, "short2": LONG[2:]}
        tax = {"long": rec("A b", "A"), "short": rec("", "A", status="shared"),
               "short2": rec("", "A", status="unnamed")}
        self.assertEqual(contained_pairs(seqs, tax), [])

    def test_counts(self):
        seqs = {"long": LONG, "short": SHORT, "mid": LONG[:-1], "far": LONG[3:]}
        tax = {"long": rec("A b", "A"), "short": rec("A c", "A", grade="partial_90"),
               "mid": rec("A d", "A"), "far": rec("B e", "B")}
        pairs = contained_pairs(seqs, tax)
        # short lies in long and in mid, mid in long, far (another genus,
        # which keeps the last base mid lacks) in long only
        self.assertEqual(pairs, [("far", "long"), ("mid", "long"),
                                 ("short", "long"), ("short", "mid")])
        self.assertEqual(contained_counts(pairs, tax),
                         {"record_pairs": 4, "species_pairs": 4, "records": 4,
                          "pairs_with_partial": 2, "cross_genus_pairs": 1})


if __name__ == "__main__":
    unittest.main()
