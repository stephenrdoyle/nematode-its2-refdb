"""bin/build.py's margins: an unnamed record (hybrid, cf., "s.l.") is never
the nearest other species, as in the classifier's gap; a shared record is.

    python3 -m unittest discover tests
"""

import os
import random
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin"))
from build import margins  # noqa: E402

rng = random.Random(1)
BASE = "".join(rng.choice("ACGT") for _ in range(240))


def edit(s, *pos):
    s = list(s)
    for p in pos:
        s[p] = "A" if s[p] != "A" else "C"
    return "".join(s)


def rec(species, status="named"):
    return {"species": species, "species_status": status,
            "deepest_rank": "species" if species else "genus"}


@unittest.skipUnless(shutil.which("minimap2"), "needs minimap2")
class Margins(unittest.TestCase):
    def nearest(self, seqs, tax):
        with tempfile.TemporaryDirectory() as d:
            fa = os.path.join(d, "refdb.fasta")
            with open(fa, "w") as fh:
                fh.writelines(f">{i}\n{s}\n" for i, s in seqs.items())
            m = margins(fa, seqs, tax, [], 1)
        return m["rud"][1], m["rud"][2]

    # The v0.2.4 case: C. rudolphii identical to a "C. rudolphii A x
    # C. rudolphii B" record, 3 edits from another species.
    def test_unnamed_not_another_species(self):
        seqs = {"rud": BASE, "hyb": BASE, "ogm": edit(BASE, 50, 120, 200)}
        tax = {"rud": rec("Contracaecum rudolphii"), "hyb": rec("", "unnamed"),
               "ogm": rec("Contracaecum ogmorhini")}
        self.assertEqual(self.nearest(seqs, tax), ("3", "ogm"))

    def test_shared_is_another_species(self):
        seqs = {"rud": BASE, "shr": edit(BASE, 50), "ogm": edit(BASE, 50, 120, 200)}
        tax = {"rud": rec("Contracaecum rudolphii"), "shr": rec("", "shared"),
               "ogm": rec("Contracaecum ogmorhini")}
        self.assertEqual(self.nearest(seqs, tax), ("1", "shr"))


if __name__ == "__main__":
    unittest.main()
