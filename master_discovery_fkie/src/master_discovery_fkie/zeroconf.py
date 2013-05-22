#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2010, I Heart Engineering
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Fraunhofer nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Roughly based on the code here; http://avahi.org/wiki/PythonPublishExample

import os
import sys
import time
import socket
import dbus
import gobject
import avahi
import threading
from datetime import datetime
from dbus.mainloop.glib import DBusGMainLoop

import roslib; roslib.load_manifest('master_discovery_fkie')
import rospy
from std_msgs.msg import String

from master_discovery_fkie.msg import LinkState, LinkStatesStamped, MasterState, ROSMaster#, SyncMasterInfo, SyncTopicInfo
from master_discovery_fkie.srv import DiscoverMasters, DiscoverMastersResponse#, GetSyncInfo
from master_monitor import MasterMonitor


ZEROCONF_NAME = "zeroconf"


class MasterInfo(object):
  '''
  The Master representation with variables available from zeroconf daemon. 
  '''
  def __init__(self, name, stype, domain, host, port, txt, interface=avahi.IF_UNSPEC, protocol=avahi.PROTO_UNSPEC, online=False):
    # flags of the avahi service
    self.interface = interface
    self.protocol = protocol
    self.name = str(name)
    self.stype = stype
    self.domain = domain
    self.host = host
    self.port = port
    self.txt = txt[:]
    # additional information
    self.online = online
    self.lastUpdate = 0

  def getMasterUri(self):
    return self.getTXTValue('master_uri')

  def getRosTimestamp(self):
    return MasterInfo.timestampToRosTime(self.getTXTValue('timestamp'))
  
  @staticmethod
  def timestampToRosTime(timestamp):
    '''..........................................................................
    Converts the string representation of the current timestamp to ROS time and
    returns it.
    ..........................................................................'''
    try:
      if not (timestamp is None):
        return float(timestamp)
    except:
      #depricated
#      import traceback
#      rospy.logwarn("%s", traceback.format_exc())
      if not (timestamp is None):
        t = datetime.strptime(timestamp, '%Y%m%d%H%M%S.%f')
      else:
        t = datetime.now()
      return time.mktime(t.timetuple()) + t.microsecond / 1e6


  @staticmethod
  def MasteruriToAddr(masteruri):
    '''..........................................................................
    Returns the host name and port of the masteruri. C{urlparse} is used. 
    @param masteruri: the URL of the master
    @type masteruri:  C{str}
    @return: a tupel of host and port
    @rtype:  C{(str, str)}
    ..........................................................................'''
    from urlparse import urlparse
    o = urlparse(masteruri)
    return (o.hostname, o.port)

  def getAddrFromMasterUri(self):
    return MasterInfo.MasteruriToAddr(self.getTXTValue('master_uri', ''))

  def getTXTValue(self, key, default=None):
    result = MasterInfo.txtValue(key, self.txt)
    if result is None:
      return default
    else:
      return result

  @staticmethod
  def txtValue(key, txt):
    '''..........................................................................
    Returns the host name and port by removing 'http:// at the front of the 
    masteruri
    
    @param key: the parameter name stored in the txt value of the avahi info
    @type key:  C{str}
    @param txt: avahi txt array
    @type txt:  C{avahi txt array}
    @return: the value stored in the txt array for given name
    @rtype:  C{str} or C{None}
    ..........................................................................'''
    for item in txt:
      valKey = item.split('=')
      if (len(valKey) == 2 and valKey[0].strip() == key.strip()):
        return valKey[1]
    return None
    
  def __repr__(self):
    """
      Produce a string representation of the master item.
    """
    return ''.join(["MasterInfo\n  Interface: ", str(self.interface),
                    "\n  protocol: ", str(self.protocol),
                    "\n  name: ", self.name,
                    "\n  service type: ", str(self.stype),
                    "\n  Domain: ", self.domain,
                    "\n  Url: http://", self.host, ":", str(self.port),
                    "\n  TXT: ", str(self.txt)])



