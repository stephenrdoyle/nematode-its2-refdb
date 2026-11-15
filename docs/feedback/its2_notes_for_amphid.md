# Notes for amphid: using the nematode ITS2 database

From nematode-its2-refdb (named nemabiome-its2-refdb until v0.1.4)
v0.1.1 (2026-11-10); updated for v0.2.2 (2026-11-15, "What changed in
v0.2.2" below). The database follows
vespa-18s-refdb's release format. These are the places where ITS2 needs
something V4 did not.

Tracked in amphid as
[stephenrdoyle/nf-amphid-pipeline#9](https://github.com/stephenrdoyle/nf-amphid-pipeline/issues/9),
which maps each point below to the amphid code it changes. The issue
also covers two points not here: `taxonomy.tsv` has NCBI's eight ranks,
not the PR2 levels amphid hard-codes, and amphid's identity charges a
read's unaligned ends - for ITS2, the 28S stretch - as differences.

## What changed in v0.2.2

**Two columns added to `taxonomy.tsv`, nothing else:** `contained_in`
and `contains`, the `;`-separated ids of named records of another
species that hold this record's ITS2 exactly (the same sequence, bases
missing at one or both ends), or that it holds; and
`counts.contained` in `manifest.json`. 151 record pairs, 57 species
pairs, 185 records, none in livestock strongylid genera. These records
were already tied (margin 0, `deepest_rank` genus or above in the
resolution tables), so no margin, rank or record changed. A held-out
read of one species of such a pair matches the other at 100%
(*Contracaecum rudolphii* named *C. ogmorhini* in amphid's leave-out
benchmark): the columns name that other record. Records are the same
as v0.2.1's.

## What changed in v0.2.1

**One file added, nothing else in the format:**
`resolution_illumina_300x300.tsv` for MiSeq v3 2x300 (windows 280 +
233), its `illumina_geometries` entry in `manifest.json`, and a
`margin_280x233` column in `species_margins.tsv`. **One curation
change:** *Spiculopteragia boehmi* relabelled *S. spiculoptera* (one
species under two names), 1,872 named species. **The recipe gained**
the one joining rule at every read length (§3), PacBio (§3a), and a
scoring rule for a concatenated read 1 that reaches 28S (§5).

## What changed in v0.2.0

**The format did not change.** The same files, columns and manifest
keys as v0.1.4; only the file names carry the new version, and the
repository is now nematode-its2-refdb (the old URLs redirect).

**The content did** (12,053 records, 1,873 named species, 439 genera;
v0.1.4 11,288, 1,874, 427):

- 737 informal "Genus sp. X" records from GenBank: `species_status` =
  `unnamed`, genus only, the informal name in `lineage` (769 `unnamed`
  records in all, 51 in v0.1.4). Score them only after the named
  records (§5): they place reads no named record reaches, such as the
  gorilla hookworm "*Necator* sp.", 45 edits from *N. americanus*.
- `lineage` also carries the Hasegawa *Necator* rDNA types (type II,
  type III).
- 248 ITS2 copies from 48 genome assemblies and 10 long-read sets (174
  in v0.1.4), and curation since: the *Metastrongylus* records, two
  more drops (MF784940, PZ362967), *T. capricola* JF276023 dropped and
  eight Sri Lankan "*D. repens*" relabelled *D. asiatica*.

New here: §3 recommends joining 2x250 pairs hybrid, and §7 asks for
the unplaced ITS2 as FASTA.

## What changed in v0.1.4

**The format did not change.** The same files, the same `taxonomy.tsv`
columns (`lineage` last, since v0.1.3) and the same manifest keys; only
the k-mer file names carry the new version. Whatever reads v0.1.3 reads
v0.1.4.

**The content did** (11,288 records, 1,874 named species, 427 genera;
v0.1.3 11,135, 1,864, 426):

- 733 GenBank records the nemabiome backbone lacks (published since its
  17 March 2026 snapshot, or ITS2s inside 5.8S/28S records), among them
  a complete *Oesophagostomum radiatum* (PZ347037) where that species
  had only partials.
- 65 more records dropped and 2 relabelled after a species coherence
  screen, among them West African "*H. contortus*" carrying the
  *H. placei* ITS2. Fewer wrong names to inherit.
- Informal "sp." names are no longer species: 19 records are now
  `species_status` = `unnamed` at genus, their informal name in
  `lineage` (51 `unnamed` records in all, 32 in v0.1.3).
- `manifest.json` `counts.lineage_records` lists these as well as the
  goat line.

**Two scoring points are new** (§5): score simple repeats by copy
number, and report a tentative species tier beside the gap rule's call.
Both are in this repository's reference scorer (`bin/its2_classify.py`)
and change no release file. The leave-one-out and real-data figures in
§5 are for v0.1.4 with both.

## 1. Score reads over the reference's span

A reference runs from the 3' end of NC1 to the start of the ~47-base
28S stretch before NC2. Reads carry that stretch; references do not,
because it varies by 1-6 bases between nematodes and borrowing one
would invent differences. About two thirds of references are also
partial at one end or both (`grade` below).

So identity must be computed over the reference's span: the reference
aligned end to end, the read's bases beyond it free (semi-global /
"glocal" alignment, reference global, read local). Scoring over the
read's full length would charge every read ~47 bases of 28S against
every reference, and charge a partial reference for bases it simply
lacks.

