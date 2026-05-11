# Annotation Guidelines

Write annotations for French lyric study in Simplified Chinese.

## Style

- Use numbered markers: `①`, `②`, `③`, etc. Put each numbered annotation on its own line.
- Prefer concrete language points over broad song interpretation.
- Be fairly detailed: the target output should help a learner understand most words and structures in the lyric line.
- Use this general format:

```markdown
① amour（[amur]）：阳性名词，意为“爱、爱情”；注意以元音开头，前面的定冠词常省音为 `l'amour`。
② suis（[sɥi]）：`être` 的直陈式现在时第一人称单数，意为“我是/我在”。
③ ne ... pas：标准否定结构，歌词中常省略 `ne`，语气更口语。
```

## French Phonetic Guidance

- Use French phonetic transcription in word-by-word square brackets, for example `Je ne serai pas` -> `[Ʒə] [nə] [səre] [pa]`.
- Keep phonetic groups in the same order as lyric words. This gives practical word-level alignment without relying on fragile extra spaces.
- Use the symbol inventory below, not International Phonetic Alphabet output, English respelling, pinyin, or approximate Chinese pronunciation.
- Represent French `r` as `[r]` in this system.
- Use nasal vowels accurately: `an/en` often `[ɑ̃]`, `in/ain/ein` often `[ɛ̃]`, `on` often `[ɔ̃]`, `un` often `[œ̃]`.
- Final consonants are often silent, but pronounce final `c`, `r`, `f`, `l` when the word normally requires it.
- Mark elision naturally: `je aime` becomes `j'aime` in spelling and `[Ʒεm]` in French phonetics.
- Mark liaison only when normally expected in connected speech or careful singing, especially after determiners, pronouns, and common adjectives. Do not overforce optional poetic liaison.

### Symbol Inventory

- 口腔前元音: `[i] [e] [ε] [a]`
- 口腔中元音: `[u] [o] [ɔ]`
- 口腔后元音: `[y] [ф] [ə] [œ]`
- 鼻化元音: `[ɛ̃] [œ̃] [ɑ̃] [ɔ̃]`
- 爆破辅音: `[p] [b] [t] [d] [k] [g]`
- 摩擦辅音: `[f] [v] [s] [z] [ʃ] [Ʒ]`
- 鼻辅音: `[l] [m] [n] [ɲ]`
- 边辅音: `[r]`
- 半元音: `[ɥ] [w] [j]`

## Annotate

- Nouns: gender, number, meaning, and article contraction when useful.
- Verbs: infinitive, current conjugated form, tense, mood, person/number, reflexive/pronominal status, participle agreement when relevant, and meaning in context.
- Adjectives and participles: gender/number agreement and noun modified.
- Pronouns: subject, object, reflexive, relative, demonstrative, possessive, and their referent if recoverable.
- Prepositions and contractions: `à`, `de`, `au`, `aux`, `du`, `des`, `dans`, `sur`, `sans`, etc.
- Negation: `ne ... pas`, `ne ... plus`, `ne ... jamais`, omitted `ne`, and polarity words.
- Tense/aspect/mood: présent, imparfait, passé composé, futur simple, conditionnel, subjonctif, impératif, infinitif constructions.
- Fixed expressions and idioms, including their literal meaning when it helps memory.
- Register and lyric usage: colloquial deletion, inversion for rhythm, omitted subjects, repeated fragments, and nonstandard punctuation.
- Pronunciation points that help singing or recognition: silent final letters, liaison, elision, schwa deletion/retention, nasal vowels.

## Usually Do Not Annotate

- Extremely common articles or subject pronouns by themselves if the line is already heavily annotated and their use is ordinary.
- Repeated words already explained in the immediately preceding repeated line, unless the repeated context changes form or meaning.
- Pure interpretation of imagery without a language point.

## Verb Note Checklist

For each conjugated verb, try to include:

- Annotation heading shape: put only the French phonetics in parentheses, for example `sommes（[sɔm]）`.
- Infinitive: `aime` -> `aimer`.
- Form: `présent de l'indicatif`, `imparfait`, `passé composé`, `conditionnel présent`, `subjonctif présent`, etc.
- Person/number: `1re personne du singulier`, `3e personne du pluriel`, etc.
- Pronominal or reflexive marker when present: `se souvenir`, `s'en aller`.
- Function in the line: main verb, auxiliary, modal-like use, relative clause verb, imperative, participle adjective.
