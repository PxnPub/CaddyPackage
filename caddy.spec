%global caddy_version 2.10.0
%global __strip /bin/true

Name      : caddy
Summary   : Web server with automatic HTTPS
Version   : %{caddy_version}.%{?build_number}%{!?build_number:x}
Release   : 1
BuildArch : x86_64
Packager  : PoiXson <support@poixson.com>
License   : AGPLv3+ADD-PXN-V1 and Apache-2.0
URL       : https://poixson.com/

BuildRequires: curl wget tar jq
BuildRequires: pxn-scripts
Provides: Caddy = %{caddy_version}

%define _rpmfilename  %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm
%global source_date_epoch_from_changelog 0
%define source_date_epoch 0

%description
Caddy is an extensible server platform that uses TLS by default.



%build
echo ; \uname -a ; echo
LATEST_CADDY_VERSION=$( \curl "https://api.github.com/repos/caddyserver/caddy/releases/latest"  \
	2>/dev/null | \jq '.tag_name' )
if [[ -z $LATEST_CADDY_VERSION ]]; then
	echo "Failed to get latest caddy version" ; exit 1
fi
LATEST_CADDY_VERSION="${LATEST_CADDY_VERSION//\"/}"
if [[ "$LATEST_CADDY_VERSION" != "v%{caddy_version}" ]]; then
	echo "Invalid latest version: $LATEST_CADDY_VERSION  expected: v%{caddy_version}" ; exit 1
fi
if [[ "$LATEST_CADDY_VERSION" != "v"* ]]; then
	echo "Invalid result getting latest caddy version: $LATEST_CADDY_VERSION" ; exit 1
fi
echo -e "\nCaddy version: %{caddy_version}\n"
if [[ -f "%{_topdir}/../v%{caddy_version}.linux-amd64.tar.gz" ]]; then
	echo -n "Found existing package: "
else
	echo "Downloading package.."
	\wget -O  \
		"%{_topdir}/../caddy-%{caddy_version}.linux-amd64.tar.gz"  \
		"https://github.com/caddyserver/caddy/releases/download/v%{caddy_version}/caddy_%{caddy_version}_linux_amd64.tar.gz"  \
			|| exit 1
fi
\cp -vf  \
	"%{_topdir}/../caddy-%{caddy_version}.linux-amd64.tar.gz"  \
	"%{_topdir}/BUILD/caddy.tar.gz"                            \
		|| exit 1



%install
echo
echo "Install.."
# create dirs
%{__install} -d  \
	"%{buildroot}%{_bindir}"                     \
	"%{buildroot}%{_sysconfdir}/caddy"           \
	"%{buildroot}%{_datadir}/licenses/%{name}/"  \
	"%{buildroot}%{_datadir}/doc/%{name}/"       \
		|| exit 1
# extract files
echo "Extracting.."
\pushd "%{buildroot}/" >/dev/null || exit 1
	\tar -zx  \
		--file="%{_topdir}/BUILD/caddy.tar.gz"  \
		--directory="%{buildroot}/"             \
			|| exit 1
\popd >/dev/null
# move files
\pushd  "%{buildroot}/"  >/dev/null  || exit 1
	\mv -v  "caddy"      "%{buildroot}%{_bindir}/"                    || exit 1
	\mv -v  "LICENSE"    "%{buildroot}%{_datadir}/licenses/%{name}/"  || exit 1
	\mv -v  "README.md"  "%{buildroot}%{_datadir}/doc/%{name}/"       || exit 1
\popd >/dev/null
# example files
\pushd  "%{_topdir}/../"  >/dev/null  || exit 1
	%{__install} -m 0644  \
		"Caddyfile.example"                  \
		"%{buildroot}%{_sysconfdir}/caddy/"  \
			|| exit 1
\popd >/dev/null



%files
%defattr(0644, root, root, 0755)
%license LICENSE
%doc README.md
# bin
%attr(0755,-,-) %{_bindir}/caddy
%dir %{_sysconfdir}/caddy
%{_sysconfdir}/caddy/Caddyfile.example
