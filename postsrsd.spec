Name:		postsrsd
Version:	2.4.1
Release:	1
Source0:	https://github.com/roehling/postsrsd/archive/%{version}/%{name}-%{version}.tar.gz
Summary:	Postfix sender rewriting scheme daemon
URL:		https://github.com/roehling/postsrsd
License:	GPL-3.0-only
Group:		Servers
BuildSystem:	cmake
BuildRequires:	cmake
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(libconfuse)
BuildRequires:	pkgconfig(check)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	python
# 2.4 fetches bundled deps unless find_package is forced. No network in the build.
BuildOption:	-DFETCHCONTENT_FULLY_DISCONNECTED:BOOL=ON
BuildOption:	-DFETCHCONTENT_TRY_FIND_PACKAGE_MODE=ALWAYS
BuildOption:	-DPOSTSRSD_CONFIGDIR=%{_sysconfdir}/postsrsd
BuildOption:	-DGENERATE_SRS_SECRET:BOOL=OFF
BuildOption:	-DINSTALL_SYSTEMD_SYSUSERS:BOOL=OFF
BuildOption:	-DWITH_SQLITE:BOOL=ON
BuildOption:	-DPOSTSRSD_USER=postfix
Requires:	postfix
Requires:	awk
Requires:	user(postfix)
Requires:	group(postfix)
Requires(post):	group(postfix)

%patchlist
# dropped (no longer applies): postsrsd-use-system-libs.patch
# dropped (no longer applies): postsrsd-hardening.patch
# dropped (no longer applies): postsrsd-config.patch
# dropped (no longer applies): postsrsd-dont-drop-privileges-if-already-dropped.patch

%description
The Sender Rewriting Scheme (SRS) is a technique to forward mails from domains
which deploy the Sender Policy Framework (SPF) to prohibit other Mail Transfer
Agents (MTAs) from sending mails on their behalf. With SRS, an MTA can
circumvent SPF restrictions by replacing the envelope sender with a temporary
email address from one of their own domains. This temporary address is bound
to the original sender and only valid for a certain amount of time, which
prevents abuse by spammers.

%install -a
mkdir -p %{buildroot}%{_sysconfdir}/postsrsd
mv %{buildroot}%{_docdir}/postsrsd/postsrsd.conf %{buildroot}%{_sysconfdir}/postsrsd/
rmdir %{buildroot}%{_docdir}/postsrsd
# We share the postfix user
rm -rf %{buildroot}%{_sysusersdir}

%check
ctest --test-dir _OMV_rpm_build --output-on-failure

%post
if [[ ! -f %{_sysconfdir}/postsrsd/postsrsd.secret ]]; then
	mkdir -p %{_sysconfdir}/postsrsd
	dd if=/dev/urandom bs=24 count=1 2>/dev/null | base64 > %{_sysconfdir}/postsrsd/postsrsd.secret
	chmod 640 %{_sysconfdir}/postsrsd/postsrsd.secret
	chown root:postfix %{_sysconfdir}/postsrsd/postsrsd.secret
fi

%files
%dir %{_sysconfdir}/postsrsd
%ghost %attr(0640, root, postfix) %{_sysconfdir}/postsrsd/postsrsd.secret
# The chroot jail: upstream's unit names it in ReadWritePaths=, and systemd
# refuses to start the service when it is missing (226/NAMESPACE). CMake
# creates it in the buildroot, but an unlisted empty directory is dropped.
%dir %attr(0755, root, root) %{_localstatedir}/lib/postsrsd
%config(noreplace) %{_sysconfdir}/postsrsd/postsrsd.conf
%{_bindir}/postsrsd
%{_unitdir}/postsrsd.service
