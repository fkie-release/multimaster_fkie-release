Name:           ros-kinetic-master-sync-fkie
Version:        0.7.7
Release:        0%{?dist}
Summary:        ROS master_sync_fkie package

Group:          Development/Libraries
License:        BSD
URL:            http://ros.org/wiki/master_sync_fkie
Source0:        %{name}-%{version}.tar.gz

Requires:       ros-kinetic-master-discovery-fkie
Requires:       ros-kinetic-multimaster-msgs-fkie
Requires:       ros-kinetic-rosgraph
Requires:       ros-kinetic-roslib
Requires:       ros-kinetic-rospy
BuildRequires:  ros-kinetic-catkin
BuildRequires:  ros-kinetic-master-discovery-fkie
BuildRequires:  ros-kinetic-multimaster-msgs-fkie

%description
Synchronize the local ROS master to the remote masters discovered by
master_discovery_fkie node. The registration of topics and services is only
perform by local ROS master.

%prep
%setup -q

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/kinetic/setup.sh" ]; then . "/opt/ros/kinetic/setup.sh"; fi
mkdir -p obj-%{_target_platform} && cd obj-%{_target_platform}
%cmake .. \
        -UINCLUDE_INSTALL_DIR \
        -ULIB_INSTALL_DIR \
        -USYSCONF_INSTALL_DIR \
        -USHARE_INSTALL_PREFIX \
        -ULIB_SUFFIX \
        -DCMAKE_INSTALL_LIBDIR="lib" \
        -DCMAKE_INSTALL_PREFIX="/opt/ros/kinetic" \
        -DCMAKE_PREFIX_PATH="/opt/ros/kinetic" \
        -DSETUPTOOLS_DEB_LAYOUT=OFF \
        -DCATKIN_BUILD_BINARY_PACKAGE="1" \

make %{?_smp_mflags}

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/kinetic/setup.sh" ]; then . "/opt/ros/kinetic/setup.sh"; fi
cd obj-%{_target_platform}
make %{?_smp_mflags} install DESTDIR=%{buildroot}

%files
/opt/ros/kinetic

%changelog
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

* Wed Sep 07 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.7-0
- Autogenerated by Bloom

* Thu Sep 01 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.6-0
- Autogenerated by Bloom

* Tue Aug 30 2016 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.5.5-0
- Autogenerated by Bloom

