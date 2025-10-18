This is a local Windows-based converter from CodeForces Polygon problem package format to BACS archive / Sybon.org archive format.

## User manual

1. Check `bacs_converter_settings.py`
2. Drop zip archives of Standart Polygon packages into `input` folder
3. Run `bacs_converter.py`
4. If `bacs_converter.py` finished with an error, then current package conversion was interrupted. Fix errors, clear the `output` folder and run `bacs_converter.py` again
5. Collect BACS packages from `output` folder

## Prerequisites

In order to run this you need installed and command-line configured:
- Python 3.10 or later
- GCC (typically MiwGW) supporting C++20 or later

For majority of the problems this should be enough. However for any language (other than C++ and Python3) used in Polygon problem source files you have to have this language installed and configured. E. g. if problem uses solutions/generators/validators in Rust, you have to be able to compile and run Rust programs. If problem uses Java/Kotlin --- you need Java/Kotlin, if problem uses Pascal --- you need Pascal, etc.

## Settings

## Development notes
