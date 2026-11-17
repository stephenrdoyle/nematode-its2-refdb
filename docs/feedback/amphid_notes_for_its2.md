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

## 4. `deepest_rank` and the gap rule: they agree (answered)

This point first said `deepest_rank` was stricter than the exact-match
clause, from 7 of 585 in-database species calls in the benchmark that
rested on a record `resolution_nanopore.tsv` stops at genus. That was
wrong in two ways:

- **All 7 records were tied (margin 0), not 2-3 edits off.** The run
  used v0.2.0, which has no `contained_in` / `contains`, so amphid
  could not yet stop contained pairs at genus (#18 needs v0.2.2+). Run
  again on v0.2.4, the same benchmark has 1 such call in 590. That one
  is an amphid matter: an *H. fabri* record lies inside a shared record
  (four *H. fabri* members, one *H. sinense*, one *H. hainanense*), and
  amphid reported no other species close. The table is right there.
- **`deepest_rank` is looser than the classifier, not stricter.** A
  record resolves to species at any margin of 1 or more ("distinct from
  every other species' record", §5.1); the classifier needs a gap of 4,
  or 2 for an exact match. That is by design, so the table is unchanged.

One real disagreement did turn up. The classifier's gap ignores unnamed
records (hybrids, cf., "s.l."), but the margins and resolution tables
counted them. 252 records took their whole-read margin from an unnamed
record. Recomputed without them, 228 margins change (222 upward), and 2
records tied at 0 come untied, which had stopped at genus:

- *Contracaecum rudolphii*, tied to "*C. rudolphii* A x *C. rudolphii*
  B"; its margin becomes 4 or more.
- *Anisakis pegreffii*, tied to "*A. simplex* s.l."; its margin becomes 1.

`bin/build.py` now leaves unnamed records out of the margins and the
window groups, as the classifier does (DESIGN §5). That takes effect in
the next release.

## 5. *Trichostrongylus retortaeformis* in sheep samples (answered)

The call stands. Every consensus named *T. retortaeformis* in S-BSST527
is an exact match to one of two records: ITS2_69d80da5ab27 or
ITS2_7939ce88afeb. That happens in five samples, HRG14-014, -125, -126
and -127 and HRG15-032, at 10-25 reads each. The nearest other species
is 3 edits off, *T. vitrinus*. ITS2_69d80da5ab27 holds three isolates
from lagomorphs, on two continents: KC521376 (hare) and KC521392
(hare), from a study of ovine nematodes in wild Australian lagomorphs
(Vet Parasitol 197:370, 2013), and PV439847 (*Lepus europaeus*,
2025). ITS2_7939ce88afeb holds JX046418 and KC521404 (rabbits, same
study). The records are sound and the gap is what the exact-match
clause allows: in the leave-out benchmark every exact match it named at
a 2-3 edit gap was right. A margin specific to this pair would have
nothing to rest on. No curation change.

The same records do something else in this dataset. They are the "next
species" that holds many *T. vitrinus* consensus at genus. Those
consensus sit 4 edits from their *T. vitrinus* record and 2 from
*T. retortaeformis*. That is the gap rule working as intended: such a
sequence is nearly as close to either species.

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

## 7. The leave-out benchmark on v0.2.5, and what counts as wrong

amphid's `tests/bench_db_gap.py` was rerun on v0.2.5. The settings were those of the v0.2.4 run: whole release, `nanopore_hac`, 300 samples, seed 2026, gap_exact 2. The held-out species are drawn from the release, so v0.2.5 held out a different set. amphid's `main` also moved between the runs: db90181 for v0.2.4, f4faf70 for v0.2.5.

From nf-amphid-pipeline #37, a held-out species' call counts as indistinguishable, not wrong, when the source record is fewer than 4 edits (the gap) from a typical record of the species named. A typical record is within the gap of another record of its own species, or is that species' only record. A record far from the rest of its species is taken as misidentified, and a call through it stays wrong. Before #37 only exact containment counted. Rescored from the same calls:

| species held out | wrong | indistinguishable |
|---|---|---|
| v0.2.4, exact containment | 18.0% | 0.0% |
| v0.2.4, within the gap | 8.0% | 10.0% |
| v0.2.5, exact containment | 19.0% | 0.7% |
| v0.2.5, within the gap | 5.7% | 14.0% |

- **v0.2.4's wrong calls** were mostly through MW370746 (8 calls) and MW413285 (7), both dropped in v0.2.5.
- **v0.2.5 *Hysterothylacium*:** held-out *H. amoyense* (13 sources) and *H. fabri* (21) get no wrong species calls. *H. aduncum* was not held out this time.
- **v0.2.5 remaining wrong calls (17):**
  - 7 *H. sinense* sources beyond the gap of every *H. liparis* record.
  - 7 through PV138334 (*H. urticae*: 1 edit from *H. cruciferae*, 5 from the other *H. urticae* record).
  - 3 single calls: *P. vulnus* → *P. penetrans*, one *H. elachista* → *H. oryzae*, *Heterorhabditis taysearae* → Steinernematidae.
- **v0.2.5 held-out genus:** one wrong call (0.3%), *Orloffia bisonis* → *Teladorsagia*. Before nf-amphid-pipeline #37's fix, the benchmark's pair listing put it among the held-out species.
- **v0.2.5 indistinguishable (42):**
  - *H. sinense* → *H. liparis*: 32.
  - *H. elachista* → *H. oryzae*: 7.
  - *Hemicriconemoides litchi* → *H. strictathecatus*: 2.
  - *P. panamaensis* → *P. gutierrezi*: 1.
- **Known limit:** a group of misidentified records passes as typical, since its records are close to each other. In v0.2.4 that was the short croaker lineage under "*H. fabri*" (2 calls), which v0.2.5 no longer has.

## 8. The leave-out benchmark on v0.2.6

The benchmark was rerun on v0.2.6 with the settings of section 7, on amphid `main` 571cbdc (nf-amphid-pipeline #37). v0.2.5's calls were rescored on the same code.

The held-out species are drawn from the release, and v0.2.6 has 10 fewer named species, so this run held out a different set: 59 species gave held-out sources, 20 of them also held out on v0.2.5. In particular, *H. sinense* was not held out this time. That species gave 39 of v0.2.5's 59 wrong or indistinguishable calls.

| species held out, within the gap | deepest | wrong | indistinguishable | higher | no consensus |
|---|---|---|---|---|---|
| v0.2.5 | 17.7% | 5.7% | 14.0% | 31.0% | 31.7% |
| v0.2.6 | 18.3% | 1.3% | 2.0% | 46.0% | 32.3% |

- Most of the drop comes from the different draw, not from the release. A paired comparison covers only the 20 species held out in both runs (136 sources on v0.2.5, 125 on v0.2.6): wrong 5.9% → 0.8%, indistinguishable 5.9% → 3.2%.
- In the records left in, species calls are 93.7% → 92.3% deepest (gap_exact 2), with no wrong calls.
- The held-out genus has one wrong call (0.3%), *Orloffia bisonis* → *Teladorsagia*, as on v0.2.5.

**PV138334.** Its 7 wrong calls are gone. Both species they came from were held out again:
- *H. cruciferae*: 2 wrong on v0.2.5, 5 at genus (the deepest allowed) on v0.2.6.
- *H. carotae*: 5 wrong of 8 on v0.2.5, 2 of 2 at genus on v0.2.6.

**Remaining wrong calls on held-out species (4).** Two of the named records sit apart from their own species and close to the source's species. They may be worth a look in the study screen:
- **2 *Parelaphostrongylus andersoni* → *P. tenuis*, both through AF504035.1.** It is labelled *P. tenuis* but is 4 edits from a *P. andersoni* record (its margin is 4, nearest ITS2_ada5f980b1b3). The other 4 *P. tenuis* records are 4, 5, 6 and 23 edits away. It is 6 edits from both held-out sources.
- **1 *Haemonchus longistipes* → *H. contortus*, through LC552171.1.** It is labelled *H. contortus* but is 6 or more edits from all 326 other *H. contortus* records and 4 from an *H. longistipes* record (the held-out source). A misidentified *H. longistipes* would explain it, but the benchmark cannot tell that from real variation.
- **1 *Heterodera elachista* → *H. oryzae*, through MT823206.1** (partial_90). It is contained in two *H. elachista* records, so it is a margin-0 tie, and 4 edits from the source. That is exactly at the gap, and the rule needs fewer than 4. The other 3 *H. elachista* calls to *H. oryzae* count as indistinguishable.

**Indistinguishable (6):**
- *H. elachista* → *H. oryzae*: 3.
- *Pratylenchus thornei* → *P. neglectus*: 2.
- *P. panamaensis* → *P. gutierrezi*: 1.

The run held out none of the species named in section 7's other open points: *H. aduncum*, *H. sinense*/*H. liparis* and *Meloidogyne graminis*/*M. marylandi*. They are untested on v0.2.6.