`manifest.json` states this as `score_over`. Margins and resolution
tables in the release are computed the same way.

## 2. Primers

NC1 `ACGTCTGGTTCAGGGTTGTT`, NC2 `TTAGTTTCTTTTCCTCCGCT`, each ordered
with 0-3 N spacers behind the Illumina adapter (nemabiome.ca's
protocol). Primer trimming must allow a 0-3 base offset, and the
deposited sets we tested needed more:

- **pairs in both orientations**: some libraries ligate both ways
  (PRJNA1137257, zoo antelopes); a pair with NC1 on read 2 and NC2 on
  read 1 must be turned round, not discarded;
- **read 2 starting inside 28S, with no NC2**: half the PRJNA1524548
  libraries use a reverse primer on 28S; trim read 2 at the conserved
  28S motif when NC2 is absent (93.9% of pairs kept instead of about
  half);
- **read-through**: a read longer than the amplicon runs on through the
  other primer; cut it where the other read starts;
- **primers clipped at the 5' end** by up to 3 bases (a fifth of the zoo
  pairs) should still be accepted;
- **reads deposited without primers** (PRJEB64582) need a mode that
  skips primer finding and tells a pair's orientation by read 2's
  conserved 28S start.

Each acts only on a pair that needs it. Reference: `bin/trim_primers.py`
(`--pretrimmed`; `--strict` turns the rest off).

## 3. Read windows

2x150, primers trimmed: forward read = first 130 bases of the ITS2;
reverse read = last 130 bases of the amplicon, of which ~47 are 28S, so
the last 83 of the ITS2. 2x250: 230 + 183; 2x300: 280 + 233 (since
v0.2.1). With a median ITS2 of 240
bases, most 2x250 pairs and many 2x150 pairs overlap and merge.
`manifest.json` → `illumina_geometries` gives the windows.

**Join pairs hybrid, at every read length**: merged where the pair overlaps,
concatenated (forward + reverse, as for unmerged pairs) where it does
not. Merging alone silently drops every pair whose ITS2 is too long to
overlap: `mergePairs` needs 12 bases, and after primer trimming (about
230 + 230) any ITS2 over about 400 bases never merges. That is
*Metastrongylus* (413-422 bases), Trichuridae, Metastrongylidae,
Onchocercidae and others. In PRJNA1524548 two pig libraries kept 6 and
665 reads merged against 22,932 and 19,801 hybrid, and *M. apri* rose
from 1.6% to 3.0% of the set's reads. Hybrid also keeps pairs that
overlap but fail merging on mismatches (4.6% of Francis & Šlapeta
pairs). It costs the gap rule 0.7-0.9 points of species calls against
merging alone; concatenating every pair costs more where the ITS2 is
short and read 1 runs through into 28S. The ASV table then holds merged
and concatenated ASVs side by side, and each is scored as it is: a
merged ASV whole, a concatenated one as two windows (§5). The README's
"For DADA2 and IdTaxa users" section has the dada2 code.

