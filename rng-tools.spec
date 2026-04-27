Name:           rng-tools
Version:        6.17
Release:        1%{?dist}
Summary:        Random number generator related utilities
License:        GPLv2+
URL:            https://github.com/pcbennion/rng-tools
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  autoconf automake make gcc
BuildRequires:  openssl-devel libcap-devel libxml2-devel
BuildRequires:  libcurl-devel jansson-devel

Requires:       openssl libcap libxml2 libcurl jansson
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
rng-tools provides rngd, a daemon that feeds entropy from hardware RNG
sources into the kernel's random pool, and rngtest for FIPS 140-2 testing.

%prep
%autosetup

%build
./autogen.sh
%configure \
    --without-pkcs11 \
    --without-rtlsdr \
    --without-radiacode
%make_build

%install
%make_install
install -D -m 0644 rngd-qrypt.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/rngd-qrypt
install -d -m 0755 %{buildroot}%{_sysconfdir}/rngd

%post
%systemd_post rngd.service

%preun
%systemd_preun rngd.service

%postun
%systemd_postun_with_restart rngd.service

%files
%license COPYING
%doc AUTHORS ChangeLog README.md README.qrypt-rpm.md
%{_sbindir}/rngd
%{_bindir}/rngtest
%{_mandir}/man8/rngd.8*
%{_mandir}/man1/rngtest.1*
%{_unitdir}/rngd.service
%dir %{_sysconfdir}/rngd
%config(noreplace) %{_sysconfdir}/sysconfig/rngd-qrypt

%changelog
* Thu Apr 24 2025 Ryan Mandich <ryan@qrypt.com> - 6.17-1
- Initial package for add-tls-configs branch