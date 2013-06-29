# Code editor component for PyQt and Pyside

Component has been created for [Enki editor](http://enki-editor.org) as replacement for [QScintilla](http://www.riverbankcomputing.com/software/qscintilla/intro)

[API documentation](https://qutepart.readthedocs.org/en/latest/)

## Features
* Syntax highlighting for 196 languages
* Smart indentation for many languages
* Line numbers
* Bookmarks
* Advanced edit operations
* Matching braces highlighting
* Autocompletion based on document content
* Marking too long lines with red line

## Building and installation
#### 1. Install [pcre](http://www.pcre.org/) and development files
On Debian, Ubuntu and other Linuxes install package ``libpcreX-dev``, where ``X`` is available in your distribution pcre version.
For other OSes - see instructions on pcre website

#### 2. Install Python development files
On Debian, Ubuntu and other Linuxes install package ``python-dev``, on other systems - see Python website

#### 3. Install C compiler
It will probably be gcc

#### 4. Build and install the package
``python setup.py install``

## Qutepart and Katepart
[Kate](http://kate-editor.org/) and Katepart (an editor component) is really cool software. Kate authors and comunity has created, probably, the biggest set of highlighters and indenters for programming languages.

* Qutepart uses kate syntax highlighters (XML files)
* Qutepart contains port from Javascript to Python of Kate indenters (12% of the code base in version 1.0.0)
* Qutepart doesn't contain Katepart code.

Nothing is wrong with Katepart. Qutepart has been created for possibility to reuse highlighters and indenters in projects, where KDE dependency is not acceptable.

## Author
Andrei Kopats
[hlamer@tut.by](mailto:hlamer@tut.by)

## Bug reports, patches
[Github page](https://github.com/hlamer/qutepart)

## License
LGPL v2