class Zeroconf(threading.Thread):
  '''
  This class creates the DBus interface to avahi and runs the gMainLoop to handle
  the gSignals.
  '''
  def __init__(self, name, service_type = '_ros-master._tcp', host=socket.gethostname(), port=11311, domain='local', txt_array=[]):
    '''..........................................................................
    Initialization method of the Zeroconf class.
    @param name: the name of the local ROS master
    @type name:  C{str}
    @param service_type: the avahi service type
    @type service_type:  C{str}
    @param host: the host of the local ROS master
    @type host: C{str}
    @param port: the port of the local ROS master
    @type port: C{int}
    @param domain: the domain name
    @type domain: C{str}
    @param txt_array: (optional) additional information
    @type txt_array: C{[str]}
    ..........................................................................'''
    self.masterInfo = MasterInfo(name, service_type, domain, host, port, txt_array)
    
    # FIXME Review thread locking as needed.
    # init thread
    threading.Thread.__init__(self)
    self._lock = threading.RLock()
    # Gobjects are an event based model of evil, do not trust them,
    DBusGMainLoop(set_as_default=True)
    # Magic? Yes, don't start threads without it.
    # Why? I'm sure thats documented somewhere.
    gobject.threads_init()
    dbus.mainloop.glib.threads_init()
    self.__main_loop = gobject.MainLoop()
    self.__bus = dbus.SystemBus()
    # Initialize iterface to DBUS Server
    self.__server = dbus.Interface(self.__bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
                                   avahi.DBUS_INTERFACE_SERVER)

    # The DBUS entry group
    self.__group = None
    # Monitor server state changes
    self.__server.connect_to_signal("StateChanged", self.__avahi_callback_state_changed)
    
    # the browser to register the updates and new services
    self.__browser = dbus.Interface(self.__bus.get_object(avahi.DBUS_NAME,
                                                          self.__server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                                                                          avahi.PROTO_UNSPEC,
                                                                                          self.masterInfo.stype,
                                                                                          self.masterInfo.domain,
                                                                                          dbus.UInt32(0))),
                                   avahi.DBUS_INTERFACE_SERVICE_BROWSER)
    self.__browser.connect_to_signal("ItemNew", self.__avahi_callback_service_browser_new)
    self.__browser.connect_to_signal("ItemRemove", self.__avahi_callback_service_browser_remove)

