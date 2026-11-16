# *Hysterothylacium* in nemits2 v0.2.4: curation screen (2026-11)

amphid's leave-out benchmark (`tests/bench_db_gap.py`, v0.2.4, 300 simulated nanopore samples, `nanopore_hac`) gave a much higher wrong rate for held-out species than on v0.2.0: 18.0% against 3.7%. The species held out differ between the two runs, so the two rates are not directly comparable. Of the 53 wrong species calls, 49 were *Hysterothylacium*:

| held out | named | calls | through record |
|---|---|---:|---|
| *H. sinense* | *H. liparis* | 31 | several |
| *H. aduncum* | *H. fabri* | 9 | ITS2_47cc30ea8d5d (MW370746) |
| *H. amoyense* | *H. zhoushanense* | 7 | ITS2_6f02e9c098be (MW413285) |
| *H. sinense* | *H. fabri* | 2 | ITS2_80278aa23724 (MW371005) |

Each call's gap was about 300 edits. That means the record named sat beside the held-out species and nowhere near any other species left in the database.

**Policy** (as in `curation_contained_pairs_2026-11.md`): `relabel` only for published synonyms, `drop` for likely misidentifications, `leave` for ITS2 genuinely shared between species.

**Evidence:**
- Distances: edits between records (`bin/build.py` `span_distance`) and from independent GenBank records to release records (`infix_distance`, the record placed inside the GenBank sequence).
- GenBank metadata (study, isolate, host), fetched 2026-11-16.

**Independent records.** Most of the release's *H. sinense* comes from one study. That is "Stock structure of the spinyhead croaker *Collichthys lucidus*" (Department of Fisheries Resources, unpublished; MW370539-MW371024): 130 of 131 *H. sinense* records, 36 of 54 *H. fabri*, 4 of 13 *H. liparis*. Records from four other studies were fetched for comparison. The nemabiome backbone lacks 72 of them, so they are not in the release:

| records | study | species |
|---|---|---|
| MH211528-MH211574 | Zhang et al. 2018, Int J Food Microbiol 284:105 | 20 *H. liparis*, 17 *H. sinense*, 9 *H. zhoushanense* (a tenth, MH211553, is in the release) |
| MF539797-MF539813 | Chen et al. 2018, Parasit Vectors 11:274 | 10 *H. sinense*, 5 *H. amoyense* (MF539807, MF539809 and the *H. zhoushanense* MF539814-15 are in the release) |
| KP335023-KP335032 | Du, Zhang & Li, unpublished (2014) | 10 *H. liparis* |
| KX817295 | Li et al. 2016, Int J Food Microbiol 241:108 | *H. sinense* |

## Findings

### 1. *H. sinense* and *H. liparis* share an ITS2

Every independent record of either species is 0 edits from the same release record, a croaker-study *H. sinense*, and 1 edit from the nearest *H. liparis* record. That holds for 28 *H. sinense* and 30 *H. liparis* from Li L.'s laboratory (which described both species). It also holds for PP029292 (*H. sinense*; Zhou & Xi, unpublished, 2023), from another laboratory and already in the release. Within the release, every *H. liparis* record is 0-2 edits from an *H. sinense* record.

So the ITS2 does not separate the two species. With both in the database, the gap rule stops at genus, which is right. The 31 benchmark calls are what any classifier would do with *H. sinense* held out. They do not show a database error. NCBI keeps the two as separate species, and no synonymy was found.

**Action: leave.** The benchmark could count this pair the way it counts contained pairs ("indistinguishable"). That is an amphid change.

### 2. One lineage under four names (croaker study)

There are 23 accessions (20 records) of a ~280-base ITS2. All are from the croaker study, and all lie within 10 edits of one another (single linkage):

- *H. fabri*: MW370892, MW370900, MW370905, MW370908, MW370915, MW370922, MW370928, MW370946, MW370962, MW370965, MW371005, MW371006, MW371015, MW371016
- *H. sinense*: MW370972, MW370990, MW371004, MW371012, MW371013, MW371023, MW371024
- *H. aduncum*: MW370896
- *H. thalassini*: MW370920

