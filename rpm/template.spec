Name:           ros-melodic-node-manager-fkie
Version:        0.8.10
Release:        0%{?dist}
Summary:        ROS node_manager_fkie package

Group:          Development/Libraries
License:        BSD, some icons are licensed under the GNU Lesser General Public License (LGPL) or Creative Commons Attribution-Noncommercial 3.0 License
URL:            http://ros.org/wiki/node_manager_fkie
Source0:        %{name}-%{version}.tar.gz

Requires:       python-docutils
Requires:       python-paramiko
Requires:       ros-melodic-default-cfg-fkie
Requires:       ros-melodic-diagnostic-msgs
Requires:       ros-melodic-dynamic-reconfigure
Requires:       ros-melodic-master-discovery-fkie
Requires:       ros-melodic-master-sync-fkie
Requires:       ros-melodic-multimaster-msgs-fkie
Requires:       ros-melodic-python-qt-binding
Requires:       ros-melodic-rosgraph
Requires:       ros-melodic-roslaunch
Requires:       ros-melodic-roslib
Requires:       ros-melodic-rosmsg
Requires:       ros-melodic-rospy
Requires:       ros-melodic-rosservice
Requires:       ros-melodic-rqt-gui
Requires:       ros-melodic-rqt-reconfigure
Requires:       screen
Requires:       xterm
BuildRequires:  ros-melodic-catkin
BuildRequires:  ros-melodic-diagnostic-msgs
BuildRequires:  ros-melodic-master-discovery-fkie
BuildRequires:  ros-melodic-multimaster-msgs-fkie

%description
Graphical interface, written in PySide, to manage the running and configured ROS
nodes on different hosts. For discovering the running ROS master
master_discovery node will be used.

%prep
%setup -q

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/melodic/setup.sh" ]; then . "/opt/ros/melodic/setup.sh"; fi
mkdir -p obj-%{_target_platform} && cd obj-%{_target_platform}
%cmake .. \
        -UINCLUDE_INSTALL_DIR \
        -ULIB_INSTALL_DIR \
        -USYSCONF_INSTALL_DIR \
        -USHARE_INSTALL_PREFIX \
        -ULIB_SUFFIX \
        -DCMAKE_INSTALL_LIBDIR="lib" \
        -DCMAKE_INSTALL_PREFIX="/opt/ros/melodic" \
        -DCMAKE_PREFIX_PATH="/opt/ros/melodic" \
        -DSETUPTOOLS_DEB_LAYOUT=OFF \
        -DCATKIN_BUILD_BINARY_PACKAGE="1" \

make %{?_smp_mflags}

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree that was dropped by catkin, and source it.  It will
# set things like CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/melodic/setup.sh" ]; then . "/opt/ros/melodic/setup.sh"; fi
cd obj-%{_target_platform}
make %{?_smp_mflags} install DESTDIR=%{buildroot}

%files
/opt/ros/melodic

%changelog
* Tue Feb 26 2019 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.10-0
- Autogenerated by Bloom

* Mon Jan 07 2019 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.9-0
- Autogenerated by Bloom

* Tue Dec 11 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.5-0
- Autogenerated by Bloom

* Sat Dec 08 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.4-0
- Autogenerated by Bloom

* Fri Aug 10 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.2-0
- Autogenerated by Bloom

* Fri Aug 03 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.1-0
- Autogenerated by Bloom

* Thu Jul 19 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.0-0
- Autogenerated by Bloom

