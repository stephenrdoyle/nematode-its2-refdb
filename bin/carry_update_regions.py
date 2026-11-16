#!/usr/bin/env python3
"""Carry the ITS2 regions of an earlier GenBank update into a later one.

    bin/carry_update_regions.py <earlier update dir> <later update dir> <out dir>

bin/genbank_update.py estimates each record's ITS2 region by aligning it
to a reference build, and bin/its2.py takes an update record only where
its cut falls at an anchor, a primer or the record's own end. A later
fetch estimated against a newer build moves some regions a few bases,
and records then flip in or out for no reason in the data (2026-11-16:
56 lost, 91 gained, against 68 records new in GenBank). This keeps the
later fetch's records (its taxonomy.txt, records.fasta.gz, log.txt:
what is in GenBank now) but, for every accession the earlier fetch also
holds, its earlier ITS2 region from seqs.fasta; only records new since
take the later estimate. Writes the same four files to <out dir>.
"""
import os
import shutil
import sys


def read_fasta(path):
    out, name = {}, None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith(">"):
            name = line[1:]
            out[name] = []
        elif name is not None:
            out[name].append(line)
    return {k: "".join(v) for k, v in out.items()}


def main() -> int:
    earlier, later, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    old = {h.split()[0].split(".")[0]: s for h, s in read_fasta(os.path.join(earlier, "seqs.fasta")).items()}
    new = read_fasta(os.path.join(later, "seqs.fasta"))
    carried = 0
    with open(os.path.join(out, "seqs.fasta"), "w") as fh:
        for h, s in new.items():
            acc = h.split()[0].split(".")[0]
            if acc in old:
                carried += s != old[acc]
                s = old[acc]
            fh.write(f">{h}\n{s}\n")
    for f in ("taxonomy.txt", "records.fasta.gz"):
        shutil.copyfile(os.path.join(later, f), os.path.join(out, f))
    log = open(os.path.join(later, "log.txt")).read()
    with open(os.path.join(out, "log.txt"), "w") as fh:
        fh.write(log.rstrip("\n") + "\n" + f"regions carried from {os.path.basename(earlier.rstrip('/'))}: "
                 f"{sum(1 for h in new if h.split()[0].split('.')[0] in old)} records "
                 f"({carried} with a different estimate); new since: "
                 f"{sum(1 for h in new if h.split()[0].split('.')[0] not in old)}\n")
    print(open(os.path.join(out, "log.txt")).read().rstrip("\n").split("\n")[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