The lineage is 95 or more edits from every other *H. fabri* record, 104 or more from every other *H. sinense*, 83 or more from every other *H. aduncum* and 107 or more from every other *H. thalassini*. It is 68 or more from any other record in the release; the nearest is *Raphidascaris acus*. None of the four names fits it, and what it is remains unknown.

**Action: drop all 23 (strong).** This follows the precedent of MW370925 and MW370927, two earlier drops from the same study.

### 3. MW370746, "*H. fabri*" (croaker study, isolate CLXC_276)

It is 1 edit from independent *H. aduncum* records (AM503956, JF683733) and 47 from every *H. fabri* record. This is the record that named 9 held-out *H. aduncum* as *H. fabri*.

**Action: drop (strong).**

### 4. MW370885, "*H. sinense*" (croaker study)

It is 90 or more edits from every record in Raphidascarididae, including 94 from its nearest *H. sinense*, and its grade is unmeasured. Its identity is unknown.

**Action: drop (strong).**

### 5. MW413285, "*H. zhoushanense*" (Univ. Basra, unpublished; host *Nemipterus japonicus*)

It is 3 edits from *H. amoyense* (KT749422, MW423789, ON098280) and 10 from *H. zhoushanense*. Every independent *H. zhoushanense* record (MH211548-57, MF539814-15) matches a release *H. zhoushanense* record exactly and is 7-9 edits from *H. amoyense*. This record named 7 held-out *H. amoyense* as *H. zhoushanense*.

It is likely *H. amoyense*, or a form near it, but it is not identical to any *H. amoyense* record.

**Action: drop (medium).**

### Looked at and left

- MW370702 "*H. sinense*" is 37-38 edits from every *H. sinense* and *H. liparis* record. It is odd, but it is nearest its own name's group and names nothing wrongly.
- MW370924 "*H. fabri*" is 8 edits from other *H. fabri*, within the species' range.

## Expected effect

Rows 2-5 remove the records behind 18 of the 49 wrong calls: 9 + 7 + 2. The 31 *H. sinense* → *H. liparis* calls stay, as they should (point 1). This has not been rerun: it needs a rebuild.

## Follow-up (not proposed here)

Adding the 72 independent records above to `curation/genbank_named.tsv` would give *H. sinense*, *H. liparis*, *H. zhoushanense* and *H. amoyense* records beyond one unpublished study. They would not separate *H. sinense* from *H. liparis*.

## Follow-up: the croaker study's other outliers (2026-11-16)

Records 20 or more edits from their name's commonest record, checked by `span_distance` against every Raphidascarididae and Anisakidae record (development build of the 16 November update):

| accession | label | finding | action |
|---|---|---|---|
| MW370888 | *H. fabri* | identical to three *H. sinense* (KF601896, KP301509, MW370544), making their record genus-level "shared" | drop |
| MW370897 | *H. fabri* | identical to seven *H. aduncum* (AF115571, JQ934879-80, ...), the same effect | drop |
| MW370934 | *H. sinense* | identical to four *H. fabri*; the only *H. sinense* in that record (it stays shared through an *H. hainanense*) | drop |
| MW370898, MW370903 | *H. aduncum* | 1 edit from independent *H. fabri* (KF736943, JQ520158, PP029274), 40 from the nearest *H. aduncum* | drop |
| MW370702 | *H. sinense* | one accession; nothing of any name within 37 edits | drop |
| MW370546 | *H. sinense* | a partial (93%); 28 or more edits from everything | drop |
| MW370643, MW370569 | *H. sinense* | 12-16 edits from *H. sinense* and *H. liparis*; nearest its own group | leave |
| PX273803 | *H. fabri* | another study; 23 edits from its name, nearest it | leave |

The first three were inside records holding several names: they caused no wrong call, but held real *H. sinense* and *H. aduncum* records at genus. The drops above (sections 2-5) and these are in `curation/overrides.tsv`. The whole study (332 accessions) was not dropped: most of it agrees with independent records, and dropping it would have left one *H. sinense* record until the 72 independent ones are added (they predate the update's date window, so they go in `curation/genbank_named.tsv` for the next fetch).