The same rule holds at every read length; only how many pairs merge
changes. At 2x150 almost no strongylid pair overlaps (trimmed reads
cover 130 + 130 bases of a ~270-330 base amplicon), so hybrid is
concatenation: on four sets, merging alone kept 0.4-11% of reads,
hybrid and concatenation named the same species (Francis & Šlapeta
98.5%, PRJNA1524548 98.3% tiered) and matched the 2x250 composition
equally (median per-sample difference 0.9-1.7%); the few pairs that do
merge at 2x150 are mostly primer dimers. At 2x300 (MiSeq v3) nearly
every pair overlaps, and hybrid keeps the 2-8% that fail to merge on
mismatches in the poorer read ends: German cattle 144,023 reads hybrid
against 141,213 merged, camels 543,334 against 525,517, roe deer
279,813 against 258,518, with the same species shares (99.1 / 99.3%,
99.6 / 99.9%, 87.4 / 87.3%).

Use DADA2's `mergePairs` with its defaults, after denoising each read:
it joins the two denoised sequences only where they agree over the
overlap, and the error correction is the denoising. Mergers that join
raw reads before denoising (PEAR, FLASH, VSEARCH) are not part of the
recipe. Nanopore and PacBio reads are single and scored whole (§3a).

DADA2's chimera check cannot see a chimera whose join falls in the gap
between the two reads of a concatenated pair. Most of the zoo set's
unplaced ITS2 (0.21% of reads) is such chimeras: read 1 *Haemonchus* or
*Teladorsagia*, read 2 *T. axei*.

## 3a. PacBio

Full-length reads (circular consensus / HiFi) are single reads of the
whole amplicon, so there is no joining and no window: each ASV is scored
whole, as a merged pair or a nanopore read. A run is declared as PacBio
up front, and that selects the settings:

1. **Demultiplex with `lima`** (symmetric tags, `--hifi-preset
   SYMMETRIC`), giving it only the tags of the library being read:
   SMRT cells are shared, and other projects' reads carry other tags of
   the same set (in S-BSST527, half the reads).
2. **Primer-trim single reads** (`bin/trim_primers.py --platform
   pacbio`): orient each read NC1-first, cut after NC1 and before NC2,
   matching primers by edit distance (PacBio errors are mostly
   insertions and deletions in homopolymers; a mismatch-only match lost
   12% of reads), keep the 28S stretch.
3. **DADA2 on single reads** (`bin/dada2_nemabiome.R` mode `single`):
   `filterAndTrim(maxN = 0, maxEE = 2, minLen = 200, maxLen = 1000)`,
   `BAND_SIZE = 32`; the error model is `PacBioErrfun` for HiFi
   (qualities to Q93), the default for older RSII reads (to Q42).
4. **Classify** as everything else (§5).

Tested on Halvarsson & Höglund's Swedish sheep (S-BSST527, RSII, 158
larval cultures): 99.3% of reads to species, the dominant species'
shares within a point of the paper's, and their single "*T. vitrinus*"
resolved into *T. vitrinus*, *T. axei* and *T. colubriformis* (each an
exact match, 4-6 edits clear of the next).

## 4. Grade

`taxonomy.tsv` and the resolution tables carry each record's `grade`:
`complete`, `near_complete` (>= 98% of the ITS2), `partial_90`,
`partial_75`, `partial` (< 75%), `unmeasured`. A read matching a
`partial` reference at 100% has been checked on fewer bases. Report the
grade with the call, and consider requiring a minimum aligned length
(say 150 bases) for a species call.

## 5. Identity limits: use the gap rule

The V4 limits (species 99.7% Illumina / 99.5% nanopore, genus 99.5% /
99%, family 95%) were set for a ~400-base insert. Over a 240-base ITS2,
one edit is 0.42%, so 99.7% means an exact match. Margins are thin: of
the 11,197 species-level records in v0.2.0, 290 are tied with another
species, 723 are one edit away and 549 two (`species_margins.tsv`, read
whole).

A leave-one-out test (DESIGN §6.1; 3,225 queries, 1,231 species, on
v0.2.1) shows identity alone is the wrong
measure. Under the V4 limits only 19.3% of reads whose species is in
the database are named to species. What separates a right call from a
wrong one is the margin to the next species. Recommended rule:

