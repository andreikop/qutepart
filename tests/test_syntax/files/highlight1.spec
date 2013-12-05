# Test file for rpmspec.xml

# Comments start with a # in column="0":

# Some comment

# When they don't start in column="0", that they are recognized as comments, but with an alert:
 # This is a bad comment.
# RPM spec says clear that comments must start at the begin of the line. However, in practice
# the RPM software is more permissive, depending on the context. But for our syntax highlighting,
# we give, while recognizing the as comment, at least a little alert. Comments should not contain
# the character % (which is marked as warning), but 2 of them are okay: %%. TODO is higlighted.

# A spec file starts with "Normal" context. Here, you can specify values for some tags:
Name:                kradioripper-unstable # Note that here in no comment possible!
Name:                name only _one_ word allowed
Name:                %macro no further syntax check after macro!
# Some tags support only _one_ word as value
Version:             0.4test5 up-from-the-space-this-is-an-error
# Some tag can have parameters: Any char in paranthesis:
Summary:             Recorder for internet radios (based on Streamripper)  
Summary(de.UTF-8):   Aufnahmeprogramm für Internetradios (basiert auf Streamripper)
# requiere free text:
License:             License 1 2 3
# requiere a well defines value:
Requires( / (  = ):  Some, value()
# new type "switch" accepts: yes, no, 0, 1
AutoReq: yes
AutoReq: yes invalid
AutoReq: %macro no further syntax check after macro!
AutoReq: no
AutoReq: 0
AutoReq: 1
# requiere a number:
Epoch:               123123
Epoch:               123123 invalid
Epoch:               %macro no further syntax check afer macro!
# If tags are used that are not known, they are not highlighted:
Invalidtag:          Some value
Invalid content in this section (only tags are allowed)
  
# You can use conditions in specs (highlighted with region markers):
%if 0%{?mandriva_version}  
# numbers and strings are distingished: string:
%if lsdksfj
# number:
%if 23472398
# string:
%if lksdjfsl72939
# invalid:
%if 92437lsdkfjdsl
# valid:
%if "lsdfj %ksdf(sdfs) 3489"
Release:             %mkrel 1.2
%else  
Release:             0  
%endif  
# requiere a well defined value:
%ifos fixed_value
# You must use these special macros (%%if etc.) always at the start of the line - if not,
# that's bad but not an arror. You must also always use the specified form. Everything else is an
# error:
 %if
something %if
%{if}
%if(some options)
# However, this are different macros and therefore correct:
%ifx
%{ifx}
%ifx(some options)

# the \ is escaped in the line. At the end of the line it escapes the line break:
echo This is \" a text \\ and here\
it continues.

%define name value
%define invalid_näme value
%define macroname multi\
line content with references like %0 %* %# %{-f} %{-f*} %1 %2 and so on
%global name value
%global invalid_näme value
%undefine name
%undefine name too-many-parameters

# This special comment is treated and highlighted like a tag:
# norootforbuild  
# It can't have parameters, so every following non-whitespace character is not good:
# norootforbuild  DONT WRITE ANYTHING HERE!
# wrong spacing is also recognized:
#  norootforbuild
# and also an indeet is not fine for norootforbuild:
 # norootforbuild
  
# This following "Conflicts" tag will be removed by set-version.sh,  
# if it is a "kradioripper" release (and not a "kradioripper-unstable" release)...  
Conflicts:           kradioripper  
  
  
%description  
# Here, a new section starts. It contains a value for the RPM field "description" and is therefor
# colored like values:
A KDE program for ripping internet radios. Based on StreamRipper.  
  
  
# A section start can have parameters:
%description -l de.UTF-8  
Ein KDE-Aufnahmeprogramm für Internetradios. Basiert auf StreamRipper.   
  
# These sections starts are errors:
 %description not at the first line
%{description} wrong form
%description(no options allowed, only parameters!)
  
  
%prep  
# This starts a section that defines the commands to prepare the build.
# q means quit. n sets the directory:  
%setup -q -n kradioripper  
echo Test
# Macros can have different forms: Valid:
%abc
%abcÄndOfMacro
%abc(def)EndOfMacro
%{abc}EndOfMacro
%{something but no single %}EndOfMacro
%{abc:def}EndOfMacro
%(abc)
# Invalid:
%ÄInvalidChar
%
%)
%}
# You can use macros inside of macro calls: Fine:
%{something %but no %{sin%(fine)gle} }EndOfMacro
# Bad:
%{No closing paranthesis (No syntax highlightig for this error available)
  
  
%build  
cmake ./ -DCMAKE_INSTALL_PREFIX=%{_prefix}  
%__make %{?jobs:-j %jobs}  
  
  
%install  
%if 0%{?suse_version}  
%makeinstall  
%suse_update_desktop_file kradioripper  
%endif  
%if 0%{?fedora_version} || 0%{?rhel_version} || 0%{?centos_version}  
make install DESTDIR=%{buildroot}  
desktop-file-install --delete-original --vendor fedora --dir=%{buildroot}/%{_datadir}/applications/kde4 %{buildroot}/%{_datadir}/applications/kde4/kradioripper.desktop  
%endif  
%if 0%{?mandriva_version}  
%makeinstall_std  
%endif  
  
  
%clean  
rm -rf "%{buildroot}"  
  
  
%files  
%defattr(-,root,root)  
%if 0%{?fedora_version} || 0%{?rhel_version} || 0%{?centos_version}  
%{_datadir}/applications/kde4/fedora-kradioripper.desktop  
%else  
%{_datadir}/applications/kde4/kradioripper.desktop  
%endif  
%{_bindir}/kradioripper  
%{_datadir}/locale/*/LC_MESSAGES/kradioripper.mo  
%if 0%{?mandriva_version}  
# TODO The %%doc macro is actually broken for mandriva 2009 in build service...
%dir %{_datadir}/apps/kradioripper  
%{_datadir}/apps/kradioripper/*  
%else  
%doc COPYING LICENSE LICENSE.GPL2 LICENSE.GPL3 NEWS WARRANTY  
%dir %{_datadir}/kde4/apps/kradioripper  
%{_datadir}/kde4/apps/kradioripper/*  
%endif  
  
  
%changelog  
* Sun May 04 2008 email@email.com
- some text
- some text
  in two lines
- some text
  in two lines
  + with subtext
  - and more subtext
  in two lines
* Tue Apr 24 2007 Name
- text
  * When the star isn't at column 0, than it doesn't indicate
  a new date
* Wen Sep 08 2003 Wrong weekday
* Mon Mai 08 2003 Wrong month
* Mon Sep 0 2003 bad day
* Mon Sep 8 2003 good day
* Mon Sep 08 2003 good day
* Mon Sep 32 2003 bad day
* Mon Sep 08 03 bad year
* Mon Sep 08 2003 Name
# When using macros, the error check is disabled:
* %myDataMacro Title of the entry
- Text
    - can
        - be
        - indeeded
        - without
    - problems

