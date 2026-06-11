# Phase 3 template-exception table (instantiation)

Built per diagnostics.yaml `notes` -- every non-trivial transformation is documented here, never silently hand-edited. Grid = 535 lexemes x 24 confirmed judgment diagnostics = 12840 cells. well_mod + that_clause_complement instantiate late (appended), not here.

## Morphology realization (spelling, never acceptability)
Every cell is realized with the lexeme's most charitable well-formed candidate; raters judge it. *worther*/*beautifuller* rated bad IS the datum (that the base fails synthetic comparison; the periphrastic escape is the separate comparative_more item). The instantiator makes spelling decisions only -- it never marks a cell non-applicable (that would smuggle the verdict into the template). Counts: comparative 535, -ly 535, -ness 535, un- 535 cells (all lexemes).

Logged dictionary facts + orthographic rules:
- Suppletive comparatives: {'good': 'better', 'bad': 'worse', 'far': 'further', 'little': 'less', 'well': 'better'} (e.g. good->better, never *gooder).
- Regular comparative: e->+r (nice->nicer); y->ier (happy->happier); CVC monosyllable doubles (big->bigger); else +er (worth->worther).
- Irregular -ly: {'true': 'truly', 'due': 'duly', 'whole': 'wholly', 'full': 'fully'}; -ic->-ically; -le->-ly (gentle->gently); y->ily (happy->happily); else +ly.
- -ness: y->iness (happy->happiness); else +ness.
- un-: un+stem, no stem change (unhappy, unnear). Hyphenation (un-X vs unX) and off-category strings (*unnear*, *una few*) stand as garbage-is-data.

## enough collision
`enough_postposed`/`enough_preposed` x lexeme *enough*: 2 cells ('enough enough'), flagged not hand-edited (pm ruling).

## postpositive note-form
`postpositive`: 535 cells instantiated as 'The something LEX happened.' per the diagnostics.yaml note (not the bare frame).

## optional complements
Frames with '(something)' optional complements (very_mod, too_mod, comparative_more, right_mod, enough_preposed, seem_complement, become_complement, coordination_with_adj) are instantiated WITHOUT the optional, to test the target operator cleanly (avoids confounding with np_complement).

## determinative underscore->space (from the sample stage)
Multiword determinative labels convert underscore->space at the sample stage (logged in phase3_sample_manifest.json); they instantiate as multiword surfaces, and morphological frames over them produce garbage-is-data:
- `a_certain` -> *a certain*
- `a_few` -> *a few*
- `a_great_many` -> *a great many*
- `a_little` -> *a little*
- `many_a` -> *many a*
- `no_one` -> *no one*