#  def __del__(self):
#    if not (self.__group is None):
#      self.__group.Free()
#      self.__group = None


  def __avahi_callback_zeroconf_service_updated(self):
    self.on_service_updated()

  def __avahi_callback_error(self, err):
    rospy.logwarn(str(err))
    print '__avahi_callback_error:', err

  def __avahi_callback_print_error(self, *args):
    '''..........................................................................
    This method will be called, if an error occurs while service resolving.
    ..........................................................................'''
    for arg in args:
      print '__avahi_callback_print_error:', arg
      rospy.logdebug('Error while resolving: %s', arg)
    self.on_resolve_error()

  def __avahi_callback_state_changed(self, state):
    if state == avahi.SERVER_COLLISION:
      self.on_server_collision()
    elif state == avahi.SERVER_RUNNING:
      self._registerService()
      self.on_server_running()
    elif state == avahi.SERVER_FAILURE:
      self.on_server_failure()

  def __avahi_callback_group_state_changed(self, state, error):
    if state == avahi.ENTRY_GROUP_ESTABLISHED:
      self.on_group_established()
    elif state == avahi.ENTRY_GROUP_COLLISION:
      self.on_group_collision()
    elif state == avahi.ENTRY_GROUP_FAILURE:
      self.on_group_failure(error)

  def __avahi_callback_service_browser_new(self,interface, protocol, name, stype, domain, flags):
    '''..........................................................................
    This callback will be called, if a new service was registered. The service 
    will the resolved to get more information about the service.
    ..........................................................................'''
    rospy.logdebug("Service Browser - itemNew: %s", name) 
    self.__server.ResolveService(interface, 
                                 protocol, 
                                 name, 
                                 stype,
                                 domain, 
                                 avahi.PROTO_UNSPEC,
                                 dbus.UInt32(0),
                                 reply_handler=self.__avahi_callback_service_resolved,
                                 error_handler=self.__avahi_callback_print_error)
    # dbus.UInt32(0) & avahi.LOOKUP_RESULT_CACHED,

  def __avahi_callback_service_browser_remove(self,interface, protocol, name, stype, domain, flags,*args):
    '''..........................................................................
    This callback will be called, if a service was removed from zeroconf.
    ..........................................................................'''
    self.on_group_removed(name)

  def __avahi_callback_service_resolved(self, *args):
    '''..........................................................................
    This callback will be called, if a new service was registered or a resolve 
    request was called. The _master list will be updated.
    ..........................................................................'''
    self.on_resolve_reply(MasterInfo(args[2], args[3], args[4], args[7], args[8], avahi.txt_array_to_string_array(args[9]), args[0], args[1], online=False))

  def _removeService(self):
    if not self.__group is None:
      self.__group.Reset()

  def _registerService(self):
      try:
        if self.__group is None:
          if (self.masterInfo.domain is None) or len(self.masterInfo.domain) == 0:
            self.masterInfo.domain = 'local'
          self.masterInfo.host = self.masterInfo.host + '.' + self.masterInfo.domain
          self.__group = dbus.Interface(self.__bus.get_object(avahi.DBUS_NAME,
                                                              self.__server.EntryGroupNew()),
                                       avahi.DBUS_INTERFACE_ENTRY_GROUP)
          self.__group.connect_to_signal('StateChanged', self.__avahi_callback_group_state_changed)
        self.__group.AddService(avahi.IF_UNSPEC,
                                avahi.PROTO_UNSPEC,
                                dbus.UInt32(0),
                                self.masterInfo.name, 
                                self.masterInfo.stype,
                                self.masterInfo.domain,
                                self.masterInfo.host,
                                dbus.UInt16(str(self.masterInfo.port)),
                                avahi.string_array_to_txt_array(self.masterInfo.txt))
        self.__group.Commit()
      except dbus.DBusException, e:
        rospy.logfatal(''.join(['registerService: ', str(e)]))
        self.on_group_collision()

#        rospy.signal_shutdown(-1)

  def requestResolve(self, master_info):
    result = None
    try:
      self._lock.acquire(True)
      if not (master_info is None):
        interface, protocol, name, stype, domain, five, six, host, port, txt, flags = self.__server.ResolveService(master_info.interface, 
                                     master_info.protocol, 
                                     master_info.name, 
                                     master_info.stype,
                                     master_info.domain, 
                                     avahi.PROTO_UNSPEC,
                                     dbus.UInt32(0))
        result = MasterInfo(name, stype, domain, host, port, avahi.txt_array_to_string_array(txt), interface, protocol, online=True)
    except dbus.DBusException:
      result = None
    except:
      import traceback
      print traceback.format_exc()
    finally:
      self._lock.release()
      return result
      

  def updateService(self, txt_array = []):
    try:
      self._lock.acquire(True)
      if not (self.__group is None):
        self.__group.UpdateServiceTxt(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, dbus.UInt32(0), 
                                 self.masterInfo.name, 
                                 self.masterInfo.stype, 
                                 self.masterInfo.domain, 
                                 avahi.string_array_to_txt_array(txt_array),
                                 reply_handler=self.__avahi_callback_zeroconf_service_updated,
                                 error_handler=self.__avahi_callback_error)
      else:
        raise Exception("ServiceGroup %s not registered in avahi", self.masterInfo.name)
    finally:
      self._lock.release()

  def resetService(self):
    self.__group.Commit()
#    del self.__group
#    self.__group = None

  def run(self):
    try:
      # Build initial state information
      self.__avahi_callback_state_changed(self.__server.GetState())
      if not self.isStopped():
        self.__main_loop.run()
    except KeyboardInterrupt or ROSInterruptException:
      print "Ctrl + C"

  def stop(self):
    self.stopped = True
    rospy.logdebug("Zeroconf stop")
    print "Zeroconf stop"
    self.__main_loop.quit()
    print "MainLoop exited"
