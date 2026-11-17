#!/usr/bin/env python3
"""Records that may not be ITS2, or not ITS2 alone.

    bin/not_its2.py <build dir> <its2_cut.tsv> [--since <release dir>] [--workers N] > <out.tsv>

Run it on every build that takes in new sequences (a GenBank update,
new curation sources): with --since the previous release, the `new`
column marks records holding an accession that release did not, so the
intake can be reviewed first (--only-new lists just those).

bin/its2.py re-cuts each record at fixed anchors, but where a GenBank
record holds no flank (it starts and ends where the backbone's ITS2
does: "record") or the anchor search fails ("hmm"), the cut is the
nemabiome backbone's, as markerDB's HMM placed it, and nothing checks
it. v0.2.5 holds records whose sequence is ITS1 or another stretch of
the rDNA (Ostertagia ostertagi KR779996-8: 552-602 bases against the
species' 241, matching no O. ostertagi ITS2 anywhere). This screen
gathers, for every record:

  start, end   how its members were cut (bin/its2.py's its2_cut.tsv);
               anchored if any member's start (end) was found by primer
               or anchor, not taken from the record's end or the HMM
  fit          primer_fit.tsv: NC1 / NC2 edits of its best member
  primer sites inside the cut, either strand (seqmatch.find_anchor_cost):
    nc1_at     NC1 (<= 2 edits) more than 40 bases in: the cut starts
               upstream, in 5.8S or ITS1
    s28_at     the 28S stretch (<= 5 edits) or NC2 (<= 2) more than 20
               bases in and more than 20 before the end: the cut runs on
               into 28S
    reversed   NC1 or NC2 (<= 2) or the 28S stretch (<= 5) found
               reverse-complemented
    its1       the 18S end / ITS1 start (GGAAGGATCATTA, exact)
  Sites count only in records not anchored at both ends: in a record
  cut at a primer or anchor at each end, a match is a look-alike.
  len_ratio    length / median length of its species' complete and
               near-complete records (else its genus')
  family_ident identity to the nearest complete or near-complete record
               of its family (1 - span edits / shorter length); computed
               for unmeasured records and records anchored at neither end

Calls (one per record, first that applies):
  its1        the 18S end / ITS1 start is in it: not ITS2, or not only
  reversed    a primer site reverse-complemented: wrong strand or chimera
  not_its2    anchored at neither end, family_ident < 0.6, and len_ratio
              outside 0.6-1.5: no sign of ITS2
  miscut      a primer site inside the cut: ITS2 with 5.8S/ITS1 or 28S
              attached
  check       anchored at neither end and family_ident < 0.75, or
              len_ratio outside 0.6-1.5 with family_ident < 0.75
Records without a call are not written. Layer records (genome
assemblies, long reads) are cut by bin/its2_scan.py and not judged.
"""
from __future__ import annotations

import argparse
import collections
import csv
import multiprocessing as mp
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import read_fasta, span_distance  # noqa: E402
from its2 import NC1, NC2, S28  # noqa: E402
from seqmatch import find_anchor_cost, revcomp  # noqa: E402

ITS1_START = "GGAAGGATCATTA"
ANCHORED = {"primer", "loose", "tight"}

_S = None


def _ident(job):
    rid, pool = job
    if not pool:
        return rid, None, ""
    d, j = min((span_distance(_S[rid], _S[o]), o) for o in pool)
    return rid, 1 - d / min(len(_S[rid]), len(_S[j])), j


def sites(x):
    """Primer and anchor sites inside the cut x."""
    out = {}
    n = len(x)
    m = find_anchor_cost(x, NC1, 2)
    if m and m[1] > 40:
        out["nc1_at"] = m[1]
    for pat, k in ((S28, 5), (NC2, 2)):
        m = find_anchor_cost(x, pat, k)
        if m and 20 < m[0] < n - 20 and "s28_at" not in out:
            out["s28_at"] = m[0]
    for pat, k in ((NC1, 2), (NC2, 2), (S28, 5)):
        if find_anchor_cost(x, revcomp(pat), k):
            out["reversed"] = 1
    if ITS1_START in x or revcomp(ITS1_START) in x:
        out["its1"] = 1
    return out


