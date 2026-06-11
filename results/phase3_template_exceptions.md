# Phase 3 template-exception table (instantiation)

Built per diagnostics.yaml `notes` -- every non-trivial transformation is documented here, never silently hand-edited. Grid = 526 lexemes x 24 confirmed judgment diagnostics = 12624 cells. well_mod + that_clause_complement instantiate late (appended), not here.

## Morphology schemas (flagged `needs_realization`)
Stem-affecting derivations are emitted as schemas with a `+` marker (e.g. *happy+er*, *happy+ly*, *happy+ness*) and realized per lexeme BEFORE judging (good->better, good->well, true->truly; non-applicable forms marked, not silently concatenated -- avoids rating spelling errors as the diagnostic). Extends the pre-known comparative exception to -ly/-ness on the same suppletion/spelling logic.
- `inflectional_comparison` (+er): 526 cells, all lexemes.
- `ly_adverb_base` (+ly): 526 cells, all lexemes.
- `ness_nominalization` (+ness): 526 cells, all lexemes.

## un- prefix (produced; garbage-is-data)
`un_prefix`: 526 cells, concatenated `un`+surface (un- does not alter the stem). Off-category strings (*unnear*, *una few*) are correct data, not errors; the orthographic flag marks hyphenation review (un-X vs unX) for the realization pass.

## enough collision
`enough_postposed`/`enough_preposed` x lexeme *enough*: 2 cells ('enough enough'), flagged not hand-edited (pm ruling).

## postpositive note-form
`postpositive`: 526 cells instantiated as 'The something LEX happened.' per the diagnostics.yaml note (not the bare frame).

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
