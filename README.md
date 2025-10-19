This is a local Windows-based converter from CodeForces Polygon problem package
format to BACS archive / Sybon.org archive format.

## User manual

1. Check `bacs_converter_settings.py`
2. Drop zip archives of **Standard** Polygon packages into `input` folder
3. Run `bacs_converter.py`
4. If `bacs_converter.py` finished with an error, then current package conversion was interrupted. Fix errors, clear the `output` folder and run `bacs_converter.py` again
5. Collect BACS packages from `output` folder

## Requirements

In order to run this you need installed and command-line configured:
- Python 3.10 or later
- GCC (typically MinGW) supporting C++20 or later

For the majority of the problems this should be enough.
However, for any language used in Polygon problem source files
that are used during `doall.bat`
you have to have this language installed and configured.
E.g. if problem uses solutions/generators/validators in Rust,
you have to be able to compile and run Rust programs.
If problem uses Java/Kotlin — you need Java/Kotlin etc.

## Settings

Those are configured in `bacs_converter_settings.py`

`NAME_PREFIX` — prefix added to the converted problem name

`NAME_SUFFIX` — suffix added to the converted problem name

`MAIN_LANG` — language name, that will be used as main for converted package.
Currently, this only affects `config.ini > info > name`.
Converter will preserve all files and create a localization for all languages 
configured in the Polygon package.

`MAINTAINERS_LIST` — defines `config.ini > info > maintainers`. List of BACS usernames,
who will be associated with this problem.

## Development notes

BACS package `misc` folder can contain anything.

BACS package `statement` folder can contain anything.
This whole folder will then be statically served to clients requesting the problem statement.
`*.ini` files will only define the entry point to this folder.
This is way more powerful than CF Polygon / CodeForces statement system,
as it allows to provide any static front-end application as a problem statement.

Sybon.org and BACS are not well aligned on test naming policies.
E.g. tests `1` and `01` are different. In order to avoid issues all leading zeroes
should be removed from test names and test numeration should start with 1.

Polygon uses weird list of languages including 'Other'. As of [19.10.25] Sybon.org just uses 3
predefined options: ru, en, es. They are glued together in this converter according to 
[ISO-639](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes).
