import json
import subprocess

def check_cinder():
	cinder = "openstack volume service list -c 'Binary' -c 'Host' -c 'State' -f json"
	data = subprocess.check_output(cinder, shell=True)
	data_json = json.loads(data)
	service_status("CINDER", data_json)
	print("\n")


def check_compute():
	compute = "openstack compute service list -c 'Binary' -c 'Host' -c 'State' -f json"
	data = subprocess.check_output(compute, shell=True)
	data_json = json.loads(data)
	service_status("NOVA", data_json)
	print("\n")


def check_neutron():
	print("CHECKING FOR NEUTRON SERVICES")
	neutron = "openstack network agent list -c 'Binary' -c 'Host' -c 'Alive' -f json"
	data = subprocess.check_output(neutron, shell=True)
	data_json = json.loads(data)
	status = True
        for service in data_json:
                if service['Alive'] != ':-)':
                        print('\033[1;91mNEUTRON SERVICES.....FAILED\033[1;m')
                        for service in data_json:
		                if service['Alive'] != ':-)':
                		        print('\033[1;91m%s on %s .....DOWN\033[1;m' % (service['Binary'], service['Host']))
                		else:
                        		print('\033[1;32m%s on %s .....UP\033[1;m' % (service['Binary'], service['Host']))
			status = False
                        break
        if status:
                print('\033[1;32mNEUTRON SERVICES.....UP\033[1;m')
	print("\n")


def service_status(service_name, data_json):
        print("CHECKING FOR %s SERVICES" % (service_name))
        status = True
        for service in data_json:
                if service['State'].lower() != 'up':
                        print('\033[1;91m%s SERVICES.....FAILED\033[1;m' % (service_name))
                        print_services(data_json)
                        status = False
                        break
        if status:
                print('\033[1;32m%s SERVICES.....UP\033[1;m' % (service_name))


def print_services(data_json):
	for service in data_json:
                if service['State'].lower() != 'up':
                        print('\033[1;91m%s on %s .....DOWN\033[1;m' % (service['Binary'], service['Host']))
                else:
                        print('\033[1;32m%s on %s .....UP\033[1;m' % (service['Binary'], service['Host']))



check_cinder()
check_compute()
check_neutron()
