# Single-study and not-ITS2 screens on nemits2 v0.2.5 (2026-11)

Two screens were written after the *Hysterothylacium* curation (`docs/curation_hysterothylacium_2026-11.md`) showed that one study can carry many bad records at once. They run on every build that takes in new sequences (README, Build).

## `bin/study_screen.py`: submissions at odds with the rest

It groups accessions into submissions, meaning runs of consecutive accession numbers. Each submission's records of a species are then checked against that species' records from every other submission. On v0.2.4 it finds the *Collichthys lucidus* croaker study by itself, and on v0.2.5 it no longer does.

v0.2.5 results:
- 757 species can be checked; 1,125 come from a single submission and cannot be.
- 4 `mislabel` calls, 62 `lineage` calls and 71 `records` calls.

Mislabel calls:
- ***Heterodera hordecalis* PQ221924, PQ221927, PQ221928:** three clones 1-3 edits from *H. goettingiana* and 64-66 from every other *H. hordecalis*. Dropped.
- ***Meloidogyne graminis* JN241868, JN241892, JN241894, JN241895:** four clones at 0-1 edits from *M. marylandi*. Left: the two species overlap, and the data cannot resolve it. The gap rule stops at genus there.
- ***Trichuris trichiura* JN181775-JN181860:** clones from human worms close to *T. suis*. Left.
- ***Cephalenchus daisuce*:** clone variation within one study. Left.

The lineage calls with no support, where a small submission stands against many independent ones, were checked by hand. Most turned out to be records that are not ITS2 (below). The others were left:
- *Trichuris arvicolae* PP495534-45;
- *Pratylenchus goodeyi* OR141133-6;
- *Aphelenchus avenae* MT492465-91;
- *Heterodera filipjevi* MG066501-22 and the Kazakh *Heterodera* clones;
- *Oesophagostomum columbianum* LC777641-48.

***O. columbianum* LC777641-48** (Japan; isolates OC2, OC3, OC7, OC9) is a consistent 261-base ITS2, against 214-220 bases for the 18 other accessions from 6 submissions. Aligned, it is that ITS2 with six inserted stretches and one substitution. The same submission's *O. asperum* (LC777661-2) matches the other *O. asperum* records to within 1-2 edits. So it is either a lineage of *O. columbianum* or a close relative identified as it. It names no other species, so it is left.

## `bin/not_its2.py`: records that may not be ITS2

Where a GenBank record has no flanking sequence, or the anchor search fails, `bin/its2.py` keeps the backbone's HMM cut, and nothing checks it. The screen looks at four things for each record:
- how its members were cut;
- primer and 28S sites inside the cut or reverse-complemented, and the 18S end;
- its length against its species' complete records;
- its identity to its family's complete records, and to its genus' records from its own and other submissions.

Unrelated DNA scores about 0.5.

v0.2.5 results:
- 8 `its1`, 12 `reversed`, 33 `not_its2`, 2 `miscut`.
- The `check` records split three ways:
  - 225 `supported`: another submission has the same ITS2.
  - 140 `own_only`: only their own submission's records match. Left as unconfirmed; mostly *Heteroxynema* (54) and *Trichuris* (43).
  - 48 `isolated`.

Dropped:
- **57 accessions** with no sign of ITS2, among them:
  - *Ostertagia ostertagi* KR779996-8: 552-602 bases against 241.
  - *Contracaecum rudolphii* MN557378-85: ITS1.
  - *Ancylostoma ceylanicum*, *Dictyocaulus*, *Globodera* and *Heterodera*.
  - Three 150-base *Haemonchus contortus* partials with a reversed NC1 inside, taken as chimeras.
- **21 isolated records** with no anchor and 0.59 or less identity to everything in their genus, though the genus has other records. Among them are two *Teladorsagia circumcincta*.

The three isolated records alone in their genus are left: *Pseudaphelenchus jiaae*, *Orientostrongylus ezoensis* and *Graphidioides affinis*.

On v0.2.5's own intake (`--since` v0.2.4), the screen flags the 3 *Gnathostoma* accessions from the 16 November update (130 bases, not ITS2) and a *Steinernema* record. Both are among the drops.

## Other decisions

- **Dropped:** *Heterodera urticae* PV138334. It is 1 edit from *H. cruciferae* and 5 from the only other *H. urticae* record. In amphid's leave-out benchmark on v0.2.5 it made 7 of the 17 wrong calls (`docs/feedback/amphid_notes_for_its2.md`, point 7).
- **Left:**
  - The *H. hainanense* accession that keeps an *H. fabri* record at genus.
  - *Cactodera estonica* HM560732 (`closer`: 7 edits from *C. xinanensis*, 10 from its own species).
