# Translating the Nodezator project

Thank you for helping translate the project! This way many more people will be able to enjoy it. Your help is much, much appreciated.

> [!IMPORTANT]
> Only contribute manual translations, preferably but not necessarily for your native language (native people can always review your contributions later). Don't use automation tools.


## How to provide translations

Translations are stored in the `.txt` files in the `nodezator/data/translations` folder.

If you want to contribute translations, all you have to do is add a line with your translation anywhere under a line starting with `en-us`, with the same indentation.

For instance, to add a `pt_br` (Brazilian Portuguese) translation to the text below...

```
continue
    en-us Continue
new_game
    en-us New game
load_game
    en-us Load game
```

...all I had to do was add the translations like so:

```
continue
    en-us Continue
    pt-br Continuar
new_game
    en-us New game
    pt-br Novo jogo
load_game
    en-us Load game
    pt-br Carregar jogo
```

In other words, your line must start with the locale code for the corresponding language-region combo (just search the web for the locale code for your language/region). For instance, `pt_br` is the locale code for Brazilian Portuguese, in other words, Portuguese (`pt`) as spoken in Brazil (`br`). Then, the locale code must be followed by a space character and the translated text.

Also, don't worry about messing up the capitalization/formatting of the locale: you can write `pt-br`, `pt-BR`, `pt_br`, `pt_BR` or really any mix of capitalizations and underscore/hyphen. These language-region codes are preprocessed so they end up with the same capitalization/formatting.

The first translation must always be `en-us`, because it is the fallback value used when a translation is not found. You can add translations in any line under the ones starting with `en-us`, in any order.


## Not required but a welcome addition: providing sample text

Although not required, there's also another quick and helpful measure you can take regarding translations: provide sample text for the language you are adding.

This sample text is a just a short sentence in your language. For instance, you can add a common proverb or saying from that language. Just avoid using non-sensical dummy text (it is more fun when the text makes sense). It is used to preview typefaces (fonts) in multiple interfaces within Nodezator.

For `en-us` (English from USA), for instance, we use "The quick brown fox jumps over the lazy dog".

In the same `nodezator/data/translations` folder where you find the `.txt` files with the translations you'll also find a `sample_text.pyl` file. It is just a text file containing a Python dictionary with sample text for each locale code.

If there's no sample text for the locale code of the language you are adding translations for, just please add one there.


## Partial translations and other measures

You don't even need to translate everything if you are not sure about the translation of a specific word/sentence. Although we'd appreciate a lot if you provided a full translation for your language/region, as long as you contribute, someone can always come after and finish what you started.

I intend to add a check so languages missing translations will appear with a `*` near their locale code when they are listed in the user preferences, indicating partial support for that language/region. I also intend to add a script to help automate the task of finding and reporting missing translations so that people can easily and quickly identify missing translations.


## More formatting tips/demonstrations

### Indentation

All indentation must consist of spaces. No tabs or other white space must be used for indentation. Also, the number of spaces used must always be multiples of 4, that is, 0, 4, 8 and so on.

Okay:

```
thank_you
    en-us Thank you
    pt-br Obrigado
```

Not okay:

```
thank_you
  en-us Thank you
  pt-br Obrigado
```

### Translation order

As we said before, you can add translations in any line under the ones starting with `en-us`. The order of the translations below `en-us` doesn't matter, as long as `en-us` is the first (because it is used as the fallback for all languages).

For instance...

```
hello
    en-us Hello
    pt-br Olá
    de-de Hallo
```

...and...

```
hello
    en-us Hello
    de-de Hallo
    pt-br Olá
```

...are okay, as long as `en-us` comes first.


### Comments and empty lines

You can make liberal usage of comments and empty lines in the file if you think it will make the file more readable.

Comments are any lines whose first non-whitespace character is a `#`.

Example using empty lines and comments:

```

hello

    # there's no need to add punctuation here, as it isn't needed in the context
    # this will be used

    en-us Hello
    de-de Hallo
    pt-br Olá
    es-es Hola

```

### Template text

You may notice that some translations have the `{}` characters in it. This just means that translation is meant as a template and the `{}` characters represent placeholder elements that will be replaced in the final text by values provided by the application.

Whenever this is used in a translation it should be clear by the context which word(s) will be replacing the `{}` characters or there should be a comment explaining everything, so translating such sentences should be straightforward.

For instance:

```
hello_username

    # this sentence will be used to greet the user using the provided name;
    # for instance: "Hello, John!"

    en-us Hello, {}!
    pt-br Olá, {}!
```