def main() -> int:
    global _S
    ap = argparse.ArgumentParser()
    ap.add_argument("build")
    ap.add_argument("cut", help="bin/its2.py's its2_cut.tsv for the build's inputs")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--since", help="previous release (or build) dir: mark records with accessions new since it")
    ap.add_argument("--only-new", action="store_true", help="write only records marked new (needs --since)")
    ap.add_argument("--ident", help="cache of family identities (TSV): read if present, else written")
    a = ap.parse_args()

    seqs = read_fasta(os.path.join(a.build, "refdb.fasta"))
    tax = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.build, "taxonomy.tsv")), delimiter="\t")}
    fit = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.build, "primer_fit.tsv")), delimiter="\t")}
    cut = {r["accession"]: r for r in csv.DictReader(open(a.cut), delimiter="\t")}
    how = collections.defaultdict(lambda: [set(), set(), 0])
    for r in csv.DictReader(open(os.path.join(a.build, "members.tsv")), delimiter="\t"):
        if r["id"] and r["role"] != "dropped":
            c = cut.get(r["accession"].split(".")[0])
            h = how[r["id"]]
            h[2] += 1
            if c:
                h[0].add(c["start"])
                h[1].add(c["end"])

    old = set()
    if a.since:
        old = {r["accession"].split(".")[0] for r in
               csv.DictReader(open(os.path.join(a.since, "members.tsv")), delimiter="\t")}
    new_acc = collections.defaultdict(int)
    for r in csv.DictReader(open(os.path.join(a.build, "members.tsv")), delimiter="\t"):
        if a.since and r["id"] and r["role"] != "dropped" and r["accession"].split(".")[0] not in old:
            new_acc[r["id"]] += 1

    full = [r for r in tax if tax[r]["grade"] in ("complete", "near_complete")]
    lens = collections.defaultdict(list)
    for r in full:
        lens[("s", tax[r]["species"])].append(len(seqs[r]))
        lens[("g", tax[r]["genus"])].append(len(seqs[r]))
    by_family = collections.defaultdict(list)
    for r in full:
        by_family[tax[r]["family"]].append(r)

    def layer(r):
        return not how[r][0] and not how[r][1]

    def anchored(r):
        return bool(how[r][0] & ANCHORED), bool(how[r][1] & ANCHORED)

    jobs = []
    for r in tax:
        if layer(r):
            continue
        st, en = anchored(r)
        if tax[r]["grade"] == "unmeasured" or not (st or en):
            jobs.append((r, [o for o in by_family[tax[r]["family"]] if o != r]))
    _S = seqs
    if a.ident and os.path.exists(a.ident):
        ident = {r: (None if i == "" else float(i), j) for r, i, j in csv.reader(open(a.ident), delimiter="\t")}
    else:
        with mp.get_context("fork").Pool(a.workers) as pool:
            ident = {r: (i, j) for r, i, j in pool.imap_unordered(_ident, jobs, chunksize=8)}
        if a.ident:
            with open(a.ident, "w") as fh:
                fh.writelines(f"{r}\t{'' if i is None else i}\t{j}\n" for r, (i, j) in ident.items())

    w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    w.writerow(["call", "id", "species", "length", "len_ratio", "grade", "members", "start", "end", "fit",
                "nc1_edits", "nc2_edits", "nc1_at", "s28_at", "reversed", "its1", "family_ident", "nearest", "new"])
    calls = collections.Counter()
    for r in tax:
        if layer(r):
            continue
        t = tax[r]
        x = seqs[r]
        st, en = anchored(r)
        s = {} if st and en else sites(x)
        ref = lens.get(("s", t["species"])) or lens.get(("g", t["genus"]))
        ratio = len(x) / statistics.median(ref) if ref else None
        odd_len = ratio is not None and not 0.6 <= ratio <= 1.5
        fi, near = ident.get(r, (None, ""))
        low = lambda v: fi is not None and fi < v
        if "its1" in s:
            call = "its1"
        elif "reversed" in s:
            call = "reversed"
        elif not (st or en) and low(0.6) and odd_len:
            call = "not_its2"
        elif "nc1_at" in s or "s28_at" in s:
            call = "miscut"
        elif (not (st or en) and low(0.75)) or (odd_len and low(0.75)):
            call = "check"
        else:
            continue
        if a.only_new and not new_acc[r]:
            continue
        calls[call] += 1
        f = fit.get(r, {})
        w.writerow([call, r, t["species"] or t["genus"] + " (genus)", len(x), "" if ratio is None else f"{ratio:.2f}",
                    t["grade"], how[r][2], ",".join(sorted(how[r][0])), ",".join(sorted(how[r][1])), f.get("fit", ""),
                    f.get("nc1_edits", ""), f.get("nc2_edits", ""), s.get("nc1_at", ""), s.get("s28_at", ""),
                    s.get("reversed", ""), s.get("its1", ""), "" if fi is None else f"{fi:.2f}",
                    (tax[near]["species"] or tax[near]["genus"]) if near else "", new_acc[r] or ""])
    print("calls: " + ", ".join(f"{k} {v}" for k, v in calls.most_common()) + f"; identity jobs {len(jobs)}"
          + (f"; records with accessions new since {a.since}: {len(new_acc)}" if a.since else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
