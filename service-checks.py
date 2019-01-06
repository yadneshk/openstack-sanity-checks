import json
import subprocess
import os

controllers_list = []

def check_baremetal_nodes():
	print("CHECKING BAREMETAL NODE STATUS")
	baremetal_nodes = "source ~/stackrc; openstack baremetal node list -c 'Name' -c 'Power State' -c 'Provisioning State' -c 'Maintenance' -f json"
	data = subprocess.check_output(baremetal_nodes, shell=True)
	nodes_data_json = json.loads(data)
	all_nodes_clean = True
	for node in nodes_data_json:
		if node['Maintenance'] or node['Provisioning State'] != 'active' or node['Power State'] != 'power on':
			print('\033[1;91mBAREMETAL NODE STATUS.....FAILED\033[1;m')
			all_nodes_clean = False
			break
	if not all_nodes_clean:
		for node in nodes_data_json:
			if node['Maintenance'] or node['Provisioning State'] != 'active' or node['Power State'] != 'power on':
				print('\033[1;91mNode %s Status Maintenance=%s, Provisioning State=%s, Power State=%s.....FAILED\033[1;m' % (node['Name'], node['Maintenance'], node['Provisioning State'], node['Power State']))
			else:
				print('\033[1;32mNODE %s STATUS.....OK\033[1;m' % (node['Name']))

	else:
		print('\033[1;32mBAREMETAL NODE STATUS.....OK\033[1;m')
	print("\n")


def check_cinder():
	cinder = "source ~/overcloudrc; openstack volume service list -c 'Binary' -c 'Host' -c 'State' -f json"
	data = subprocess.check_output(cinder, shell=True)
	data_json = json.loads(data)
	service_status("CINDER", data_json)
	print("\n")


def check_compute():
	compute = "source ~/overcloudrc; openstack compute service list -c 'Binary' -c 'Host' -c 'State' -f json"
	data = subprocess.check_output(compute, shell=True)
	data_json = json.loads(data)
	service_status("NOVA", data_json)
	print("\n")


def check_neutron(expected_status):
	print("CHECKING FOR NEUTRON SERVICES")
	neutron = "source ~/overcloudrc; openstack network agent list -c 'Binary' -c 'Host' -c 'Alive' -f json"
	data = subprocess.check_output(neutron, shell=True)
	data_json = json.loads(data)
	status = True
        for service in data_json:
                if str(service['Alive']).lower() != expected_status :
                        print('\033[1;91mNEUTRON SERVICES.....FAILED\033[1;m')
                        for service in data_json:
		                if str(service['Alive']).lower() != expected_status:
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


#def check_systemd_services():
def get_controllers_ip():
	print("Enter controller count")
	controller_count = int(raw_input())
	for i in range(0,controller_count):
		controllers_list.append(raw_input("Enter controller ip\n").strip())
	print(controllers_list)
	for controller in controllers_list:
		systemd_service = "ssh heat-admin@" + controller + " sudo systemctl list-units --state=failed 'openstack*' 'neutron*' 'httpd' 'docker' 'ceph*'"
		data = subprocess.check_output(systemd_service, shell=True)
		print(data)



def check_osp13_services():
	check_baremetal_nodes()
	check_cinder()
	check_compute()
	check_neutron(":-)")

def check_osp10_services():
	check_baremetal_nodes()
	check_cinder()
	#check_compute()
	check_neutron("true")
	get_controllers_ip()


def ask_osp_version():
	print("OSP Version(10 or 13)")
	return raw_input()


def main():
	osp_version = int(ask_osp_version())
	if osp_version == 13:
		print("CHECKING SERVICES FOR OSP13")
		check_osp13_services()
	elif osp_version == 10:
		print("CHECKING SERVICES FOR OSP10")
		check_osp10_services()
	else:
		print("Invalid version number")


main()