#    if not (self.__group is None):
#      self.__group.Free()
#      self.__group = None

  def isStopped(self):
    return hasattr(self, 'stopped')

  def on_server_running(self):
    rospy.loginfo("Template: on_server_running")
    if hasattr(self, 'collision'):
      self.stop()
      sys.exit("ERROR: Template: on_group_collision - EXIT!")
    pass
  
  def on_server_collision(self):
    rospy.logfatal("Template: on_server_collision")
    self.collision = True
    pass
  
  def on_server_failure(self):
    rospy.logfatal("Template: on_server_failure")
    pass

  def on_group_established(self):
    rospy.logdebug("Template: on_group_established")
    pass
  
  def on_group_collision(self):
    rospy.logfatal("Template: on_group_collision")
    self.collision = True
    self.stop()
    sys.exit("ERROR: Template: on_group_collision - EXIT!")
    pass
  
  def on_group_failure(self, error):
    rospy.logfatal("Template: on_group_failure - %s", error)
    self.stop()
    sys.exit("ERROR: Template: on_group_failure - EXIT! [%s]", error)

  def on_group_removed(self, name):
    rospy.loginfo("Template: on_group_removed - %s", name)
    pass

  def on_resolve_reply(self, master_info):
    rospy.logdebug("Template: on_resolve_reply - %s", master_info.name)
    pass

  def on_service_updated(self):
    rospy.logdebug('Template: on_service_updated')

  def on_resolve_error(self):
    rospy.logdebug("Template: on_resolve_error")
    pass



class Polling(threading.Thread):
  '''
  The class to poll the updates of the ROS masters from the avahi daemon.
  '''
  def __init__(self, master_list, master_info, callback, update_hz):
    '''..........................................................................
    Initialize method for the Polling class
    @param master_info: the information of the master to polling
    @type master_info:  MasterInfo
    @param callback: the function to call fn(MasterInfo) periodically. 
    @type callback:  str
    ..........................................................................'''
    threading.Thread.__init__(self)
    self.masterList = master_list
    self.masterInfo = master_info
    self.__callback = callback
    self.__update_hz = update_hz
#    print "CREATE POLLING for", master_info.name, ", count of active threads:", threading.activeCount()
    self.start()
  
  def stop(self):
    self.__callback = None
  
  def run(self):
    '''..........................................................................
    Callback method of the ROS timer for periodically polling.
    ..........................................................................'''
    self.current_check_hz = self.__update_hz
    while (not (self.__callback is None)) and (not rospy.is_shutdown()):
      cputimes = os.times()
      cputime_init = cputimes[0] + cputimes[1]
      master = self.__callback(self.masterInfo)
      if not master is None:
        self.masterList.updateMaster(master)
      else:
        self.masterList.setMasterOnline(self.masterInfo.name, False)
      # adapt the check rate to the CPU usage time
      cputimes = os.times()
      cputime = cputimes[0] + cputimes[1] - cputime_init
      if self.current_check_hz*cputime > 0.20:
        self.current_check_hz = float(self.current_check_hz)/2.0
      elif self.current_check_hz*cputime < 0.10 and self.current_check_hz < self.__update_hz:
        self.current_check_hz = float(self.current_check_hz)*2.0
#      print "update rate", self.current_check_hz
      time.sleep(1.0/self.current_check_hz)
#    print "stop polling", self.masterInfo.name
#    else:
#      raise Exception("no callback defined for %s", self.masterInfo.name)



