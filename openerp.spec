%define     oe_rel 20130408-234645
            # tarball's source directory,
%define     oe_src_dir openerp-%{version}-%{oe_rel}

Name:       openerp
Version:    6.1
Release:    1	
            # See LICENSING
License:    AGPLv3 and GPLv3 and BSD and LGPLv2+
Group:      Networking/WWW
Summary:    Business Applications Server
URL:        https://www.openerp.com
BuildArch:  noarch
Source0:    http://nightly.openerp.com/6.1/nightly/src/openerp-%{version}-%{oe_rel}.tar.gz
Source1:    openerp.service
Source2:    openerp-gen-cert
Source3:    README.omv
Source4:    LICENSING
            # https://bugs.launchpad.net/bugs/993408
Patch0:     openerp-fsf-fix.patch
            # Patch is not usable upstream.
Patch1:     openerp-unbundle-pyftpdlib.patch
            # Relicensed by copyright owner, see
            # https://bugzilla.redhat.com/show_bug.cgi?id=693425#c57
Patch10:    openerp-server-relicense-dict_tools-to-LGPL2.1.patch

Requires:   ghostscript
Requires:   postgresql-python
Requires:   pychart
Requires:   pydot
Requires:   pyftpdlib
Requires:   pyparsing
Requires:   pywebdav
Requires:   python-babel
Requires:   python-dateutil
# See BZ 817268
# Requires:   python-faces
Requires:   python-feedparser
Requires:   python-gdata
Requires:   python-imaging
Requires:   python-ldap
Requires:   python-lxml
Requires:   python-mako
Requires:   python-openid
Requires:   python-psycopg2
Requires:   python-reportlab
Requires:   python-simplejson
# https://fedorahosted.org/fpc/ticket/171
#Requires:  python-trml2pdf
Requires:   python-vatnumber
Requires:   python-vobject
Requires:   python-werkzeug
Requires:   python-xlwt
Requires:   python-ZSI
Requires:   pytz
Requires:   PyYAML

Obsoletes:  openerp-mpl  <= %{version}
Provides:   openerp6
Provides:   openerp-server

BuildRequires:  desktop-file-utils
BuildRequires:  python-libxslt
BuildRequires:  pkgconfig(pygtk-2.0)
BuildRequires:  python-openbabel
BuildRequires:  python-setuptools

BuildRequires:  python-devel
BuildRequires:  systemd-units

Requires(pre):    rpm-helper
Requires(post):   rpm-helper
Requires(preun):  rpm-helper
Requires(postun): rpm-helper


%description
Server package for OpenERP.

OpenERP is a free Enterprise Resource Planning and Customer Relationship
Management software. It is mainly developed to meet changing needs.

The main functional features are: CRM & SRM, analytic
and financial accounting, double-entry stock management,
sales and purchases management, tasks automation,
help desk, marketing campaign, ... 
and vertical modules for very specific businesses.

Technical features include a distributed server, flexible work-flows, an object
database, dynamic GUIs, custom reports, NET-RPC and XML-RPC interfaces, ...

For more information, please visit: http://www.openerp.com

This server package contains the core (server) of OpenERP system and all
additions of the official distribution. You may need the GTK client to connect
to this server, or the web-client, which serves to HTML browsers. You can
also find more additions (aka. modules) for this ERP system in:
http://www.openerp.com/ or  http://apps.openerp.com/


%prep
%setup -q -n %{oe_src_dir}
%patch0 -p1
%patch1 -p1
%patch10 -p1

# https://bugs.launchpad.net/bugs/993414
find . -name \*.py -a -perm 644 | \
    xargs sed -i -e '\;/usr/bin/env;d' -e '\;/usr/bin/python;d'
find . -name \*.html -o -name \*yml -o -name \*.js -o -name \*.po  \
    -o -name \*.css -o -iname readme* -o -name \*.csv \
    -o -name account_asset_change_duration.py \
    -o -name input_complete \
    -o -name base_quality_interrogation.py |
        xargs chmod 644
