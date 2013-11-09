Name:           python-qutepart
Version:        1.1.0
Release:        1%{?dist}
Summary:        Code editor widget for PyQt
Summary(es):    Componente de edición de código fuente basado en Qt
Group:          Development/Libraries/Python

License:        GPL-2.0
URL:            https://github.com/hlamer/qutepart

Source0:        https://github.com/hlamer/qutepart/archive/v%{version}.tar.gz#/qutepart-%{version}.tar.gz

BuildRequires:  pcre-devel
BuildRequires:  python-devel
Requires:       python >= 2.7
Requires:       pcre


%if 0%{?fedora_version}
BuildRequires:  PyQt4
Requires:       PyQt4
%else
BuildRequires:  python-qt4
Requires:       python-qt4
%endif



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

%description -l es
Qutepart usa el resaltado de sintaxis de Kate (ficheros XML), contiene una
traducción de Javascript a Python de las herramientas de sangrado de Kate (12%
del código base en la versión 1.0.0), y no contiene código de Katepart.

No hay nada de malo en Katepart. Qutepart ha sido creado para poder reutilizar
las herramientas de resaltado y sangrado en proyectos donde la dependencia de
KDE es inaceptable.


%prep
%setup0 -q -n qutepart-%{version}


%build
%{__python} setup.py build


%install
%{__python} setup.py install --skip-build --prefix=%{_prefix} --root %{buildroot}


%files
%defattr(-,root,root)
%doc LICENSE README.md
%{python_sitearch}/qutepart*


%changelog
* Sun Sep 8 2013 Jairo Llopis <yajo.sk8@gmail.com>  1.1.0-1
- Initial release.
