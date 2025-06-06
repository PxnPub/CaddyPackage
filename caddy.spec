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
BuildRequires: systemd, systemd-rpm-macros
Provides: Caddy = %{caddy_version}

%define _rpmfilename  %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm
%global source_date_epoch_from_changelog 0
%define source_date_epoch 0

%description
Caddy is an extensible server platform that uses TLS by default.



### Build ###
%build
echo -e "\nBuild..\n"$( \uname -a )"\n"
LATEST_CADDY_VERSION=$( \curl "https://api.github.com/repos/caddyserver/caddy/releases/latest"  \
	2>/dev/null | \jq '.tag_name' )
if [[ -z $LATEST_CADDY_VERSION ]]; then
	echo -e "\nFailed to get latest caddy version\n" ; exit 1
fi
LATEST_CADDY_VERSION="${LATEST_CADDY_VERSION//\"/}"
if [[ "$LATEST_CADDY_VERSION" != "v%{caddy_version}" ]]; then
	echo -e "\nInvalid latest version: $LATEST_CADDY_VERSION  expected: v%{caddy_version}\n" ; exit 1
fi
if [[ "$LATEST_CADDY_VERSION" != "v"* ]]; then
	echo -e "\nInvalid result getting latest caddy version: $LATEST_CADDY_VERSION\n" ; exit 1
fi
echo -e "\nCaddy version: %{caddy_version}\n"
if [[ -f "%{_topdir}/../caddy-%{caddy_version}.linux-amd64.tar.gz" ]]; then
	echo -e "\nFound existing package\n"
else
	echo -e "\nDownloading package.."
	\wget -O  \
		"%{_topdir}/../caddy-%{caddy_version}.linux-amd64.tar.gz"  \
		"https://github.com/caddyserver/caddy/releases/download/v%{caddy_version}/caddy_%{caddy_version}_linux_amd64.tar.gz"  \
			|| exit 1
fi
\cp -vf  \
	"%{_topdir}/../caddy-%{caddy_version}.linux-amd64.tar.gz"  \
	"%{_topdir}/BUILD/caddy.tar.gz"                            \
		|| exit 1



### Install ###
%install
echo -e "\nInstall..\n"
# create dirs
%{__install} -d  \
	"%{buildroot}%{_bindir}"                                          \
	"%{buildroot}%{_unitdir}"                                         \
	"%{buildroot}%{_presetdir}"                                       \
	"%{buildroot}%{_sysconfdir}/caddy"                                \
	"%{buildroot}%{_datadir}/licenses/%{name}/"                       \
	"%{buildroot}%{_datadir}/doc/%{name}/"                            \
	"%{buildroot}%{_localstatedir}/log/caddy/"                        \
	"%{buildroot}%{_sharedstatedir}/caddy/.config/"                   \
	"%{buildroot}%{_sharedstatedir}/caddy/.local/share/caddy/locks/"  \
		|| exit 1
# extract files
echo -e "\nExtracting..\n"
\pushd "%{_topdir}/BUILD/" >/dev/null || exit 1
	\tar -zx  \
		--file="%{_topdir}/BUILD/caddy.tar.gz"  \
		--directory="%{_topdir}/BUILD/"         \
			|| exit 1
	# bin file
	\mv -v  "caddy"  "%{buildroot}%{_bindir}/"  || exit 1
\popd >/dev/null
# copy files
\pushd  "%{_topdir}/../"  >/dev/null  || exit 1
	%{__install} -m 0644  "service/caddy.service"  "%{buildroot}%{_unitdir}/"    || exit 1
	%{__install} -m 0644  "service/caddy.preset"   "%{buildroot}%{_presetdir}/"  || exit 1
	%{__install} -m 0644  \
		"etc/caddy.env"                      \
		"etc/Caddyfile.example"              \
		"%{buildroot}%{_sysconfdir}/caddy/"  \
			|| exit 1
\popd >/dev/null



### Pre/Post ###
%pre
if [[ ! -e /etc/systemd/system-preset/ ]]; then
	\mkdir -v   /etc/systemd/system-preset  || exit 1
	\chmod 0755 /etc/systemd/system-preset  || exit 1
fi
\id  "caddy"  >/dev/null 2>/dev/null  || \
	\useradd --system --user-group  \
		--uid 808                  \
		--shell /sbin/nologin      \
		--home-dir /var/lib/caddy  \
		"caddy"  || exit 1

%post
%systemd_post  caddy.service
if [[ "$1" -eq 1 ]]; then
	/usr/bin/systemctl  start  caddy.service  || :
fi

%preun
%systemd_preun  caddy.service

%postun
%systemd_postun_with_restart  caddy.service
if [[ "$1" -eq 0 ]]; then
	\userdel --force  "caddy"
fi



### Files ###
%files
%defattr(0644, root, root, 0755)
%license LICENSE
%doc README.md
# bin
%attr(0755,-,-) %{_bindir}/caddy
# systemd
%{_unitdir}/caddy.service
%{_presetdir}/caddy.preset
# configs
%dir %{_sysconfdir}/caddy
%{_sysconfdir}/caddy/caddy.env
%{_sysconfdir}/caddy/Caddyfile.example
# logs
%attr(0755,caddy,caddy) %dir %{_localstatedir}/log/caddy
# config backups
%attr(0755,caddy,caddy) %dir %{_sharedstatedir}/caddy
%attr(0755,caddy,caddy) %dir %{_sharedstatedir}/caddy/.config
# locks
%attr(0755,caddy,caddy) %dir %{_sharedstatedir}/caddy/.local
%attr(0755,caddy,caddy) %dir %{_sharedstatedir}/caddy/.local/share
%attr(0755,caddy,caddy) %dir %{_sharedstatedir}/caddy/.local/share/caddy
%attr(0755,caddy,caddy) %dir %{_sharedstatedir}/caddy/.local/share/caddy/locks
