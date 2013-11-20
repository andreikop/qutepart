Name:           python-qutepart
Version:        1.1.1
Release:        1%{?dist}
Summary:        Code editor widget for PyQt
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
- Initial RPM release

* Wed Nov 20 2013 Andrei Kopats <hlamer@tut.by>  1.1.1-1
- RPM release for Suse
- Highlight XXX alert
- Bugfixes