- **species**: >= 99% identity over the span AND the best reference of
  any other species is >= 4 edits further off (same span); or an exact
  match (0 edits) AND that reference is >= 2 edits off;
- **genus** >= 97%, **family** >= 95%;
- a reference with `species_status` = `unnamed` (hybrids, cf.,
  environmental, informal "sp." names) is not "another species"; a
  `shared` one is;
- score against named records first, and against the informal
  "Genus sp." records (`unnamed`, informal name in `lineage`) only where
  that call stops above genus, keeping the deeper call. They are there
  to place reads no named record reaches (the gorilla *Necator* sp.),
  and scored alongside the named ones they can take a named species'
  variants. Since the build after v0.1.4 there are 737 of them.

Recall = right calls / reads; precision = right calls / calls made at
that rank; over-classification = a species named for a read whose
species is missing from the database.

| Rule (whole reads) | Species recall | Species precision | Genus recall | Genus precision | Over-classification |
|---|---:|---:|---:|---:|---:|
| V4 limits | 19.3% | 94.7% | 51.8% | 99.3% | 1.8% |
| gap rule | 57.9% | 99.3% | 89.8% | 99.4% | 5.5% |
| tiered: gap rule + tentative species at >= 98% | 68.9% | 99.0% | 89.8% | 99.4% | 9.1% |
| dada2 assignTaxonomy, for scale | 86.5% | 95.6% | 97.6% | 99.3% | 39.3% |
| DECIPHER IdTaxa, for scale | 79.6% | 97.4% | 94.2% | 99.5% | 19.7% |

(v0.2.1; v0.2.0 gave 57.7%, 99.3% and 5.4% for the gap rule, v0.1.4
57.3%, 99.2% and 5.5%, before
repeat-aware scoring 56.4%, 99.2% and 5.4%, and v0.1.3 55.3%, 98.8% and
5.9%. With informal records, reads of a missing species whose genus is in the
database reach the right genus 30.7% of the time, from 26.2% in v0.1.4,
with no more wrong genera.)

**A tentative tier.** Half the present-species reads the gap rule
stops at genus have no other species within 4 edits but are 1-3% from
their own (intraspecific variation). Naming those at >= 98%, with the
same 4-edit gap, as a flagged *tentative* species call gains 11 points
of recall for 4 of over-classification, and on real data names the goat
line of *T. circumcincta*, *Oe. venulosum* and *Oe. radiatum* reads held
at genus (Francis & Šlapeta, 2x250 hybrid: 95.7% to 99.4% of reads to
species, v0.2.0). Keep
the gap rule's call as the confident one and report the tentative call
beside it: a read 1-2% from its own species looks the same as one 1-2%
from a missing sister, which is what tentative kangaroo *Cloacina* calls
may be. `bin/classify_asvs.py` writes `tiered_rank`, `tiered_name` and
`tentative`. On the Francis & Šlapeta goats this brings the goat line
to species: per-host shares then match IdTaxa's to within a point, and
the published analysis's within 1-2 points in cattle and sheep.

Limits set separately per genus or family did no better on held-out
species. Thresholds cannot fix the remaining missing-species errors:
four in five are sister species under 1% apart with one of them
missing, the rest reads identical to a record deposited under another
name.

**Report how close a call came.** With each call, give the best species
and its identity, and the nearest other species with how many edits
further it is. Example: "*Trichostrongylus*; nearest *T. rugatus* 99.6%;
next *T. retortaeformis* +2". A genus call then says whether it is "exactly
species X, but its sister is 1 edit away" or "98% to X, nothing else
close". Both stop at genus for different reasons, and users act on them
differently. `bin/classify_asvs.py` writes these as `nearest` and
`next`.

**Report the lineage.** `taxonomy.tsv` has a `lineage` column: a
published line within a species, kept under the species' name: the
*Teladorsagia circumcincta* goat line (2 records), which Francis &
Šlapeta (2023) found in goats and not in sheep on shared pasture. It
also carries the informal name of a genus-level record, whose species
is blank (737 in v0.2.0, 19 in v0.1.4: *Oesophagostomum* sp.
3335_MDR_CAM_OH15, *Cloacina* sp. 1 AJ-2019), and since v0.2.0 the
Hasegawa *Necator* rDNA types ("Necator sp. type II", "type III"):
gorilla, chimpanzee and human *Necator* reads in Cameroon that stop at
genus are type II. When every tied best reference carries the same lineage,
report it with the call, at any rank: a goat-line read at 98% stops at
genus but is still "nearest *T. circumcincta* (goat line) 98.0%". Blank
means no line is recorded, not the other line. `bin/classify_asvs.py`
writes it as `lineage`.

