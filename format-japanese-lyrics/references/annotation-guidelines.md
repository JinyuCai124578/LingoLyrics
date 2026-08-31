# Annotation Guidelines

Write annotations for Japanese lyric study in Simplified Chinese.

## Style

- Keep each note short, objective, and useful: usually one sentence, at most two.
- Use numbered markers: `①`, `②`, `③`, etc.
- Use this format: `①词或短语（かな / romaji）：词性，简短解释；必要时补充词源或用法。`
- Prefer concrete language points over broad song interpretation.
- Keep the romaji style from the input: spaced by kana/mora, long vowels split as `o u`, `e i`, etc.
- In generated lyric notes, quote Japanese words, grammar forms, particles, and set phrases with Japanese corner brackets: `「虚しい」`, `「てしまう」`, `「が」`. Do not use Markdown inline-code backticks for these language examples.
- Maintain the same annotation depth across the whole song. Later blocks should stay as specific as earlier blocks: readings, romaji, part of speech/function, and a concise usage explanation when the earlier style includes them.
- For grammar-heavy or morphologically rich expressions, decompose the form before giving the meaning: identify the base word, conjugation, auxiliary/helper verb, suffix, or contraction, then explain how the pieces combine. Prefer this especially for 「ている」, 「てしまう/ちゃう/じゃう」, 「たい」, potential/passive/causative forms, negative forms, colloquial contractions, compound verbs, and fixed expressions.

## Annotate

- Content words: nouns, verbs, adjectives, adverbs.
- Mimetic words and onomatopoeia, especially when they carry mood or motion.
- Loanwords: mention source language when helpful.
- Fixed phrases, idioms, colloquial contractions, and omitted elements common in lyrics.
- Difficult kanji readings, ateji, jukugo readings, and word-origin points that aid memory.
- Grammar patterns that affect meaning: contrast, concession, conditionals, negation, potential, passive, causative, te-form chains, 「てしまう」, 「ている」, 「てくる/ていく」, sentence-ending nuance.
- Differences between literal meaning and the supplied Chinese translation when useful.
- Repeated or parallel lines should keep comparable note detail, or explicitly explain the contrast from the earlier occurrence. Do not reduce later repeated sections to vague or bare notes just because similar material appeared before.

## Usually Do Not Annotate

- Basic particles alone: 「の」, 「が」, 「は」, 「を」, 「に」, 「で」, 「と」, 「も」, 「から」, 「まで」, 「へ」, 「や」.
- Very ordinary inflection such as plain 「ます」, 「た」, or 「て」 forms, unless the form is part of a meaningful expression.
- Items already explained in the immediately preceding repeated line may be summarized only when the line is truly identical and the surrounding section is already well annotated. For later chorus returns or parallel variants, preserve comparable detail or name the difference.

## Example Note Shape

```markdown
①言ってる（いってる / i tte ru）：动词「言う」的て形「言って」 + 补助动词「いる」的口语缩约「る」，表示动作正在进行或状态持续，意为“正在说、说着”。
```
