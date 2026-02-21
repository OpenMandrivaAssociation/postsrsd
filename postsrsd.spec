Name:		postsrsd
Version:	2.0.11
Release:	1
Source0:	https://github.com/roehling/postsrsd/archive/%{version}/%{name}-%{version}.tar.gz
Summary:	Postfix sender rewriting scheme daemon
URL:		https://github.com/roehling/postsrsd
License:	GPL
Group:		Servers
BuildSystem:	cmake
BuildRequires:	cmake
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(libconfuse)
BuildOption:	-DUSE_SYSTEM_LIBS:BOOL=ON
BuildOption:	-DPOSTSRSD_CONFIGDIR=%{_sysconfdir}/postsrsd
BuildOption:	-DFETCHCONTENT_FULLY_DISCONNECTED:BOOL=ON
BuildOption:	-DGENERATE_SRS_SECRET:BOOL=OFF
BuildOption:	-DWITH_SQLITE:BOOL=ON
BuildOption:	-DPOSTSRSD_USER=postfix
BuildOption:	-DPOSTSRSD_GROUP=postfix
Requires:	postfix
Requires:	awk
Requires:	user(postfix)
Requires:	group(postfix)
Requires(post):	group(postfix)

%patchlist
postsrsd-use-system-libs.patch
postsrsd-hardening.patch
postsrsd-config.patch
postsrsd-dont-drop-privileges-if-already-dropped.patch

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
# We share the postfix user
rm -rf %{buildroot}%{_sysusersdir}

%post
if [[ ! -f %{_sysconfdir}/postsrsd/postsrsd.secret ]]; then
	mkdir -p %{_sysconfdir}/postsrsd
	dd if=/dev/urandom bs=24 count=1 2>/dev/null | base64 > %{_sysconfdir}/postsrsd/postsrsd.secret
	chmod 640 %{_sysconfdir}/postsrsd/postsrsd.secret
	chown root:postfix %{_sysconfdir}/postsrsd/postsrsd.secret
fi

%files
%dir %{_sysconfdir}/postsrsd
%ghost %attr(0644, root, postfix) %{_sysconfdir}/postsrsd/postsrsd.secret
%config(noreplace) %{_sysconfdir}/postsrsd/postsrsd.conf
%{_bindir}/postsrsd
%{_unitdir}/postsrsd.service