**Score read windows strictly.** Charge every reference base from the
reference's own end to where a window stops; leave read bases free only
before the reference's start (primer offset, up to 30). Cut the second
window at the 28S anchor, not at a fixed 47 bases. Giving a reference's
first bases slack let one partial *H. bedfordi* record tie *H. placei*
reads in the reference scorer (DESIGN §6.2); amphid already charges
them. **A concatenated pair whose read 1 already reaches the 28S
anchor** (a pair that overlaps but failed to merge, common at 2x300)
spans the whole ITS2: score read 1 whole, not as a window, or its 28S
bases are charged as differences. Without this, 2x300 hybrid lost real
species to "unplaced" (camels 99.6% -> 96.6% to species);
`bin/classify_asvs.py` does it since 2026-11-14.

**Score simple repeats by copy number.** A difference in how many units
a simple repeat has (a homopolymer of >= 4 bases, >= 3 copies of a 2-3
base unit) should cost one edit, not one per base: goat *Oe. venulosum*
reads with an (AT)n 16 bases longer than any reference were 13-21 edits
off and stopped at family. Score each reference both plain and with
repeats collapsed and keep the better, but measure the margin to the
next species plain: collapsing that too made sister species that differ
mainly in repeat length (*T. trichiura* / *T. incognita*, *O. volvulus* /
*O. ochengi*) unresolvable. A repeat cut short where a read window stops
should not be charged. In leave-one-out this names 19 more species when
present and costs 0.1 points of over-classification
(`bin/its2_classify.py` `collapse()`).

**Orient reads.** A sequence whose best hit is on the reverse strand
should be turned before scoring; IdTaxa does this with
`strand = "both"`.

## 5a. If a k-mer classifier is used instead

assignTaxonomy and IdTaxa compare k-mers over the whole ASV, not over
the reference's span. Against this database, whose records stop before
the 28S stretch, every ASV carries ~47 bases no reference has. Cut the
stretch off the ASVs first (`bin/trim_28s.py`, or `R/trim_28s.R` as
shipped with the release: at the 28S anchor
`AACCTGAGCTCAGTCGTGATTACCCGCCGAACTTAAGCATATCA`, else the last 47
bases). Uncut, assignTaxonomy named 45% of reads of one sheep set to
species; cut, 99.2%.

## 6. Ties are already resolved in the tables

A record whose span sits exactly inside another species' record is
"tied" with it. The resolution tables stop it at the shared rank. If
amphid assigns from the tables, nothing more is needed. If it assigns
from alignments, a read hitting both at the same score must be given
their common ancestor. That is the usual LCA rule, but it only works if
both hits are reported, so secondary alignments must not be capped
below the number of tied records.

## 7. Save what stays unplaced

An ASV left above family falls into one of two groups, and they mean
different things:

- **unplaced ITS2**: it aligns to records, but none is within family
  range (95%). It ends in the 28S stretch like any ITS2 amplicon, and
  the `nearest` record says roughly where it sits. These are nematodes
  the database lacks: in the Cameroon apes (PRJEB64582), 17% of reads,
  mostly a *Paralibyostrongylus* 79-92% from anything named.
- **not ITS2-like**: nothing in the database aligns to it, and it
  seldom carries the 28S stretch. Primer dimers, chimeras and
  off-target products: BLAST finds gut bacteria and phages, or nothing.
  Zoo antelopes (PRJNA1137257) 8% of reads, Cameroon 0.6%.

Write each group to its own FASTA, so that unplaced ITS2 can be taken
further (BLAST, a tree, a request for adult-worm references) without
digging it out of the tables:

    >ASV00004 reads=188804 libraries=139 nearest=Libyostrongylus_douglassi identity=91.4 next=Libyostrongylus_dentatus+8
    TTGT...

and report both shares beside the classified ones, not as one
"unassigned". The ASV is the whole amplicon, 28S stretch included.
