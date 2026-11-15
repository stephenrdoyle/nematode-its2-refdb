# nematode-its2-refdb

Builds a curated nematode ITS2 reference database for NC1/NC2
"nemabiome" metabarcoding, read on Illumina (2x150, 2x250) and
nanopore. It starts from the nemabiome ITS2 database and adds GenBank
records published since, informal "Genus sp." lineages, and ITS2 copies
from genome assemblies; each record is re-cut to the span the reads
cover, graded by how much of it it holds, and screened, with mislabelled
records dropped or relabelled (`curation/`). It writes taxonomy,
resolution tables and the adapter look-alike mask. It is an independent
derivative, not a product of the nemabiome project; see
[Citation](#citation). It is the ITS2
counterpart of [vespa-18s-refdb](https://github.com/stephenrdoyle/vespa-18s-refdb),
writes the same release format, and is consumed by
[amphid](https://github.com/stephenrdoyle/nf-amphid-pipeline).

**Status: v0.2.3 (2026-11-15).** v0.1.0 was the first release. See
[docs/DESIGN.md](docs/DESIGN.md) for the design and the measurements
behind it, and [docs/feedback/its2_notes_for_amphid.md](docs/feedback/its2_notes_for_amphid.md)
for what amphid needs to change to use it. DADA2 and IdTaxa users: see
[For DADA2 and IdTaxa users](#for-dada2-and-idtaxa-users).

## Download and verify

```bash
V=v0.2.3
curl -LO https://github.com/stephenrdoyle/nematode-its2-refdb/releases/download/$V/nemits2_$V.tar.gz
shasum -a 256 nemits2_$V.tar.gz
# 89f99f4fa17513dffdb22800053cbf2b734cec2251cc115a63d8104ed4e0e692
tar -xzf nemits2_$V.tar.gz
```

Each file's sha256 is in `nemits2_<version>/manifest.json`; the manifest
and summary of every release are also committed under `releases/`.

## What a record is

NC1 sits at the 3' end of 5.8S, NC2 in 28S. A record runs from the end
of NC1 to the start of the ~47-base 28S stretch before NC2 - the ITS2,
cut at fixed anchors rather than where the source database's HMM put
its boundaries. Reads carry the 28S stretch too; amphid scores a read
over its reference's span only, so it counts neither for nor against.

Most GenBank ITS2 records do not run primer to primer. Each record's
`grade` says how much of the ITS2 it holds, judged against its closest
record anchored at both ends: `complete`, `near_complete` (>= 98%),
`partial_90`, `partial_75`, `partial`, or `unmeasured` (no relative at
>= 80% identity).

## v0.2.3

12,048 records and 1,869 named species (425 genera), from the same
sources as v0.2.2: curation of the contained pairs that crossed a genus,
and relabels now traceable to their GenBank names. The release format is
v0.2.2's; `members.tsv` notes carry more, and `manifest.json` counts
relabels (`counts.relabelled`).

- **Relabels are recorded in `members.tsv`.** A source record relabelled
  in `curation/overrides.tsv` now notes the name its source record
  carries ("relabelled (curation/overrides.tsv): source name
  *Cooperia spatulata*", and NCBI's current name where that differs), so
  an accession followed to GenBank can be read beside its new label.
  Before, only `curation/overrides.tsv` recorded it. `manifest.json`
  counts them (`counts.relabelled`: 49; 45 before this release's
  curation).
- **Curation: the five contained pairs that crossed a genus**
  (`curation/overrides.tsv`). Synonyms relabelled: *Paratylenchus
  paralatescens* (OR354384) as *Gracilacus paralatescens*, as its
  other three records; *Oscheius microvilli* (NCBI: *Caenorhabditis
  microvilli*; KT825914, MN932153, OM004005) as *O. myriophilus*, a
  proposed junior synonym whose ITS2 it shares. Misidentified records
  dropped, not relabelled, so no accession carries a name GenBank does
  not: six *Pseudoterranova decipiens* larvae from cod and redfish
  (MG272333-7, KT852550) with the *Phocanema bulbosa* ITS2, and the only
  *Rugopharynx alpha* (LN906946), which is *Papillostrongylus barbatus*'s.
  *Aphelenchoides oryzae* inside *A. besseyi* stays: a valid species of
  the *A. besseyi* complex whose ITS2 overlaps it. Against v0.2.2:
  12,048 records (12,053), 1,869 named species (1,872); 146 contained
  pairs, none across a genus (151, 5); 9 records named to species read
  whole and through every window that stopped at family; five
  `closer` records in the coherence screen gone, none new.
- **Leave-one-out** (3,223 queries, 1,228 species): gap rule 58.2%
  species recall, 99.3% precision, 5.2% over-classification read whole
  (v0.2.2: 57.9%, 99.3%, 5.5%).

## Earlier releases

### v0.2.2

12,053 records and 1,872 named species, the same records as v0.2.1:
every build file but `taxonomy.tsv`, `manifest.json` and `summary.txt` is
byte-identical to v0.2.1's, and so is the DADA2 reference FASTA.
Margins, resolution and leave-one-out are unchanged.

- **Contained records flagged** (docs/DESIGN.md §5). A named record
  whose ITS2 lies exactly inside a named record of another species (the
  same sequence, a few bases shorter at one or both ends) is kept and
  flagged: two new `taxonomy.tsv` columns, `contained_in` and
  `contains`, list the other-species records, and `manifest.json` →
  `counts` → `contained` counts them. Such records were already tied
  (margin 0, stopped at the rank the two share); now a consumer can see
  which records they are tied with. On v0.2.0's inputs: 152 record
  pairs, 58 species pairs, 187 records; 147 pairs within a genus, 5
  across genera (synonyms or mislabels). In v0.2.2: 151, 57 and 185;
  the one strongylid pair within a genus, *Spiculopteragia spiculoptera*
  inside *S. boehmi*, went with v0.2.1's relabel. None in the livestock
  strongylid genera (cyathostomins, *Haemonchus*, *Teladorsagia*,
  *Trichostrongylus*, *Cooperia*, *Oesophagostomum* and the rest).
- Tests: `python3 -m unittest discover tests`.

### v0.2.1

12,053 records and 1,872 named species, from the same sources as
v0.2.0. The release format is v0.2.0's plus a third Illumina geometry:
`resolution_illumina_300x300.tsv` (MiSeq v3, windows 280 + 233), a
`margin_280x233` column in `species_margins.tsv`, and its entry in
`manifest.json` → `illumina_geometries`. The only change to records is
the *Spiculopteragia* relabel below.

- **Joining and read lengths.** Hybrid joining (merged where a pair
  overlaps, concatenated where not) is the rule at every read length:
  tested at 2x150 (four sets: same calls as concatenation) and 2x300
  (German cattle and camels, Ehnert et al. 2025 and Brachmann et al.
  2025; roe deer, Beaumelle et al. 2022: 2-8% more reads than merging,
  same species shares, and the published communities reproduced).
- **`bin/classify_asvs.py`:** a concatenated pair whose read 1 already
  reaches 28S is scored whole on read 1 (at 2x300, camels 96.6% ->
  99.6% of reads to species with hybrid joining).
- **PacBio:** `bin/trim_primers.py --platform pacbio`, a `single` mode
  in `bin/dada2_nemabiome.R` and `PLATFORM=pacbio` in
  `bin/real_data.sh`; demultiplex with `lima`. Swedish sheep
  (S-BSST527): 99.3% of reads to species.
- **Curation:** *Spiculopteragia boehmi* relabelled *S. spiculoptera*
  (one species under two names); roe deer *S. spiculoptera* reads now
  reach species.

### v0.2.0

12,053 records and 1,873 named species (439 genera) from 18,023 source
records: the nemabiome backbone (15,107), 2,668 GenBank records it
lacks (from `sources/genbank_update_20261113`, fetched 2026-11-13,
whose 5,897 records holding an ITS2 include 3,894 informal "Genus sp."
records; those cut at no anchor or identical to a named record are left
out), and 248 ITS2 copies from 48 genome assemblies and 10 long-read
sets. The first release under the name nematode-its2-refdb (until
v0.1.4, nemabiome-its2-refdb): it is a curated derivative of the
nemabiome ITS2 database, not a copy. The release format is unchanged
from v0.1.4: the same files and columns, `lineage` now also carrying the
informal name of 737 genus-level records and two *Necator* types.

Sixteen more genome assemblies scanned for ITS2 (`curation/long_read_sources.tsv`;
docs/DESIGN.md §5.5): 74 copies of 15 species, 49 of them new records
(*Dirofilaria immitis*, *Acanthocheilonema viteae*, *Dictyocaulus
viviparus*, *Trichuris trichiura*, *Thelazia callipaeda* and others).
The genomes settle two curation questions (`curation/overrides.tsv`):

- **The only *Trichostrongylus capricola* record, JF276023, is dropped.**
  It is 1 edit from 692 of the 766 ITS2 copies of the
  *T. colubriformis* genome GCA_963978875, inside that species' own
  spread. *T. colubriformis* reads it held at genus are now named:
  5.8% of the ruminant mock's reads (gap rule 90.8% -> 96.9% to
  species), 2,052 Francis & Šlapeta reads (goats 87.2% -> 88.6%).
- **Eight Sri Lankan "*D. repens*" records are *D. asiatica***
  (ON332065-71, PV643877): 1-3 edits from the *D. asiatica* genome,
  14-21 from the *D. repens* genome.

Leave-one-out (3,230 queries): present species named 57.3% (gap rule) /
68.2% (tiered), as in v0.1.4; over-classification 5.4% / 9.0%, from
5.5% / 9.3%. The mocks still name no wrong species
(`results/`, docs/DESIGN.md §6).

***Metastrongylus* curation** (docs/DESIGN.md §8.18;
`curation/genbank_named.tsv`, `curation/overrides.tsv`). Most records
are SSCP bands of Conole et al. (2001, Estonian wild boar), whose ITS2
varies chiefly in microsatellites. *M. pudendotectus* is one species
(records up to 78 edits apart plain are 2-11 apart with repeats
collapsed, and repeat-aware scoring names it); *M. salmi* is not: three
tight types, A and C 21-34 edits apart, about as far as A is from
*M. apri*. Type C is the sequence Humbert & Henry (1997) deposited as
*M. asymmetricus*, so it stays tied with that species at genus. Type B
(AJ305395/400/403) is type A lacking a 44-base block every other record
carries, most likely a gel-band artefact, and is dropped. Added by hand:
the rest of the Conole bands, *M. apri* from Denmark, Viet Nam and
Brazil, and 14 Brazilian wild boar *M. salmi* (OR660330-50, unpublished),
a further type 17-27 edits from every other record.

**Informal "Genus sp." records** (docs/DESIGN.md §5.7). Some lineages
are known only by an informal name, such as the gorilla hookworm
"*Necator* sp." of Hasegawa et al. The GenBank update now takes every
nematode ITS2 record named "Genus sp. X"; the build gives each its genus
only (`species_status` `unnamed`, the name in `lineage`) and drops it
where a named record's ITS2 is identical to, inside or contains it, or
where its genus disagrees with its ITS2 (a named record of another
genus >= 97% identical and closer than any of its own genus: 86 records,
mostly *Raphidascaris* and *Terranova* inside *Hysterothylacium* and
*Euterranova*). The classifier scores reads against named records
first and uses informal ones only where that call stops above genus, so
they add genus calls and never change one. 737 are kept. Leave-one-out:
missing species reach the right genus 23.5% of the time (from 19.3%),
wrong genus unchanged at 1.2%. Real data: no species call changes;
gorilla *Necator* (18-21% of Cameroon ape reads) and kangaroo
*Macropostrongylus* (0.6-0.7% of PRJNA1524548) reach genus instead of
unassigned.

**Hasegawa *Necator* types** (`curation/lineages.tsv`). The informal
*Necator* records of Hasegawa et al. (2014, 2017) carry their rDNA type
as the lineage: type II (types II and II', 1-3 edits apart; 28 records,
among them all the untyped "*Necator* sp. HH-2015" records, 0-4 edits
from type II) and type III (19-20 edits from type II); type I is
*N. americanus*. Gorilla, chimpanzee and human *Necator* reads in
Cameroon (PRJEB64582) that stop at genus are type II.

**Curation since v0.1.4** (`curation/overrides.tsv`): MF784940, an
"*Uncinaria* sp." carrying the *H. contortus* ITS2, and PZ362967, a
*Meloidogyne graminicola* 63 edits from every other record of its
species (the v0.2.0 species coherence screen), are dropped. Records
dropped by an override now keep their own source in `members.tsv`.

**Tools.** `bin/trim_primers.py` turns pairs sequenced in both
orientations, cuts read-through and accepts primers clipped at the 5'
end, each only where a pair needs it (`--strict` restores the old
trims), and takes reads deposited without primers (`--pretrimmed`).
`bin/real_data_report.py` pages show "Unplaced ITS2" (aligns, but no
family within range) apart from "Not ITS2-like" (nothing aligns:
primer dimers, chimeras, off-target), and can count by sample.

### v0.1.4

11,288 records and 1,874 named species (427 genera) from 16,051 source
records: the nemabiome backbone plus 733 GenBank records it lacks
(`bin/genbank_update.py`: ITS2 records published since the backbone's
17 March 2026 snapshot, 5.8S/28S records holding an ITS2, and 98
accessions listed by hand in `curation/genbank_named.tsv`). Update
records are taken only where `bin/its2.py` cut them at an anchor or
their own end; 1,057 were not. New species include *Heligmosomoides
bibullosus*, *Metastrongylus asymmetricus* and *M. confusus*.

- **Informal names are not species.** "sp."/"spp." names (*Oesophagostomum*
  sp. 3335_MDR_CAM_OH15, *Cloacina* sp. 1 AJ-2019, 19 records) are
  genus-level, unnamed records; the informal name is in the `lineage`
  column (`curation/lineages.tsv`).
- **Species coherence screen** (`bin/species_coherence.py`,
  `results/curation/species_coherence.tsv`): records far from their own
  species and next to another. 65 more drops and 2 relabels
  (`curation/overrides.tsv`, `docs/curation_pass_2026-11-11.md` F-H),
  among them *Ashworthius sidemi* OP787564 (an *H. contortus* ITS2) and
  24 West African "*H. contortus*" carrying the *H. placei* ITS2.
- **Cuts:** an NC1 well inside a cut is taken as the start (5.8S and
  ITS1 no longer ride along), and a record ending in a short 28S stub is
  cut at it (a complete *Oesophagostomum radiatum*, PZ347037, is now in).
- **Repeat-aware scoring** (`bin/its2_classify.py`): a read that differs
  from a reference only in how many units a simple repeat has is one edit
  off, not one per base. Goat *Oe. venulosum* reads with a long (AT)n
  stopped at family; they are now named (docs/DESIGN.md §6).
- **A tentative tier** (`tiered_rank`, `tiered_name`, `tentative` in
  `bin/classify_asvs.py`'s output): species at >= 98% with the next
  species >= 4 edits off, flagged, beside the gap rule's confident call.
- `bin/dada2_nemabiome.R` takes `TRUNCLEN="F,R"` for a fixed truncation
  (tested; it cost species calls, so the default stays off).

### v0.1.3 and before

v0.1.3 adds a `lineage` column to `taxonomy.tsv` (the *Teladorsagia
circumcincta* goat line, `curation/lineages.tsv`); records and calls are
as in v0.1.2.

11,135 records from 15,282 source records: 15,108 nemabiome sequences
(version 20260317; 54 dropped and 33 relabelled,
`curation/overrides.tsv`) and 174 ITS2 copies from long-read genome
assemblies and HiFi reads (`curation/long_read_its2.tsv`, which adds six
species: *Loa loa*, *Acanthocheilonema viteae*, *Litomosoides
sigmodontis*, *Spirocerca lupi*, *Trichuris incognita*, *Heligmosomoides
bakeri*). Names follow current NCBI Taxonomy
(`curation/ncbi_names.tsv`; 64 source records renamed). 1,125 partial
records are folded into a full-length record of the same species that
holds them, and 749 weak records (partial or unmeasured, one accession)
into a record of their species within 1 edit. 426 genera, 1,836 species
with a record of their own.

Changes from v0.1.1 (11,146 records): the 2026-11-11 curation pass
(`docs/curation_pass_2026-11-11.md`). 27 relabels fold minor male morphs
into their species (*Cooperia surnabada* and *C. spatulata*,
*Marshallagia occidentalis*, *Teladorsagia davtiani*, *Ostertagia
arctica*); 26 drops remove records that sit next to another species
while the rest of their own sits far off, and shared ITS2s typical of
only one of their names. Leave-one-out species recall rises from 53.4%
to 55.3% and over-classification falls from 6.4% to 5.9%; *Cooperia*
reads are now named to species. v0.1.1 changed from v0.1.0 (11,956
records): weak records folded (issue #2), 36 records deposited
reverse-complemented turned and re-cut, primer and 28S remnants trimmed,
and margins and resolution tables computed against every candidate
(issue #1).

<!-- figures:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/grade_dark.svg">
  <img alt="Bar chart: records per nematode group in nemits2_v0.2.3, by how much of the ITS2 they hold: I · animal parasites 446 (complete 49, near complete 186, partial 59, unmeasured 152); I · plant parasites 167 (complete 0, near complete 0, partial 0, unmeasured 167); I · free-living 16 (complete 2, near complete 2, partial 0, unmeasured 12); II · plant parasites 56 (complete 0, near complete 0, partial 0, unmeasured 56); II · free-living 19 (complete 1, near complete 0, partial 0, unmeasured 18); III · animal parasites 2,141 (complete 857, near complete 695, partial 367, unmeasured 222); IV · animal parasites 784 (complete 178, near complete 244, partial 140, unmeasured 222); IV · plant parasites 4,353 (complete 2,311, near complete 914, partial 509, unmeasured 619); IV · free-living 50 (complete 18, near complete 9, partial 8, unmeasured 15); V · animal parasites 3,628 (complete 1,175, near complete 1,469, partial 713, unmeasured 271); V · free-living 370 (complete 246, near complete 50, partial 36, unmeasured 38); Other Chromadoria · free-living 16 (complete 0, near complete 0, partial 0, unmeasured 16); Family not placed 2 (complete 2, near complete 0, partial 0, unmeasured 0)." src="docs/figures/grade_light.svg" width="760">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/taxa_dark.svg">
  <img alt="Bar chart: records per nematode group in nemits2_v0.2.3, and how many resolve to species read whole: I · animal parasites 446 (365 to species); I · plant parasites 167 (167 to species); I · free-living 16 (16 to species); II · plant parasites 56 (56 to species); II · free-living 19 (19 to species); III · animal parasites 2,141 (1,923 to species); IV · animal parasites 784 (691 to species); IV · plant parasites 4,353 (3,985 to species); IV · free-living 50 (42 to species); V · animal parasites 3,628 (3,341 to species); V · free-living 370 (296 to species); Other Chromadoria · free-living 16 (14 to species); Family not placed 2 (0 to species)." src="docs/figures/taxa_light.svg" width="760">
</picture>

How many species nemits2_v0.2.3 can name. A species named in the source records but with no record of its own shares its ITS2 with another species (or sits inside another species' record over its span), so a read from it is named only to genus or above. Names are counted as written.

| Records | Species named in sources | Species with their own record (read whole) | Species named through Illumina 150x150 | Species named through Illumina 250x250 | Species named through Illumina 300x300 | Genera |
|---|---:|---:|---:|---:|---:|---:|
| All records | 2,435 | 1,846 | 1,840 | 1,846 | 1,846 | 439 |
| **I · animal parasites** | 94 | 33 | 33 | 33 | 33 | 6 |
| I · plant parasites | 65 | 65 | 64 | 65 | 65 | 3 |
| I · free-living | 10 | 10 | 10 | 10 | 10 | 9 |
| II · plant parasites | 18 | 18 | 18 | 18 | 18 | 2 |
| II · free-living | 9 | 9 | 9 | 9 | 9 | 6 |
| **III · animal parasites** | 397 | 291 | 286 | 291 | 291 | 104 |
| **IV · animal parasites** | 225 | 149 | 149 | 149 | 149 | 13 |
| IV · plant parasites | 806 | 646 | 646 | 646 | 646 | 94 |
| IV · free-living | 29 | 21 | 21 | 21 | 21 | 13 |
| **V · animal parasites** | 620 | 501 | 501 | 501 | 501 | 161 |
| V · free-living | 157 | 102 | 102 | 102 | 102 | 25 |
| Other Chromadoria · free-living | 2 | 1 | 1 | 1 | 1 | 2 |
| Family not placed | 3 | 0 | 0 | 0 | 0 | 1 |

How far a record can be named in nemits2_v0.2.3, best case (an exact read, no sequencing error): the share of records resolving to species, and to genus at best.

| Records | Nanopore (whole ITS2): species | genus | Illumina 150x150: species | genus | Illumina 250x250: species | genus | Illumina 300x300: species | genus |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All records (12,048) | 91% | 9% | 89% | 11% | 91% | 9% | 91% | 9% |
| **I · animal parasites** (446) | 82% | 18% | 76% | 24% | 81% | 19% | 82% | 18% |
| I · plant parasites (167) | 100% | 0% | 99% | 1% | 100% | 0% | 100% | 0% |
| I · free-living (16) | 100% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| II · plant parasites (56) | 100% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| II · free-living (19) | 100% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| **III · animal parasites** (2,141) | 90% | 10% | 86% | 14% | 90% | 10% | 90% | 10% |
| **IV · animal parasites** (784) | 88% | 12% | 88% | 12% | 88% | 12% | 88% | 12% |
| IV · plant parasites (4,353) | 92% | 8% | 91% | 9% | 92% | 8% | 92% | 8% |
| IV · free-living (50) | 84% | 16% | 84% | 16% | 84% | 16% | 84% | 16% |
| **V · animal parasites** (3,628) | 92% | 8% | 91% | 9% | 92% | 8% | 92% | 8% |
| V · free-living (370) | 80% | 20% | 80% | 20% | 80% | 20% | 80% | 20% |
| Other Chromadoria · free-living (16) | 88% | 12% | 88% | 12% | 88% | 12% | 88% | 12% |
| Family not placed (2) | 0% | 50% | 0% | 50% | 0% | 50% | 0% | 50% |
<!-- figures:end -->

The figures and tables above are generated from the build by
`bin/readme_figures.py`, alt text included; rerun it after a build to
refresh them in place:

```bash
python3 bin/readme_figures.py work/build docs/figures README.md
```

Groups are the nematode clades of Blaxter et al. (1998), split by
lifestyle. Insect parasites (*Steinernema*, *Heterorhabditis*) count as
animal parasites; fungal feeders (*Aphelenchoides*, *Bursaphelenchus*)
count as plant parasites. A record whose span sits exactly inside
another species' record is tied with it and stops at the rank they share;
`taxonomy.tsv`'s `contained_in` and `contains` name the other record.

Most species-level records are close to another species: 712 at one
edit, 542 at two, 278 tied (`species_margins.tsv`, read whole), over a median ITS2 of
240 bases. At that length amphid's 99.7% species limit allows no
mismatch at all.

## How well reads are named

Tested two ways (docs/DESIGN.md §6): leave-one-out on the database
itself, and two livestock datasets (one published) run through the standard
nemabiome DADA2 workflow.

Leave-one-out figures are for v0.2.3, the datasets' for v0.2.1. Since v0.1.0 the classifier
also scores every candidate (issue #1) and scores read windows strictly
(docs/DESIGN.md §6).

**Leave-one-out** (3,223 records of 1,228 species, read whole; 2x150 is
within 3 points). *Present*: only the query's own record removed.
*Missing*: every record of the query's species removed, so any species
named is wrong. Recall = right calls / reads; precision = right calls /
calls made at that rank; over-classification = species named for a
missing species (`results/leave_one_out/metrics.txt`).

| Classifier, this database | Species recall | Species precision | Genus recall | Genus precision | Over-classification |
|---|---:|---:|---:|---:|---:|
| `bin/classify_asvs.py`, gap rule | 58.2% | **99.3%** | 90.0% | 99.6% | **5.2%** |
| `bin/classify_asvs.py`, tiered (gap + tentative) | 69.3% | 99.0% | 90.0% | 99.6% | 8.8% |
| DECIPHER IdTaxa (threshold 60) | 79.5% | 97.6% | 94.3% | **99.7%** | 19.2% |
| dada2 assignTaxonomy (minBoot 80) | **86.6%** | 95.7% | **97.8%** | 99.4% | 38.1% |

The gap rule names a species only when the read is >= 99% identical to
it and every other species is >= 4 edits further off, or the match is
exact and every other species is >= 2 edits off; otherwise it stops at
genus (>= 97%) or family (>= 95%). It is the most conservative of the
three: it names fewest species but is wrong least, which matters most in
samples with species missing from the database (wildlife, new hosts). At
genus all three are about 99% precise; they differ in how often they
name a species that is not there. Differences in a simple repeat's
length count as one edit when finding the best match, but not when
measuring the gap to the next species.

The tiered rule also names, as *tentative*, a species the read is
>= 98% identical to with every other species >= 4 edits off: reads
1-2% from their own species (the *Teladorsagia circumcincta* goat line,
*Oe. venulosum*), but also reads of a missing sister species. Read
tentative calls as species where the hosts' worms are well sampled
(livestock), as genus where they may not be (wildlife).
Tuning the rule per genus or family did not help on held-out species
(`results/leave_one_out/group_rules.txt`). Each call carries `nearest`
(the best species and its identity) and `next` (the nearest other
species and how many edits further), so a genus call still says how
close it came: *Trichostrongylus*; nearest *T. rugatus* 99.6%;
next *T. retortaeformis* +2.

**Real data** (share of reads named to species; all arms named the same
species wherever two of them named one). Four NC1/NC2 sets: two from
the Šlapeta group, one published, from livestock and Australian
wildlife; humans and great apes in Cameroon (deposited without
primers); and zoo antelopes (2x150 only, both orientations ligated).
2x250 pairs joined hybrid (merged where they overlap, concatenated where
they do not), and cut to 2x150:

| Dataset | assignTaxonomy x nemabiome | IdTaxa x nemabiome | assignTaxonomy x this db | IdTaxa x this db | gap rule x this db | tiered x this db |
|---|---:|---:|---:|---:|---:|---:|
| Francis & Šlapeta, cattle, goats, sheep, PRJNA936713, 2x250 | 72.0% | 81.7% | 99.5% | 99.7% | 95.7% | 99.4% |
| same, cut to 2x150 | 76.0% | 88.2% | 99.1% | 92.4%* | 95.2% | 98.5% |
| Šlapeta group, unpublished, PRJNA1524548, cattle, kangaroos, pigs, rabbits, 2x250 | 70.4% | 69.7% | 95.1% | 93.7% | 94.3% | 98.3% |
| same, cut to 2x150 | 73.7% | 65.9% | 94.9% | 96.9% | 94.7% | 98.3% |
| Ilík et al., humans, chimpanzees, gorillas, Cameroon, PRJEB64582, 2x250 | 99.1%† | 62.8% | 73.3% | 62.2% | 62.8% | 62.8% |
| same, cut to 2x150 | 99.0%† | 85.9% | 78.5% | 61.9% | 59.8% | 59.8% |
| zoo antelopes, PRJNA1137257, 2x150 | 12.6% | 62.6% | 67.2% | 68.2% | 60.3% | 69.7% |

\* IdTaxa sits on its threshold for the main *H. placei* ASV (6.5% of
reads): retrained, it names it or leaves it at genus. Set a seed and
report it.
† assignTaxonomy on the nemabiome backbone names the gorilla hookworm
(Hasegawa type II, 45 edits from *N. americanus*) as *N. americanus*;
this database leaves it at genus *Necator*. Cameroon's ape
trichostrongyloid (a *Paralibyostrongylus*, 79-92% to anything named)
has no record in either.

assignTaxonomy and IdTaxa compare k-mers over the whole ASV, so with
this database the ASVs' 28S stretch must be cut off first
(`bin/trim_28s.py`); the columns for this database are on cut ASVs.
Merging only, as the standard workflow does, loses the ITS2 too long
for a 2x250 pair to overlap: two of the four PRJNA1524548 pig libraries kept
6 and 665 reads merged and 22,932 and 19,801 hybrid, all *Metastrongylus
apri* (see For DADA2 and IdTaxa users). Half the PRJNA1524548 libraries have
read 2 starting inside 28S, without NC2; `bin/trim_primers.py` keeps
them. `results/dada2_comparison/` holds each arm's summary, the per-ASV
calls, the merged and concatenated runs, and an HTML report per set
(docs/DESIGN.md §6.2).

**Simulated mocks** (Jesudoss Chelladurai et al. 2025; canine, equine,
ruminant, all species present, so they measure recall, not
over-classification): no classifier, with either database, named a
wrong species for an exact copy of a source sequence (precision 100%);
the k-mer classifiers named 88-100% of reads to species, the gap rule
91-100%, stopping at genus where a sister species is 1 edit off; the
tiered rule named no wrong species either.
The mocks' truth includes two backbone mislabels this database corrects
(docs/DESIGN.md §6.3; `results/mocks/`).

## For DADA2 and IdTaxa users

The release carries the database in the formats of the nemabiome.ca
DADA2 workflow, to use in place of nemabiome's own files:

| file | use |
|---|---|
| `nemits2_<version>_dada2.fasta` | `assignTaxonomy` reference |
| `nemits2_<version>_idtaxa.RData` | `load()` it for `trainingSet`, then `IdTaxa` |
| `trim_28s.R` | **required**: cut the 28S stretch off ASVs before classifying |

Records here stop where the ~47-base 28S stretch before NC2 starts; your
ASVs end in it. assignTaxonomy and IdTaxa compare k-mers over the whole
ASV, so uncut ASVs lose most species calls (one livestock set: 45% of
reads to species uncut, 99.3% cut).

Join pairs hybrid rather than by merging alone, at every read length. `mergePairs`
needs 12 bases of overlap; after primer trimming (about 230 + 230
bases) an ITS2 over about 400 bases never merges, and those pairs are
silently dropped: *Metastrongylus* (413-422 bases), Trichuridae,
Metastrongylidae, Onchocercidae and others. Keep the merged pairs and
concatenate only the rest:

```r
mm <- mergePairs(dadaF, derepF, dadaR, derepR, returnRejects = TRUE)
cc <- mergePairs(dadaF, derepF, dadaR, derepR, justConcatenate = TRUE)
hybrid <- mapply(function(m, c) {
  acc <- m[m$accept, ]
  rest <- !paste(c$forward, c$reverse) %in% paste(acc$forward, acc$reverse)
  rbind(acc[, c("sequence", "abundance")], c[rest, c("sequence", "abundance")])
}, mm, cc, SIMPLIFY = FALSE)
seqtab <- makeSequenceTable(hybrid)
```

(for one sample, `mm` and `cc` are data frames rather than lists: wrap
them in `list()`; `bin/dada2_nemabiome.R` does this as its `hybrid`
mode). At 2x150 almost no strongylid pair overlaps and hybrid is
concatenation; at 2x300 nearly every pair merges and hybrid keeps the
2-8% that fail on mismatches; tested on four 2x150 and three 2x300 sets
(docs/DESIGN.md §6.2). PacBio reads are single and whole: demultiplex
with `lima`, then `bin/trim_primers.py --platform pacbio` and
`bin/dada2_nemabiome.R` mode `single` (`bin/real_data.sh` with
`PLATFORM=pacbio`). After `removeBimeraDenovo`:

```r
source("trim_28s.R")
seqs <- getSequences(seqtab.nochim)
cut  <- trim_28s(seqs)
ok   <- nchar(gsub("N", "", cut)) >= 100      # shorter is not ITS2

taxa <- assignTaxonomy(cut[ok], "nemits2_<version>_dada2.fasta", minBoot = 80)
rownames(taxa) <- seqs[ok]                      # back to your ASVs

load("nemits2_<version>_idtaxa.RData")          # trainingSet
ids <- IdTaxa(DNAStringSet(cut[ok]), trainingSet, strand = "both", threshold = 60)
```

Concatenated ASVs (2x150, or the unmerged part of a hybrid join) are
cut in their reverse part. Set a seed and report it: IdTaxa's calls are
random draws, and ASVs near its threshold change between runs - in one
cattle set, *Haemonchus placei* ASVs holding 10-23% of reads sat at
confidence 62-76 and switched between species and genus with the seed.

Which classifier to use is a trade-off (docs/DESIGN.md §6.2): k-mer
classifiers name the most species when every species is in the
database; when some may be missing, they name a wrong one far more often
than the span-scored gap rule (`bin/classify_asvs.py`). Its tiered rule
sits between them: 98-99% of reads named on both livestock sets, with
less than half IdTaxa's over-classification.

## Build

```bash
S=sources/nemabiome_its2_20260317/Nematode_ITS2_20260317
python3 bin/nemabiome_export.py sources/nemabiome_its2_20260317/raw/database.xlsx $S
python3 bin/fetch_backbone_records.py ${S}_taxonomy_nr.txt sources/genbank_backbone/records.fasta.gz
# GenBank records the backbone lacks, merged with it (the last release is the reference)
U=sources/genbank_update_20261113
python3 bin/genbank_update.py ${S}_taxonomy_nr.txt releases/nemits2_v0.1.3 2026/03/17 $U curation/genbank_named.tsv
python3 bin/genbank_update.py merge $S sources/genbank_backbone/records.fasta.gz $U work/its2
python3 bin/its2.py work/its2/seqs.fasta work/its2/records.fasta.gz work/its2/its2_cut
python3 bin/informal_accessions.py work/its2/taxonomy.txt > work/its2/informal.txt   # never a partial's relative
python3 bin/its2_partials.py work/its2/its2_cut work/its2/its2_refs 8 work/its2/informal.txt
python3 bin/ncbi_names.py ${S}_taxonomy_nr.txt curation/ncbi_names.tsv   # current NCBI names; refetch before a release
python3 bin/build.py work/its2/its2 work/its2/taxonomy.txt nemabiome_20260317 work/build --workers 8 \
    --layer curation/long_read_its2.tsv --lineages curation/lineages.tsv
python3 bin/species_coherence.py work/build > work/build/species_coherence.tsv   # screen before a release
bin/export_kmer.sh work/build work/build/kmer nemits2_dev   # DADA2 / IdTaxa files (R, dada2, DECIPHER)
```

To cut a release, from committed code: build with `--version vX.Y.Z` into
a fresh directory, then `bin/release.py <build dir> releases vX.Y.Z`. It
adds the DADA2 / IdTaxa files, re-checksums, and writes
`releases/nemits2_vX.Y.Z/` and its tarball; it refuses a build from
uncommitted code and never overwrites a release.

The long-read layer is committed. To remake it, scan each assembly or
read set listed in `curation/long_read_sources.tsv` with
`bin/its2_scan.py scan`, then
`bin/genome_layer.py curation/long_read_sources.tsv ${S}_taxonomy_nr.txt curation/long_read_its2.tsv`.

Testing: `python3 -m unittest discover tests` (build rules),
`bin/its2_leave_one_out.py` (gap rule), `bin/loo_dada2.py`
(assignTaxonomy or IdTaxa on the same queries), `bin/loo_group_rules.py`;
`bin/real_data.sh` for real data (`bin/trim_primers.py`,
`bin/dada2_nemabiome.R`, `bin/trim_28s.py`, `bin/assign_taxonomy.R`,
`bin/idtaxa.R`, `bin/classify_asvs.py`, `bin/compare_arms.py`, then
`bin/real_data_report.py` for the HTML report); `bin/mock_arms.sh` and
`bin/score_mocks.py` for the mocks. These need R with dada2 and DECIPHER.

Needs Python 3.9+ and minimap2. `sources/README.md` says where each
download comes from.

## Release files

| file | holds |
|---|---|
| `refdb.fasta` | one record per unique ITS2 |
| `taxonomy.tsv` | superkingdom ... species, deepest rank, members, grade, coverage, sources, lineage (a published line within a species; blank for nearly all), contained_in / contains (named records of another species holding this ITS2 exactly, or held by it) |
| `members.tsv` | every source record, its grade, bases trimmed at each end, and a note: why it was dropped or folded, its name before an NCBI rename, or, if relabelled in `curation/overrides.tsv`, the name its source record (GenBank) carries |
| `conflicts.tsv` | records whose members disagree at order or above |
| `primer_fit.tsv` | NC1/NC2 edits of each record's best member, where its source record holds the sites |
| `resolution_nanopore.tsv`, `resolution_illumina_<R>x<R>.tsv` | deepest rank read whole or through the two read windows, grade, margin |
| `species_margins.tsv` | edits to the nearest record of another species, over the shorter record's span |
| `anchor_lookalikes.tsv` | adapter-anchor near-copies, for amphid's pre-flight mask |
| `manifest.json`, `summary.txt` | versions, primers, windows, counts, checksums |
| `nemits2_<version>_dada2.fasta`, `nemits2_<version>_idtaxa.RData`, `trim_28s.R` | for the DADA2 workflow (above) |

## Citation

The backbone is the nemabiome ITS2 database (Workentine et al. 2020,
BMC Genetics 21:74; https://www.nemabiome.ca), CC BY 4.0. Primers:
Gasser et al. 1993, Nucleic Acids Res 21:2525; method: Avramenko et al.
2015, PLoS ONE 10:e0143559.

MIT licence for the code (LICENSE).
