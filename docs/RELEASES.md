# Earlier releases

Release notes for nemits2 releases before the current one, newest first.
The current release is described in the [README](../README.md); each
release's manifest and summary are under `releases/`.

## v0.2.4

12,044 records and 1,866 named species (425 genera), from the same
sources as v0.2.3: curation of the contained pairs within a genus. The
release format is v0.2.3's. Against v0.2.3: 12,048 records, 1,869 named
species; 131 contained pairs in 46 species pairs (146, 53); 17 more
records named to species read whole and 18 more through 2x150 windows;
`counts.relabelled` 97 (49).

Curation of the within-genus contained pairs (`docs/curation_contained_pairs_2026-11.md`):
- *Globodera achilleae* (AY599498) relabelled *G. millefolii*, its senior synonym (Subbotin et al. 2011); identical to *G. millefolii* from the type host and region.
- *Heterorhabditis sonorensis* (14 accessions) relabelled *H. taysearae*, its senior synonym (Dhakal et al. 2021).
- *Hoplolaimus stephanus* (33 accessions) relabelled *H. galeatus*, its senior synonym (Subbotin et al. 2025).
- *Ditylenchus dipsaci* MG384729 dropped: it carries the *D. weischeri* ITS2 and is 13 edits from every other *D. dipsaci* record.
- *Hysterothylacium amoyense* MW370925 dropped: it carries the *H. fabri* ITS2 and is 97 edits from every other *H. amoyense* record.
- *Hysterothylacium fabri* MW370927 dropped: it carries the *H. thalassini* ITS2 and is 104 edits from every other *H. fabri* record.
- In the coherence screen, six fewer `closer` calls and four fewer
  `displaced`; one new `closer`: the merged *G. millefolii* record, with
  AF161004 (*G. millefolii*) 43 edits off it, left for a later look.
- **Leave-one-out** (3,220 queries, 1,226 species), read whole: tiered
  rule (the default) 69.7% species recall, 99.0% precision, 8.4%
  over-classification (v0.2.3: 69.3%, 99.0%, 8.8%); its gap-rule call
  58.6%, 99.4%, 4.9% (v0.2.3: 58.2%, 99.3%, 5.2%).

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

## v0.2.2

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

## v0.2.1

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

## v0.2.0

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

## v0.1.4

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

## v0.1.3 and before

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
