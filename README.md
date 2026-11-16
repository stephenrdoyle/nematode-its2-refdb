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

**Status: v0.2.4 (2026-11-15).** v0.1.0 was the first release. See
[docs/DESIGN.md](docs/DESIGN.md) for the design and the measurements
behind it, and [docs/feedback/its2_notes_for_amphid.md](docs/feedback/its2_notes_for_amphid.md)
for what amphid needs to change to use it. DADA2 and IdTaxa users: see
[For DADA2 and IdTaxa users](#for-dada2-and-idtaxa-users).

## Download and verify

```bash
V=v0.2.4
curl -LO https://github.com/stephenrdoyle/nematode-its2-refdb/releases/download/$V/nemits2_$V.tar.gz
shasum -a 256 nemits2_$V.tar.gz
# bfefebcdd89cb4535dd07061fd9500c852089c04c8d6b0ce7fe5064d0b3545a5
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

Earlier releases: [docs/RELEASES.md](docs/RELEASES.md).

<!-- figures:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/grade_dark.svg">
  <img alt="Bar chart: records per nematode group in nemits2_v0.2.4, by how much of the ITS2 they hold: I · animal parasites 446 (complete 49, near complete 186, partial 59, unmeasured 152); I · plant parasites 167 (complete 0, near complete 0, partial 0, unmeasured 167); I · free-living 16 (complete 2, near complete 2, partial 0, unmeasured 12); II · plant parasites 56 (complete 0, near complete 0, partial 0, unmeasured 56); II · free-living 19 (complete 1, near complete 0, partial 0, unmeasured 18); III · animal parasites 2,139 (complete 855, near complete 695, partial 367, unmeasured 222); IV · animal parasites 784 (complete 178, near complete 244, partial 140, unmeasured 222); IV · plant parasites 4,351 (complete 2,310, near complete 914, partial 508, unmeasured 619); IV · free-living 50 (complete 18, near complete 9, partial 8, unmeasured 15); V · animal parasites 3,628 (complete 1,175, near complete 1,469, partial 713, unmeasured 271); V · free-living 370 (complete 246, near complete 50, partial 36, unmeasured 38); Other Chromadoria · free-living 16 (complete 0, near complete 0, partial 0, unmeasured 16); Family not placed 2 (complete 2, near complete 0, partial 0, unmeasured 0)." src="docs/figures/grade_light.svg" width="760">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/taxa_dark.svg">
  <img alt="Bar chart: records per nematode group in nemits2_v0.2.4, and how many resolve to species read whole: I · animal parasites 446 (365 to species); I · plant parasites 167 (167 to species); I · free-living 16 (16 to species); II · plant parasites 56 (56 to species); II · free-living 19 (19 to species); III · animal parasites 2,139 (1,925 to species); IV · animal parasites 784 (691 to species); IV · plant parasites 4,351 (3,994 to species); IV · free-living 50 (42 to species); V · animal parasites 3,628 (3,347 to species); V · free-living 370 (296 to species); Other Chromadoria · free-living 16 (14 to species); Family not placed 2 (0 to species)." src="docs/figures/taxa_light.svg" width="760">
</picture>

How many species nemits2_v0.2.4 can name. A species named in the source records but with no record of its own shares its ITS2 with another species (or sits inside another species' record over its span), so a read from it is named only to genus or above. Names are counted as written.

| Records | Species named in sources | Species with their own record (read whole) | Species named through Illumina 150x150 | Species named through Illumina 250x250 | Species named through Illumina 300x300 | Genera |
|---|---:|---:|---:|---:|---:|---:|
| All records | 2,432 | 1,844 | 1,838 | 1,844 | 1,844 | 439 |
| **I · animal parasites** | 94 | 33 | 33 | 33 | 33 | 6 |
| I · plant parasites | 65 | 65 | 64 | 65 | 65 | 3 |
| I · free-living | 10 | 10 | 10 | 10 | 10 | 9 |
| II · plant parasites | 18 | 18 | 18 | 18 | 18 | 2 |
| II · free-living | 9 | 9 | 9 | 9 | 9 | 6 |
| **III · animal parasites** | 397 | 291 | 286 | 291 | 291 | 104 |
| **IV · animal parasites** | 225 | 149 | 149 | 149 | 149 | 13 |
| IV · plant parasites | 804 | 645 | 645 | 645 | 645 | 94 |
| IV · free-living | 29 | 21 | 21 | 21 | 21 | 13 |
| **V · animal parasites** | 619 | 500 | 500 | 500 | 500 | 161 |
| V · free-living | 157 | 102 | 102 | 102 | 102 | 25 |
| Other Chromadoria · free-living | 2 | 1 | 1 | 1 | 1 | 2 |
| Family not placed | 3 | 0 | 0 | 0 | 0 | 1 |

How far a record can be named in nemits2_v0.2.4, best case (an exact read, no sequencing error): the share of records resolving to species, and to genus at best.

| Records | Nanopore (whole ITS2): species | genus | Illumina 150x150: species | genus | Illumina 250x250: species | genus | Illumina 300x300: species | genus |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All records (12,044) | 91% | 9% | 89% | 10% | 91% | 9% | 91% | 9% |
| **I · animal parasites** (446) | 82% | 18% | 76% | 24% | 81% | 19% | 82% | 18% |
| I · plant parasites (167) | 100% | 0% | 99% | 1% | 100% | 0% | 100% | 0% |
| I · free-living (16) | 100% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| II · plant parasites (56) | 100% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| II · free-living (19) | 100% | 0% | 100% | 0% | 100% | 0% | 100% | 0% |
| **III · animal parasites** (2,139) | 90% | 10% | 86% | 14% | 90% | 10% | 90% | 10% |
| **IV · animal parasites** (784) | 88% | 12% | 88% | 12% | 88% | 12% | 88% | 12% |
| IV · plant parasites (4,351) | 92% | 8% | 91% | 9% | 92% | 8% | 92% | 8% |
| IV · free-living (50) | 84% | 16% | 84% | 16% | 84% | 16% | 84% | 16% |
| **V · animal parasites** (3,628) | 92% | 8% | 92% | 8% | 92% | 8% | 92% | 8% |
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

Most species-level records are close to another species: 690 at one
edit, 522 at two, 258 tied (`species_margins.tsv`, read whole), over a median ITS2 of
240 bases. At that length amphid's 99.7% species limit allows no
mismatch at all.

## How well reads are named

Tested two ways (docs/DESIGN.md §6): leave-one-out on the database
itself, and two livestock datasets (one published) run through the standard
nemabiome DADA2 workflow.

Leave-one-out figures are for v0.2.4, the datasets' for v0.2.1. Since v0.1.0 the classifier
also scores every candidate (issue #1) and scores read windows strictly
(docs/DESIGN.md §6).

**Leave-one-out** (3,220 records of 1,226 species, read whole; 2x150 is
within 3 points). *Present*: only the query's own record removed.
*Missing*: every record of the query's species removed, so any species
named is wrong. Recall = right calls / reads; precision = right calls /
calls made at that rank; over-classification = species named for a
missing species (`results/leave_one_out/metrics.txt`).

| Classifier, this database | Species recall | Species precision | Genus recall | Genus precision | Over-classification |
|---|---:|---:|---:|---:|---:|
| `bin/classify_asvs.py`, tiered (gap + tentative; the default) | 69.7% | 99.0% | 90.0% | 99.6% | 8.4% |
| `bin/classify_asvs.py`, gap rule (the tiered rule's confident call) | 58.6% | **99.4%** | 90.0% | 99.6% | **4.9%** |
| DECIPHER IdTaxa (threshold 60) | 80.4% | 97.6% | 94.4% | **99.7%** | 18.8% |
| dada2 assignTaxonomy (minBoot 80) | **86.3%** | 95.7% | **97.9%** | 99.4% | 38.9% |

The default is the tiered rule, which reports two calls for each read:
the gap rule's, the confident one, and beside it a tentative species
where the gap rule stops short. amphid calls the same way.

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
than the span-scored rules (`bin/classify_asvs.py`). Its tiered rule,
the default, names 98-99% of reads on both livestock sets with less
than half IdTaxa's over-classification; its gap-rule call, reported
beside it, over-classifies least.

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
