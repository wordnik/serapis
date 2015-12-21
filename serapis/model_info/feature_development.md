## Part-of-Speech Features

### Development

The **top 10 most identifying features** for free-range definitions by part-of-speech tag analysis as measured by the chi-squared test (chi2) are:

| part of speech pattern | [chi^2 distance score](https://github.com/summerAI/wordnik/blob/clare/frd-model-init/serapis/model_info/pos_tag_features_chi2dist.csv) | (fictive) example |
| --- | --- | --- |
| _term_ vbz dt | 40.644784189606625 | _term_ conveys this |
| _term_ vbz    | 19.890285126112712 | _term_ is |
| vbz dt nn | 11.730307326381473 | is an action |
| vbz dt    | 10.91237066719685 | shows this |
| _term_ wdt vbz    | 9.9010813488181686 | _term_ which |
| dt _term_ vbz | 9.6538475741645939 | a _term_ is |
| vbz dt jj | 9.1372092998409364 | is a descriptive |
| nn vbn    | 8.3832595804348031 | word meant |
| vb nns    | 8.3057406590157896 | describing words |

### Reference

Alphabetical list of part-of-speech tags used in the [Penn Treebank Project](https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html):

| Number | Tag | Description |
| --- | --- | --- |
| 1. | CC | Coordinating conjunction |
| 2. | CD | Cardinal number |
| 3. | DT | Determiner |
| 4. | EX | Existential there |
| 5. | FW | Foreign word |
| 6. | IN | Preposition or subordinating conjunction |
| 7. | JJ | Adjective |
| 8. | JJR | Adjective, comparative |
| 9. | JJS | Adjective, superlative |
| 10. | LS | List item marker |
| 11. | MD | Modal |
| 12. | NN | Noun, singular or mass |
| 13. | NNS | Noun, plural |
| 14. | NNP | Proper noun, singular |
| 15. | NNPS | Proper noun, plural |
| 16. | PDT | Predeterminer |
| 17. | POS | Possessive ending |
| 18. | PRP | Personal pronoun |
| 19. | PRP$ | Possessive pronoun |
| 20. | RB | Adverb |
| 21. | RBR | Adverb, comparative |
| 22. | RBS | Adverb, superlative |
| 23. | RP | Particle |
| 24. | SYM | Symbol |
| 25. | TO | to |
| 26. | UH | Interjection |
| 27. | VB | Verb, base form |
| 28. | VBD | Verb, past tense |
| 29. | VBG | Verb, gerund or present participle |
| 30. | VBN | Verb, past participle |
| 31. | VBP | Verb, non-3rd person singular present |
| 32. | VBZ | Verb, 3rd person singular present |
| 33. | WDT | Wh-determiner |
| 34. | WP | Wh-pronoun |
| 35. | WP$ | Possessive wh-pronoun |
<<<<<<< HEAD
<<<<<<< HEAD
| 36. | WRB | Wh-adverb |
=======
| 36. | WRB | Wh-adverb |
>>>>>>> 368ae98... documentation
=======
| 36. | WRB | Wh-adverb |
>>>>>>> b16835f... Update feature_development.md
