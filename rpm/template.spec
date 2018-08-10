Name:           ros-indigo-multimaster-fkie
Version:        0.8.2
Release:        0%{?dist}
Summary:        ROS multimaster_fkie package

Group:          Development/Libraries
License:        BSD
URL:            http://ros.org/wiki/multimaster_fkie
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       ros-indigo-default-cfg-fkie
Requires:       ros-indigo-master-discovery-fkie
Requires:       ros-indigo-master-sync-fkie
Requires:       ros-indigo-multimaster-msgs-fkie
Requires:       ros-indigo-node-manager-fkie
BuildRequires:  ros-indigo-catkin

%description
The metapackage to combine the nodes required to establish and manage a
multimaster network. This requires no or minimal configuration. The changes are
automatically detected and synchronized.

%prep
%setup -q

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/indigo/setup.sh" ]; then . "/opt/ros/indigo/setup.sh"; fi
mkdir -p obj-%{_target_platform} && cd obj-%{_target_platform}
%cmake .. \
        -UINCLUDE_INSTALL_DIR \
        -ULIB_INSTALL_DIR \
        -USYSCONF_INSTALL_DIR \
        -USHARE_INSTALL_PREFIX \
        -ULIB_SUFFIX \
        -DCMAKE_INSTALL_LIBDIR="lib" \
        -DCMAKE_INSTALL_PREFIX="/opt/ros/indigo" \
        -DCMAKE_PREFIX_PATH="/opt/ros/indigo" \
        -DSETUPTOOLS_DEB_LAYOUT=OFF \
        -DCATKIN_BUILD_BINARY_PACKAGE="1" \

make %{?_smp_mflags}

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/indigo/setup.sh" ]; then . "/opt/ros/indigo/setup.sh"; fi
cd obj-%{_target_platform}
make %{?_smp_mflags} install DESTDIR=%{buildroot}

%files
/opt/ros/indigo

%changelog
* Fri Aug 10 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.2-0
- Autogenerated by Bloom

* Fri Aug 03 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.1-0
- Autogenerated by Bloom

* Mon Jul 16 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.0-0
- Autogenerated by Bloom

* Sat Mar 24 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.8-0
- Autogenerated by Bloom

* Fri Oct 27 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.7-0
- Autogenerated by Bloom

* Wed Oct 04 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.6-0
- Autogenerated by Bloom

* Tue Jul 25 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.5-0
- Autogenerated by Bloom

* Wed May 03 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.4-0
- Autogenerated by Bloom

* Mon Apr 24 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.3-0
- Autogenerated by Bloom

* Fri Jan 27 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.2-0
- Autogenerated by Bloom

* Tue Jan 10 2017 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.7.0-0
- Autogenerated by Bloom

* Tue Nov 15 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.6.2-0
- Autogenerated by Bloom

* Tue Oct 18 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.6.1-0
- Autogenerated by Bloom

* Wed Oct 12 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.6.0-0
- Autogenerated by Bloom

* Sat Sep 10 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.8-0
- Autogenerated by Bloom

* Thu Sep 01 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.6-0
- Autogenerated by Bloom

* Tue Aug 30 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.5-0
- Autogenerated by Bloom

* Thu Apr 21 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.4-0
- Autogenerated by Bloom

* Fri Apr 01 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.3-0
- Autogenerated by Bloom

* Thu Mar 31 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.2-0
- Autogenerated by Bloom

* Wed Mar 23 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.1-0
- Autogenerated by Bloom

* Sat Mar 19 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.0-0
- Autogenerated by Bloom

* Fri Dec 18 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.4-0
- Autogenerated by Bloom

* Tue Dec 01 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.3-0
- Autogenerated by Bloom

* Tue Oct 20 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.2-0
- Autogenerated by Bloom

* Tue Apr 28 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.1-0
- Autogenerated by Bloom

* Wed Feb 25 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.0-0
- Autogenerated by Bloom

* Thu Jan 22 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.3.17-0
- Autogenerated by Bloom

