import platform
import subprocess
import re
import socket
import psutil
from requests import get


class Connectivity:
        @staticmethod
        def get_rssi():
                if platform.system() == 'Linux':
                        p = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                elif platform.system() == 'Windows':
                        p = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                        raise Exception('reached else of if statement')
                out = p.stdout.read().decode()
        
                if platform.system() == 'Linux':
                        m = re.findall('(wl.*?[0-9]+).*?Signal level=(-[0-9]+) dBm', out, re.DOTALL)
                elif platform.system() == 'Windows':
                        m = re.findall('Name.*?:.*?([A-z0-9 ]*).*?Signal.*?:.*?([0-9]*)%', out, re.DOTALL)
                else:
                        raise Exception('reached else of if statement')
        
                p.communicate()
        
                return m

        @staticmethod
        def get_public_ip():
                ip = get('https://api.ipify.org').text
                return ip

        @staticmethod
        def get_local_ip():
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(0)
                try:
                        # doesn't even have to be reachable
                        s.connect(('10.254.254.254', 1))
                        IP = s.getsockname()[0]
                except Exception:
                        IP = '127.0.0.1'
                finally:
                        s.close()
                return IP

        @staticmethod
        def get_info():
                return {
                        "rssi": Connectivity.get_rssi(),
                        "local_ip": Connectivity.get_local_ip(),
                        "public_ip": Connectivity.get_public_ip(),
                }

class System:
        @staticmethod
        def get_config():
                my_system = platform.uname()
                return {
                        "system"   : my_system.system,
                        "node_name": my_system.node,
                        "release"  : my_system.release,
                        "version"  : my_system.version,
                        "machine"  : my_system.machine,
                        "processor": my_system.processor
                }
        @staticmethod
        def get_resources():
                return {
                        "cpu_percent"   : psutil.cpu_percent(),
                        "virtual_memory": dict(psutil.virtual_memory()._asdict()),
                        "virtual_memory_available"  : psutil.virtual_memory().available * 100 / psutil.virtual_memory().total,
                        "virtual_memory_used"  : psutil.virtual_memory().percent
                }

        @staticmethod
        def get_processes():
                '''
                Get list of running process sorted by Memory Usage
                '''
                listOfProcObjects = []
                # Iterate over the list
                for proc in psutil.process_iter():
                        try:
                                # Fetch process details as dict
                                pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
                                pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
                                # Append dict to list
                                listOfProcObjects.append(pinfo);
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass

                # Sort list of dict by key vms i.e. memory usage
                listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)

                return listOfProcObjects

        @staticmethod
        def get_info():
                return {
                        "config": System.get_config(),
                        "platform": System.get_resources(),
                        "processes": System.get_processes(),
                }

if __name__ == '__main__':
        print(Connectivity.get_info(), '\n',System.get_info())