chmod 644 $( find openerp/addons/account_asset -name \*.py )
chmod 644       openerp/addons/l10n_ch/test/test*.v11

find . -name \*.html | xargs sed -i 's/\r//'
sed -i 's/\r//' openerp/addons/l10n_ch/test/test*.v11
sed -i 's/\r//' openerp/addons/account_asset/security/ir.model.access.csv

find . -name .hg_* | xargs rm -f
rm -f openerp/addons/.bzrignore

# Empty and of no use.
rm openerp/addons/base_report_designer/openerp_sxw2rml/office.dtd

# Prebuilt binaries, bundled libs and foreign packaging
rm -rf win32 debian setup.nsi
rm -rf bin/pychart
rm -rf openerp/addons/outlook/plugin/openerp-outlook-addin.exe \
       openerp/addons/thunderbird openerp/addons/plugin_thunderbird

# Client-side plugin, until we can build it under Fedora.
rm -rf openerp/addons/outlook/plugin/

%build
NO_INSTALL_REQS=1 python ./setup.py --quiet build

%install
python ./setup.py --quiet install --root=%{buildroot}
sed -i "s|%{buildroot}||" %{buildroot}%{_bindir}/openerp-server
rm  %{buildroot}/usr/openerp/.apidoc
rm -r  %{buildroot}%{python_sitelib}/openerp
mv %{buildroot}/usr/openerp %{buildroot}%{python_sitelib}
install -m 644 -D install/openerp-server.conf  \
    %{buildroot}%{_sysconfdir}/openerp/openerp-server.conf
install -d %{buildroot}%{_sysconfdir}/openerp/start.d
install -d %{buildroot}%{_sysconfdir}/openerp/stop.d

install -D -m 755 %SOURCE2 %{buildroot}%{_sbindir}/openerp-gen-cert
install -D -m 644 %SOURCE1 %{buildroot}%{_unitdir}/openerp.service
install -m 644  %{SOURCE3} %{SOURCE4} .

install -m 644 openerp/import_xml.rng %{buildroot}%{python_sitelib}/openerp
install -d %{buildroot}%{python_sitelib}/openerp/addons/base/security
install -m 644 openerp/addons/base/security/* \
    %{buildroot}%{python_sitelib}/openerp/addons/base/security

install -d %{buildroot}/%{_datadir}/openerp/pixmaps
install -m 644 -D install/*.png  %{buildroot}/%{_datadir}/openerp/pixmaps

install -D -m 644 install/openerp-server.1 \
    %{buildroot}/%{_mandir}/man1/openerp-server.1
install -D -m 644 install/openerp_serverrc.5 \
    %{buildroot}/%{_mandir}/man5/openerp-serverrc.5

install -d %{buildroot}%{_localstatedir}/spool/openerp
install -d %{buildroot}%{_localstatedir}/run/openerp

rm -f %{buildroot}%{python_sitelib}/openerp/addons/wiki/controllers/wiki.py
rm -f %{buildroot}%{python_sitelib}/openerp/addons/wiki/widgets/wiki.py*

%pre
%_pre_useradd %{name} /var/run/openerp /bin/false
%_pre_groupadd %{name}

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
%_postun_userdel %{name}
%_postun_groupdel %{name}

%files
%doc LICENSE README  README.omv LICENSING
%{_bindir}/*
%{_sbindir}/*
%{_unitdir}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_datadir}/openerp
%{python_sitelib}/openerp
%{python_sitelib}/openerp-%{version}*-py%{python_version}.egg-info
%attr(0755,openerp,openerp) %{_localstatedir}/run/openerp
%attr(0755,root,openerp) %dir %{_sysconfdir}/openerp
%dir %{_sysconfdir}/openerp/start.d
%dir %{_sysconfdir}/openerp/stop.d
%attr(0660,root,openerp)  %config(noreplace) %{_sysconfdir}/openerp/openerp-server.conf
