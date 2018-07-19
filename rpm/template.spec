Name:           ros-melodic-multimaster-fkie
Version:        0.8.0
Release:        0%{?dist}
Summary:        ROS multimaster_fkie package

Group:          Development/Libraries
License:        BSD
URL:            http://ros.org/wiki/multimaster_fkie
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       ros-melodic-default-cfg-fkie
Requires:       ros-melodic-master-discovery-fkie
Requires:       ros-melodic-master-sync-fkie
Requires:       ros-melodic-multimaster-msgs-fkie
Requires:       ros-melodic-node-manager-fkie
BuildRequires:  ros-melodic-catkin

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
* Thu Jul 19 2018 Alexander Tiderko <alexander.tiderko@gmail.com> - 0.8.0-0
- Autogenerated by Bloom

