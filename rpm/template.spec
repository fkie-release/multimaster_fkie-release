Name:           ros-jade-master-discovery-fkie
Version:        0.5.2
Release:        0%{?dist}
Summary:        ROS master_discovery_fkie package

Group:          Development/Libraries
License:        BSD
URL:            http://ros.org/wiki/master_discovery_fkie
Source0:        %{name}-%{version}.tar.gz

Requires:       avahi
Requires:       avahi-ui-tools
Requires:       ros-jade-multimaster-msgs-fkie
Requires:       ros-jade-rosgraph
Requires:       ros-jade-roslib
Requires:       ros-jade-rospy
Requires:       ros-jade-std-srvs
BuildRequires:  ros-jade-catkin
BuildRequires:  ros-jade-multimaster-msgs-fkie
BuildRequires:  ros-jade-std-srvs

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
if [ -f "/opt/ros/jade/setup.sh" ]; then . "/opt/ros/jade/setup.sh"; fi
mkdir -p obj-%{_target_platform} && cd obj-%{_target_platform}
%cmake .. \
        -UINCLUDE_INSTALL_DIR \
        -ULIB_INSTALL_DIR \
        -USYSCONF_INSTALL_DIR \
        -USHARE_INSTALL_PREFIX \
        -ULIB_SUFFIX \
        -DCMAKE_INSTALL_LIBDIR="lib" \
        -DCMAKE_INSTALL_PREFIX="/opt/ros/jade" \
        -DCMAKE_PREFIX_PATH="/opt/ros/jade" \
        -DSETUPTOOLS_DEB_LAYOUT=OFF \
        -DCATKIN_BUILD_BINARY_PACKAGE="1" \

make %{?_smp_mflags}

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/jade/setup.sh" ]; then . "/opt/ros/jade/setup.sh"; fi
cd obj-%{_target_platform}
make %{?_smp_mflags} install DESTDIR=%{buildroot}

%files
/opt/ros/jade

%changelog
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

* Thu May 07 2015 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.4.1-0
- Autogenerated by Bloom

