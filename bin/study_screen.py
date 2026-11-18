#!/usr/bin/env python3
"""Submissions whose records of a species disagree with everyone else's.

    bin/study_screen.py <build dir> [--workers N] > <out.tsv>

bin/species_coherence.py judges one record at a time. A single study
that labels many records wrongly (v0.2.4's Collichthys lucidus study:
one ITS2 lineage under four Hysterothylacium names, other species' ITS2
under H. fabri and H. sinense) shows there as scattered calls, and
where the study holds most of a species' records it can look like the
species itself. This screen groups accessions into submissions and
checks each submission's records of a species against the records of
that species from every other submission.

A submission is a run of accessions with one prefix whose numbers lie
within --gap of each other (GenBank numbers a submission's sequences
consecutively); every source record in members.tsv (dropped ones too)
is used to find the runs, so a study's records of other species keep
its run together. Only kept, named accessions are judged.

For each accession of species S in submission B, in record r:
  ind    edits from r to the nearest record holding an S accession from
         another submission (0 if r holds one itself); bin/build.py's
         span_distance
  other  edits from r to the nearest record of another species
         (species_margins.tsv, read whole; 0 if r is shared with another
         species, or r is another species' record). A short partial is
         near many records over the few bases it has (a 150-base
         Cylicostephanus goldi partial lies 2-4 edits from most
         cyathostomins), so where the nearest is shorter than
         --min-span of r's length, other is measured afresh against the
         family's records of other species at least that long
  supported   ind <= 3
  conflict    ind >= 10 and other < ind (nearer another species than any
              independent record of its own), or ind >= 20 (far from
              every independent record)

A (species, submission) is listed when it has >= --min accessions of S
and at least one conflict, with `call`:

  mislabel  >= 3 conflicts within 3 edits of another species, making
            >= 20% of its accessions of S: the submission holds another
            species' ITS2 under this name
  lineage   >= 3 conflicts making >= 20%, mostly far from everything: its
            S and the other submissions' S differ - a cryptic lineage, or
            one side misidentified; `ind_acc` and `ind_subs` say how much
            independent support the other side has
  records   fewer: single records to look at as the coherence screen's

Species with no second submission cannot be checked here and are only
counted (stderr). Records from genome assemblies and long reads (a
layer) belong to no submission and are not judged.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import read_fasta, span_distance  # noqa: E402

_S = None


def _init(seqs):
    global _S
    _S = seqs


def _nearest(job):
    key, i, others = job
    return key, i, min((span_distance(_S[i], _S[j]), j) for j in others)


ACC = re.compile(r"^([A-Z]+)(\d+)$")


def submissions(accessions, gap):
    """accession -> submission label (first-last of its run)."""
    by = collections.defaultdict(list)
    for a in accessions:
        m = ACC.match(a)
        if m:
            by[m.group(1)].append((int(m.group(2)), a))
    out = {}
    for pre, xs in by.items():
        xs.sort()
        run = [xs[0]]
        for x in xs[1:] + [None]:
            if x is not None and x[0] - run[-1][0] <= gap:
                run.append(x)
                continue
            label = run[0][1] if len(run) == 1 else f"{run[0][1]}-{run[-1][1]}"
            for _, a in run:
                out[a] = label
            if x is not None:
                run = [x]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--gap", type=int, default=20, help="largest step in accession number within a submission")
    ap.add_argument("--min", type=int, default=3, help="fewest accessions of a species for a submission to be listed")
    ap.add_argument("--min-span", type=float, default=0.75,
                    help="shortest another species' record may be, as a share of r's length, to count for other")
    a = ap.parse_args()

    seqs = read_fasta(os.path.join(a.build, "refdb.fasta"))
    tax = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.build, "taxonomy.tsv")), delimiter="\t")}
    marg = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.build, "species_margins.tsv")), delimiter="\t")}
    rows = list(csv.DictReader(open(os.path.join(a.build, "members.tsv")), delimiter="\t"))
    base = lambda acc: acc.split(".")[0]
    sub = submissions({base(r["accession"]) for r in rows}, a.gap)

    # Kept, named accessions: species -> [(accession, submission, record)]
    acc_of = collections.defaultdict(list)
    for r in rows:
        if r["role"] == "dropped" or not r["id"]:
            continue
        sp = r["label"].split(";")[-1]
        if len(sp.split()) < 2 or " sp." in sp or " x " in sp or base(r["accession"]) not in sub:
            continue
        if tax[r["id"]]["genus"] != sp.split()[0]:
            continue
        acc_of[sp].append((base(r["accession"]), sub[base(r["accession"])], r["id"]))

    by_family = collections.defaultdict(list)
    for i, t in tax.items():
        if t["species"]:
            by_family[t["family"]].append(i)
    reshort = {}

    def other(rid, sp):
        t = tax[rid]
        if t["species_status"] == "shared" or (t["species"] and t["species"] != sp):
            return 0, rid
        m = marg.get(rid)
        if not m or m["margin_whole"] in ("", "NA"):
            return None, ""
        near = m["nearest_whole"]
        if near not in seqs or len(seqs[near]) >= a.min_span * len(seqs[rid]):
            return int(m["margin_whole"]), near
        if rid not in reshort:
            pool = [j for j in by_family[t["family"]] if tax[j]["species"] != sp
                    and len(seqs[j]) >= a.min_span * len(seqs[rid])]
            reshort[rid] = min(((span_distance(seqs[rid], seqs[j]), j) for j in pool), default=(None, ""))
        return reshort[rid]

    jobs, single = [], 0
    for sp, xs in acc_of.items():
        subs = {s for _, s, _ in xs}
        if len(subs) < 2:
            single += 1
            continue
        for s in subs:
            mine = [x for x in xs if x[1] == s]
            if len(mine) < a.min:
                continue
            ind = {rid for _, t, rid in xs if t != s}
            for rid in {rid for _, _, rid in mine} - ind:
                jobs.append(((sp, s), rid, sorted(ind)))
    with Pool(a.workers, initializer=_init, initargs=(seqs,)) as pool:
        dist = {(k, i): d for k, i, d in pool.imap_unordered(_nearest, jobs, chunksize=4)}

    w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    w.writerow(["call", "species", "submission", "n_acc", "species_acc", "share", "ind_acc", "ind_subs",
                "supported", "conflict", "near_other", "conflict_accessions"])
    out = []
    for sp, xs in acc_of.items():
        for s in sorted({x[1] for x in xs}):
            mine = [x for x in xs if x[1] == s]
            if len(mine) < a.min or len({x[1] for x in xs}) < 2:
                continue
            sup, con, n_near = 0, [], 0
            for acc, _, rid in mine:
                d, near = dist.get(((sp, s), rid), (0, rid))
                o, onear = other(rid, sp)
                if d <= 3:
                    sup += 1
                if (d >= 10 and o is not None and o < d) or d >= 20:
                    n_near += o is not None and o <= 3 and o < d
                    other_sp = (tax[onear]["species"] or tax[onear]["genus"] + " (shared)") if onear in tax else ""
                    con.append(f"{acc}:ind={d},other={o if o is not None else 'NA'}{' ' + other_sp if other_sp else ''}")
            if not con:
                continue
            big = len(con) >= 3 and len(con) >= 0.2 * len(mine)
            call = "records" if not big else "mislabel" if n_near >= 3 and n_near >= 0.2 * len(mine) else "lineage"
            ind_subs = len({x[1] for x in xs} - {s})
            out.append((["mislabel", "lineage", "records"].index(call), -len(con),
                        [call, sp, s, len(mine), len(xs), f"{len(mine) / len(xs):.2f}", len(xs) - len(mine), ind_subs,
                         sup, len(con), n_near, "; ".join(con)]))
    for *_, row in sorted(out, key=lambda x: x[:2]):
        w.writerow(row)
    print(f"species checked: {sum(1 for xs in acc_of.values() if len({x[1] for x in xs}) > 1)}; "
          f"with one submission only (not checkable): {single}; jobs {len(jobs)}; "
          f"other re-measured past a short partial: {len(reshort)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