class MasterList(object):
  '''
  The MasterList manages the synchronization and polling thread for local and 
  each remote ROS master. The changes will be published as a complete list of 
  known ROS masters as ROSMasters message under the topic '~masters'. To detect
  the changes the setMasterOnline() and checkMastersState() should be used to 
  change the state of the ROS masters.
  '''
  def __init__(self, local_master_info, callback_update_remote, callback_update_local):
    '''..........................................................................
    Initialization method of the MasterList. 
    @param local_master_info: the information of the local ROS master
    @type local_master_info:  MasterInfo
    @param callback_update_remote: the function fn(MasterInof) for polling the 
                                   state of remote ROS masters
    @type callback_update_remote:  str
    @param callback_update_local: the function fn(MasterInfo) to test the state 
                                  of the local ROS master
    @type callback_update_local:  str
    ..........................................................................'''
    # initialize the ROS publishers
    self.pubchanges = rospy.Publisher("~changes", MasterState)
    self.pubstats = rospy.Publisher("~linkstats", LinkStatesStamped)
    # initialize the ROS services
    rospy.Service('~list_masters', DiscoverMasters, self.rosservice_list_masters)
    # the list with all ROS master neighbors
    self.__lock = threading.RLock()
    # the info of local master, this master is always online
    self.localMasterName = local_master_info.name
    self.__masters = {}
    self.__pollings = {}
    self.__callback_update_remote = callback_update_remote
    self.__callback_update_local = callback_update_local


  def setMasterOnline(self, name, state):
    '''..........................................................................
    Sets the online state of the ROS master with given name. This method should 
    be used to detect changes of the ROS master states and publish it to the 
    '~masters' topic. 
    @param name: the name of the ROS master.
    @type name:  str
    @param state: the new state of the ROS master (True is online).
    @type state:  bool
    ..........................................................................'''
    try:
      self.__lock.acquire()
      m = self.__masters[name]
      # publish the master list, only on new state 
      if (state != m.online):
        rospy.loginfo("%s is now %s", m.name, "online" if state else "offline")
        m.online = state
        self.pubchanges.publish(MasterState(MasterState.STATE_CHANGED, 
                                            ROSMaster(str(m.name), 
                                                      m.getMasterUri(), 
                                                      m.getRosTimestamp(), 
                                                      state, 
                                                      m.getTXTValue('zname', ''), 
                                                      m.getTXTValue('rpcuri', ''))))
    except:
#      import traceback
#      rospy.logwarn("%s", traceback.format_exc())
      pass
    finally:
      self.__lock.release()

  def checkMastersState(self):
    '''..........................................................................
    Checks the last update time and mark the ROS master offline, if necessary.
    This method will be called on timeout error while resolving service.
    ..........................................................................'''
    try:
      self.__lock.acquire()
      for key in self.__masters.keys():
        master = self.__masters[key]
        if time.time() - master.lastUpdate > 1.0/Discoverer.ROSMASTER_HZ+2:
          self.setMasterOnline(key, False)
    except:
      import traceback
      rospy.logwarn("Error while check master state: %s", traceback.format_exc())
    finally:
      self.__lock.release()

  def updateMaster(self, master_info):
    '''..........................................................................
    Sets the new information of the master and synchronize the ROS master if 
    needed.
    @param master_info: new update information for the master
    @type master_info: MasterInfo
    ..........................................................................'''
    try:
      self.__lock.acquire()
      if (master_info.name in self.__masters):
        if (self.__masters[master_info.name].getRosTimestamp() != master_info.getRosTimestamp()):
#          print 'PUBLISH NEW STATE for', master_info.name
          self.__masters[master_info.name].txt = master_info.txt[:]
          self.pubchanges.publish(MasterState(MasterState.STATE_CHANGED, 
                                              ROSMaster(str(master_info.name), 
                                                        master_info.getMasterUri(), 
                                                        master_info.getRosTimestamp(), 
                                                        True, 
                                                        master_info.getTXTValue('zname', ''), 
                                                        master_info.getTXTValue('rpcuri', ''))))
        self.__masters[master_info.name].lastUpdate = time.time()
        self.setMasterOnline(master_info.name, True)
      else:
#        print "new master:", master_info.name
        self.__masters[master_info.name] = master_info
        # create a new polling thread to detect changes
        self.__pollings[master_info.name] = Polling(self, master_info, self.__callback_update_local if (self.localMasterName == master_info.name) else self.__callback_update_remote, Discoverer.ROSMASTER_HZ)
        self.pubchanges.publish(MasterState(MasterState.STATE_NEW, 
                                            ROSMaster(str(master_info.name), 
                                                      master_info.getMasterUri(), 
                                                      master_info.getRosTimestamp(), 
                                                      True, 
                                                      master_info.getTXTValue('zname', ''), 
                                                      master_info.getTXTValue('rpcuri', ''))))
    except:
      import traceback
      rospy.logwarn("Error while update master: %s", traceback.format_exc())
    finally:
      self.__lock.release()

  def removeMaster(self, name):
    '''..........................................................................
    Removes the master from the list and ends the synchronization to the given
    remote master.
    @param name: the name of the ROS master to remove
    @type name:  str
    ..........................................................................'''
    try:
      self.__lock.acquire()
      rospy.logdebug("remove master: %s", name)
      if (name in self.__pollings):
        r = self.__pollings.pop(name)
        r.stop()
        del r
      if (name in self.__masters):
        r = self.__masters.pop(name)
        self.pubchanges.publish(MasterState(MasterState.STATE_REMOVED, 
                                            ROSMaster(str(r.name), 
                                                      r.getMasterUri(), 
                                                      r.getRosTimestamp(), 
                                                      False, 
                                                      r.getTXTValue('zname', ''), 
                                                      r.getTXTValue('rpcuri', ''))))
#        r.stop()
        del r
    except:
      import traceback
      rospy.logwarn("Error while remove master: %s", traceback.format_exc())
    finally:
      self.__lock.release()

  def getMasterInfo(self, name):
    '''..........................................................................
    Returns MasterInfo object for given name or None.
    @param name:  the name of the ROS master
    @type name: str
    @return: the information about the master with given name 
    @rtype: MasterInfo or None, if master not found
    ..........................................................................'''
    result = None
    try:
      self.__lock.acquire()
      result = self.__masters[name]
    except:
      import traceback
      rospy.logwarn("Error while getMasterInfo: %s", traceback.format_exc())
    finally:
      self.__lock.release()
      return result

  def removeAll(self):
    '''..........................................................................
    Removes all masters and ends the synchronization to these.
    ..........................................................................'''
    try:
      self.__lock.acquire()
      while self.__pollings:
        name, p = self.__pollings.popitem()
        p.stop()
      while self.__masters:
        name, master = self.__masters.popitem()
        self.pubchanges.publish(MasterState(MasterState.STATE_REMOVED, 
                                            ROSMaster(str(master.name), 
                                                      master.getMasterUri(), 
                                                      master.getRosTimestamp(), 
                                                      False, 
                                                      master.getTXTValue('zname', ''), 
                                                      master.getTXTValue('rpcuri', ''))))
    except Exception:
      import traceback
      rospy.logwarn("Error while removeAll: %s", traceback.format_exc())
    finally:
      self.__lock.release()

  def rosservice_list_masters(self, req):
    '''
    Callback for the ROS service to get the current list of the known ROS masters.
    '''
    masters = list()
    self.__lock.acquire(True)
    try:
      for key, master in self.__masters.iteritems():
        masters.append(ROSMaster(str(master.name), 
                                 master.getMasterUri(), 
                                 master.getRosTimestamp(), 
                                 master.online, 
                                 master.getTXTValue('zname', ''), 
                                 master.getTXTValue('rpcuri', '')))
    except:
      pass
    finally:
      self.__lock.release()
      return DiscoverMastersResponse(masters)



class Discoverer(Zeroconf):
  '''
  This class is a subclass of Zeroconf to handle the callback of the avahi daemon.
  Furthermore the informations of the local ROS master will be stored and a 
  method to check the state of the local ROS master and update it in avahi if 
  needed. A list with all remote ROS masters is managed by MasterList.
  '''
  ROSMASTER_HZ = 2 # the test rate of ROS master state in hz

  def __init__(self, monitor_port=11611, domain=''):
    '''..........................................................................
    Initialize method of the local master.
    @param monitor_port: The port of the RPC Server, used to get more information about the ROS master.
    @type monitor_port:  int
    ..........................................................................'''
    if rospy.has_param('~rosmaster_hz'):
      Discoverer.ROSMASTER_HZ = rospy.get_param('~rosmaster_hz')

    self.master_monitor = MasterMonitor(monitor_port)
    name = self.master_monitor.getMastername()
    # create the txtArray for the zeroconf service of the ROS master
    materuri = self.master_monitor.getMasteruri()
    # test the host for local entry
    masterhost, masterport = MasterInfo.MasteruriToAddr(materuri)
    if (masterhost in ['localhost', '127.0.0.1']):
      sys.exit("'%s' is not reachable for other systems. Change the ROS_MASTER_URI!", masterhost)
    rpcuri = ''.join(['http://', socket.gethostname(), ':', str(monitor_port), '/'])
    txtArray = ["timestamp=%s"%str(0), "master_uri=%s"%materuri, "zname=%s"%rospy.get_name(), "rpcuri=%s"%rpcuri]
    # the Zeroconf class, which contains the QMainLoop to receive the signals from avahi
    Zeroconf.__init__(self, name, '_ros-master._tcp', masterhost, masterport, domain, txtArray)
    # the list with all ROS master neighbors with theirs SyncThread's and all Polling threads
    self.masters = MasterList(self.masterInfo, self.requestResolve, self.checkLocalMaster)
    # set the callback to finish all running threads
    rospy.on_shutdown(self.finish)
