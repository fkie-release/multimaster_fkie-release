Name:           ros-indigo-node-manager-fkie
Version:        0.5.5
Release:        0%{?dist}
Summary:        ROS node_manager_fkie package

Group:          Development/Libraries
License:        BSD, some icons are licensed under the GNU Lesser General Public License (LGPL) or Creative Commons Attribution-Noncommercial 3.0 License
URL:            http://ros.org/wiki/node_manager_fkie
Source0:        %{name}-%{version}.tar.gz

Requires:       python-docutils
Requires:       python-paramiko
Requires:       ros-indigo-default-cfg-fkie
Requires:       ros-indigo-diagnostic-msgs
Requires:       ros-indigo-dynamic-reconfigure
Requires:       ros-indigo-master-discovery-fkie
Requires:       ros-indigo-master-sync-fkie
Requires:       ros-indigo-multimaster-msgs-fkie
Requires:       ros-indigo-python-qt-binding
Requires:       ros-indigo-rosgraph
Requires:       ros-indigo-roslaunch
Requires:       ros-indigo-roslib
Requires:       ros-indigo-rosmsg
Requires:       ros-indigo-rospy
Requires:       ros-indigo-rosservice
Requires:       ros-indigo-rqt-gui
Requires:       ros-indigo-rqt-reconfigure
Requires:       screen
Requires:       xterm
BuildRequires:  ros-indigo-catkin
BuildRequires:  ros-indigo-diagnostic-msgs
BuildRequires:  ros-indigo-master-discovery-fkie
BuildRequires:  ros-indigo-multimaster-msgs-fkie

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

