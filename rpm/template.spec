Name:           ros-hydro-master-discovery-fkie
Version:        0.4.1
Release:        0%{?dist}
Summary:        ROS master_discovery_fkie package

Group:          Development/Libraries
License:        BSD
URL:            http://ros.org/wiki/master_discovery_fkie
Source0:        %{name}-%{version}.tar.gz

Requires:       avahi
Requires:       avahi-ui-tools
Requires:       ros-hydro-multimaster-msgs-fkie
Requires:       ros-hydro-rosgraph
Requires:       ros-hydro-roslib
Requires:       ros-hydro-rospy
Requires:       ros-hydro-std-srvs
BuildRequires:  ros-hydro-catkin
BuildRequires:  ros-hydro-multimaster-msgs-fkie
BuildRequires:  ros-hydro-std-srvs

%description
Discover the running ROS Masters in local network. The discovering is done by
sending an echo heartbeat messages to a defined multicast group. The alternative
is to use a zeroconf/avahi daemon to register the ROS master as service and
discover other ROS masters.

%prep
%setup -q

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/hydro/setup.sh" ]; then . "/opt/ros/hydro/setup.sh"; fi
mkdir -p obj-%{_target_platform} && cd obj-%{_target_platform}
%cmake .. \
        -UINCLUDE_INSTALL_DIR \
        -ULIB_INSTALL_DIR \
        -USYSCONF_INSTALL_DIR \
        -USHARE_INSTALL_PREFIX \
        -ULIB_SUFFIX \
        -DCMAKE_INSTALL_PREFIX="/opt/ros/hydro" \
        -DCMAKE_PREFIX_PATH="/opt/ros/hydro" \
        -DSETUPTOOLS_DEB_LAYOUT=OFF \
        -DCATKIN_BUILD_BINARY_PACKAGE="1" \

make %{?_smp_mflags}

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/hydro/setup.sh" ]; then . "/opt/ros/hydro/setup.sh"; fi
cd obj-%{_target_platform}
make %{?_smp_mflags} install DESTDIR=%{buildroot}

%files
/opt/ros/hydro

%changelog
* Tue Apr 28 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.1-0
- Autogenerated by Bloom

* Wed Feb 25 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.0-0
- Autogenerated by Bloom

* Thu Jan 22 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.3.17-0
- Autogenerated by Bloom

* Fri Dec 12 2014 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.3.16-0
- Autogenerated by Bloom

* Wed Dec 03 2014 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.3.15-0
- Autogenerated by Bloom

* Fri Oct 24 2014 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.3.14-0
- Autogenerated by Bloom

* Tue Jul 29 2014 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.3.13-0
- Autogenerated by Bloom