#    #start the signal main loop
#    if (not rospy.is_shutdown()):
#      self.start()


  @property
  def getName(self):
    return self.masterInfo.name

  def finish(self, *args):
    '''..........................................................................
    Removes all remote masters and unregister their topics and services. Stops 
    the QMainLoop of avahi.
    ..........................................................................'''
    rospy.logdebug("Stop zeroconf DBusGMainLoop")
    if hasattr(self.master_monitor, 'rpcServer'):
      self.master_monitor.rpcServer.shutdown()
    self.stop()
    self.masters.removeAll()

  def __repr__(self):
    '''..........................................................................
    String representation of local ros manager
    ..........................................................................'''
    return ''.join(['Discoverer: ', repr(self.masterInfo)])

  def on_server_running(self):
    rospy.loginfo("Zeroconf server now running.")

  def on_server_collision(self):
    rospy.logfatal("Zeroconf server collision.")
    self.collision = True
    self.finish()
    rospy.signal_shutdown("Zeroconf server collision.")

  def on_server_failure(self):
    rospy.logfatal("Zeroconf server error.")
    self.finish()
    rospy.signal_shutdown("on_server_failure")

  def on_group_established(self):
    rospy.logdebug("Service %s established.", self.masterInfo.name)

  def on_group_collision(self):
    if not self.isStopped():
      rospy.logwarn("ERROR: Service name collision. %s already exists. Retry in 3 sec...", self.masterInfo.name)
      self._removeService()
      time.sleep(3)
      self._registerService()

  def on_group_failure(self, error):
    rospy.logfatal("Error in group %s: %s", self.masterInfo.name, error)
    self.finish()
    rospy.signal_shutdown("Error in group")

  def on_group_removed(self, name):
    if (name != self.masterInfo.name):
      rospy.loginfo("%s group removed from zeroconf.", name)
      self.masters.removeMaster(name)

  def on_resolve_reply(self, master_info):
    rospy.logdebug("on_resolve_reply: %s", master_info.name)
    self.masters.updateMaster(master_info)

  def on_service_updated(self):
    self.masters.updateMaster(self.masterInfo)
     
  def on_resolve_error(self):
    self.masters.checkMastersState()

  def checkLocalMaster(self, master_info):
    '''..........................................................................
    Compares the current state of the local ROS master. If the state was changed
    the avahi sevice will be updated
    @param master_info: will not be used, is only for compatibility to the Polling class.
    ..........................................................................'''
    # get the state of the local ROS master
    try:
      # compare the current system state of ROS master with stored one and update the timestamp if needed
      if self.master_monitor.checkState():
        # sets a new timestamp in zeroconf
#        rospy.logdebug("state of local master changed")
        rpcuri = self.masterInfo.getTXTValue('rpcuri', '')
        masteruri = self.masterInfo.getTXTValue('master_uri', '')
        self.masterInfo.txt = ["timestamp=%s"%str(self.master_monitor.getCurrentState().timestamp), "master_uri=%s"%masteruri, "zname=%s"%rospy.get_name(), "rpcuri=%s"%rpcuri]
        self.updateService(self.masterInfo.txt)
      return self.masterInfo
    except:
      import traceback
      rospy.logerr("Error while check local master: %s", traceback.format_exc())
    return None