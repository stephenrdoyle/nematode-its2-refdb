# Notes from amphid: what using the database has shown

From nf-amphid-pipeline (amphid) database mode, 2026-11-16. The
counterpart of [its2_notes_for_amphid.md](its2_notes_for_amphid.md):
that file says what amphid needs from the database, and this one says
what amphid's runs and benchmarks have shown about the database. Pull
requests are stephenrdoyle/nf-amphid-pipeline unless named otherwise.
Each point says whether it asks anything of the database. Most do not.

## 1. S-BSST527: results depend slightly on the index, not only the names

amphid's `main` (a4bbbcb, after #29) was run on S-BSST527 (PacBio RSII
CCS, four pools, 443,433 reads) against v0.2.2 and v0.2.4. DADA2's ASVs
were classified with `classify_asvs.py` against the same releases.

| S-BSST527 | v0.2.2 | v0.2.4 | DADA2 (either) |
|---|---|---|---|
| clustered reads named to species, tiered (gap) | 98.44% (97.79%) | 98.31% (97.41%) | 99.32% (99.28%) |
| *Haemonchus* at genus, study-wide, paper filter | 0.91% | 1.01% | 0.00% |
| per-sample Bray-Curtis against DADA2, median | 0.0047 | 0.0061 | |
| reads naming another species than the nearest ASV | 5 | 5 | |

On v0.2.2, `main` reproduces the run recorded in amphid's
`docs/CONTRACTS.md` exactly: all 2,621 consensus sequences are the same,
with the same calls.

**Why v0.2.4 differs.** No consensus sequence present in both runs
changes its call. DADA2's own classification does not move either. v0.2.4
drops 9 records, none of them sheep parasites: *Pseudoterranova
decipiens* ×4, *Hysterothylacium amoyense* and *H. fabri*, *Globodera
millefolii*, *Ditylenchus dipsaci*, *Rugopharynx alpha*. It leaves the
406 *Haemonchus* records untouched. Yet 475 consensus sequences (15,347
reads, mostly *H. contortus*) are built differently.

The likely mechanism has not been confirmed read by read. amphid groups
reads by their primary database hit before it builds consensus
sequences. *H. contortus* has 329 records, many near-identical, and a
small change to the minimap2 index changes which of them a noisy read's
primary hit lands on. That changes which reads are grouped together,
and so which consensus sequences are built.

**For the database:** nothing is wrong with v0.2.4. The point is that
amphid's results can shift by about 0.1-0.4 points between releases for
reasons unrelated to the taxa in a sample. That is worth knowing when
comparing a dataset across releases. amphid may group by species, or by
a within-species cluster, rather than by record. If the release ever
shipped a record → within-species cluster map (records within N edits of
each other), amphid could group on it directly. That is a suggestion,
not a request.

## 2. Contained pairs: used, and they behave as intended

v0.2.2's `contained_in` / `contains` (nematode-its2-refdb #4, with the
cross-genus curation in #6) are used by amphid since #18. Two checks:

- **With both species in the database, the gap rule stops every
  contained pair at genus.** This was checked on all 147 within-genus
  record pairs in v0.2.0, including those whose length difference
  exceeds amphid's 5-base tie slack.
- **The leave-out benchmark separates them out.** In amphid's
  `tests/bench_db_gap.py` (point 3), a held-out species named after a
  sister it contains exactly is counted as indistinguishable, not wrong.
  On the whole release that was 1.3% of held-out-species sources (3.7%
  wrong besides). There were none in the strongylid families.

A cap on amphid's calls at each record's `deepest_rank` from
`resolution_nanopore.tsv` was considered and rejected (point 4).

## 3. The exact-match clause (GAP_EXACT) on nanopore consensus

amphid took `its2_classify.py`'s exact-match clause in #17: an exact
match is a species when the next species is ≥2 edits off. The release's
leave-one-out scored reference sequences. A nanopore consensus carries
residual errors, so amphid measured the clause on simulated nanopore
reads: `tests/bench_db_gap.py`, v0.2.0, 300 samples per run, `--gap-exact`
2 and 0 on the same reads.

| sources | in database: species, 0 → 2 | species held out: wrong | genus held out: wrong |
|---|---|---|---|
| whole release, nanopore_hac | 82.0% → 90.8% | 3.7% (+1.3% indistinguishable), unchanged | 0.3%, unchanged |
| strongylid families, nanopore_hac | 93.3% → 97.2% | 5.7%, unchanged | 2.3%, unchanged |
| strongylid families, nanopore_sup | 93.5% → 97.3% | 5.7%, unchanged | 2.3%, unchanged |

Every call the clause changed was an in-database species named to the
right species instead of genus. No held-out species or genus was called
differently. The benchmark takes any span-scored release
(`--release`, `--families`, `--error-model`). It could be run as a
release check alongside the leave-one-out, if useful.

## 4. `deepest_rank` is stricter than the gap rule in places

In the benchmark's whole-release run, 7 of 585 species calls on
in-database sources rested on a record that `resolution_nanopore.tsv`
says resolves only to genus. All 7 calls were right; in the strongylid
run it was 4. Most are exact matches at a 2-3 edit gap, which GAP_EXACT
names and the resolution table, by its margin, does not. Capping
amphid's calls at `deepest_rank` would have removed 10 wrong calls on
held-out species but lost these correct ones, so amphid does not cap.

**For the database:** if `deepest_rank` is meant to say what a read of
that record can be named, it could take the exact-match clause into
account, so the table and the classifier agree. As it stands, amphid
reports `deepest_rank` beside the call (`db_resolution`) but does not
use it.

## 5. *Trichostrongylus retortaeformis* in a sheep sample

Under the exact-match clause, S-BSST527 sample HRG14-014 gets 30 of
2,101 reads named *T. retortaeformis*. The consensus is an exact match
to the release's *T. retortaeformis* records (ASV00141/ASV00123 in the
DADA2 run), 3 edits from *T. vitrinus*. `classify_asvs.py` names the same
sequences *T. retortaeformis* too, so the two classifiers agree. The
paper did not report it.

It is usually a lagomorph parasite, so the call deserves a look. The 11
records behind the name, mostly the KC5213xx series, look well
supported.

**For the database:** only a question. Is a 3-edit gap to *T. vitrinus*
enough to name this pair? If there is reason to think not, a
pair-specific note or margin would let both classifiers stop at genus
here.

## 6. Nanopore NC1/NC2 data: none public that we could find

No public Oxford Nanopore dataset of NC1/NC2 ITS2 amplicons was found,
in ENA or the literature, for amphid to test against. Two leads:

- **Charrier, Chen, Redman, Ammar, Meira, Queiroz & Gilleard** (Calgary;
  bioRxiv doi:10.64898/2025.12.04.692384, now in Int J Parasitol). They
  sequenced sheep L1 pools from 77 flocks by MinION alongside Illumina,
  using NC5/NC2 and new EC1/EC2 primers, not NC1. No read deposit was
  found.
- **Williams et al. 2024**, *Animal* 18:101156 (Aberystwyth). MinION
  nemabiomes of 34 ewes; the primers and any deposit are unknown
  (subscription-only).

Until one turns up, amphid's nanopore evidence for ITS2 is the
simulation in point 3.
