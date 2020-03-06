# Code editor component for PyQt5

**NOTE** wheels released on PyPi doesn't contain C extension which speedups long file hihglighting.
Build Qutepart from sources if speed is critical for your project. You can help releasing binary parser by implementing [this issue](https://github.com/andreikop/qutepart/issues/85)

Component has been created for [Enki editor](http://enki-editor.org)

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
* Rectangular selection and copy-paste
* Vim mode

## Qutepart and Katepart
[Kate](http://kate-editor.org/) and Katepart (an editor component) is really cool software. The Kate authors and community have created, probably, the biggest set of highlighters and indenters for programming languages.

* Qutepart uses Kate syntax highlighters (XML files)
* Qutepart contains a port from Javascript to Python of Kate indenters (12% of the code base in version 1.0.0)
* Qutepart doesn't contain Katepart code.

Nothing is wrong with Katepart. Qutepart has been created to enable reusing highlighters and indenters in projects where a KDE dependency is not acceptable.

## Author
Andrei Kopats
[andrei.kopats@gmail.com](mailto:andrei.kopats@gmail.com)

## Bug reports, patches
[Github page](https://github.com/andreikop/qutepart)

## License
LGPL v2
