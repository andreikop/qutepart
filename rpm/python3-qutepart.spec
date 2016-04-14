Name:           python3-qutepart
Version:        3.0.0
Release:        1%{?dist}
Summary:        Code editor widget for PyQt
Group:          Development/Libraries/Python

License:        GPL-2.0
URL:            https://github.com/hlamer/qutepart

Source0:        https://github.com/hlamer/qutepart/archive/v%{version}.tar.gz#/qutepart-%{version}.tar.gz

BuildRequires:  pcre-devel
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3
Requires:       pcre
Requires:       python3-qt5


%description
Qutepart is a code editor widget for PyQt. Features:
    - Syntax highlighting for 196 languages
    - Smart indentation for many languages
    - Line numbers
    - Bookmarks
    - Advanced edit operations
    - Matching braces highlighting
    - Autocompletion based on document content
    - Marking too long lines with red line
    - Rectangular selection and copy-paste
    - Linter marks support
    - Vim mode


%prep
%setup0 -q -n qutepart-%{version}


%build
/usr/bin/python3  setup.py build


%install
/usr/bin/python3  setup.py install --skip-build --prefix=%{_prefix} --root %{buildroot}


%files
%defattr(-,root,root)
%doc LICENSE README.md
%{python3_sitearch}/qutepart*


%changelog
* Fri Mar 25 2016 Andrei Kopats <hlamer@tut.by>  3.0.0-11
- Migration to Python3

* Wed Nov 11 2015 Andrei Kopats <hlamer@tut.by>  2.2.3-10
- Vim Overwrite mode fix
- Italic font rendering fix

* Sat May 30 2015 Andrei Kopats <hlamer@tut.by>  2.2.2-9
- Fixed Python indenter exception

* Wed May 27 2015 Andrei Kopats <hlamer@tut.by>  2.2.1-8
- Rust syntax by Rust team
- Do not strip trailing empty lines

* Wed Mar 25 2015 Andrei Kopats <hlamer@tut.by>  2.2.0-7
- Vim mode

* Mon Aug 18 2014 Andrei Kopats <hlamer@tut.by>  2.1.2-6
- Fix CPU load management

* Mon Aug 04 2014 Andrei Kopats <hlamer@tut.by>  2.1.1-5
- Crash fix

* Tue Jul 22 2014 Andrei Kopats <hlamer@tut.by>  2.1.0-4
- API: Linter marks
- API: drawWhiteSpaceTrailing -> drawIncorrectIndentation, drawWhiteSpaceAnyIndentation -> drawAnyWhitespace
- API: increaseIndentAction, undoAction, redoAction
- API: Updated XML parsers. More languages are supported.
- Better autoindentation for Python

* Fri Mar 14 2014 Andrei Kopats <hlamer@tut.by>  1.3.0-3
- Bugfixes and improvements
- API: Added binaryParserAvailable flag
- API: Added indentWithSpaceAction, unIndentWithSpaceAction

* Wed Nov 20 2013 Andrei Kopats <hlamer@tut.by>  1.1.1-2
- RPM release for Suse
- Highlight XXX alert
- Bugfixes

* Sun Sep 8 2013 Jairo Llopis <yajo.sk8@gmail.com>  1.1.0-1
- Initial RPM release
