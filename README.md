# Serapis

Serapis is an acquisition, mining, and modeling pipeline that takes undefined words from [Wordnik's](http://wordnik.com) dictionary, finds occurences of them across the web, and determines whether the sentence in which they occur offers an in-context definition of the word.

For example, this sentence is a free-range definition, or "FRD", for "cheeseor":

```
The term “cheeseors” describes flighted globules of intergalactic cheese, known to be the scourge of the asteroid belt.
```

### Pipeline Schematic

![layout](https://cloud.githubusercontent.com/assets/1047165/11378714/6e279848-92a1-11e5-9e22-fdf49143c805.png)

It uses a standard [message format](https://github.com/summerAI/serapis/wiki/Message-Format) throughout an Amazon Lambda pipeline.

### Modeling Sentences

High-level details on the feature development and production can be found in the slides from Clare's [presentation on building this system](http://www.slideshare.net/ClareCorthell/distributed-natural-language-processing-systems-in-python).

The system requires a model to score sentences for FRDness (scores: binary classification, classification confidence) which is not included here.

### Setup and Troubleshooting

Please read the [Wiki](https://github.com/summerAI/wordnik/wiki) for help with setting up your code base. Use the pipes at your own risk.

### Contribution

Serapis was created for [Wordnik](http://wordnik.com) by the [summer.ai](http://summer.ai) team, [Clare Corthell](https://github.com/clarecorthell) and [Manuel Ebert](https://github.com/mebert) in 2015/2016.
