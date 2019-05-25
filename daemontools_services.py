#!/usr/bin/python
import re, os, sys, time

DEBUG_MODE = False

if 'DEBUG_MODE' in os.environ.keys() and os.environ['DEBUG_MODE']!='0':
  DEBUG_MODE = True

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['dev'],
    'supported_by': 'vpnTech'
}

DOCUMENTATION = '''
---
module: daemontools_services

short_description: Query Daemontools Services

version_added: "2.8"

description:
    - "Check Daemontools Services"

options:
    name:
        description:
            - This is the service you want to check. If not specified, checks all services.
        required: false

author:
    - vpnTech
'''

EXAMPLES = '''
- name: Query Services
  daemontools_services:
  register: services
- debug: var=services

'''

RETURN = '''
services:
    description: Daemontools Services
    type: str
    returned: always
msg:
    description: A message
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule

class BaseService(object):
    def __init__(self, module):
        self.module = module
        self.incomplete_warning = False

class DaemontoolsScanService(BaseService):
    def execute_command(self, cmd):
        try:
            (rc, out, err) = self.module.run_command(' '.join(cmd))
        except Exception as e:
            self.module.fail_json(msg="failed to execute: %s" % to_native(e), exception=traceback.format_exc())
        return (rc, out, err)

    def daemontools_enabled(self):
	return True
        try:
            f = open('/service','r')
        except IOError:
            return False


    def gather_services(self):
        services = {}
	if DEBUG_MODE:
  	  print("GATHERING SERVICES")
        if not self.daemontools_enabled():
            return None
        svstat_path = self.module.get_bin_path("svstat", opt_dirs=["/usr/bin", "/usr/local/bin", "/usr/sbin", "/usr/local/sbin","/bin","/sbin"])
	if DEBUG_MODE:
	  print("svstat_path={}".format(svstat_path))

        if svstat_path is None:
            return None

	self.checkServicesCommand = "{} /service/*".format(svstat_path)
        rc, stdout, stderr = self.module.run_command(self.checkServicesCommand, use_unsafe_shell=True)



	if DEBUG_MODE:
          print("daemontools_enabled={}".format(self.daemontools_enabled()))
          print("rc={}".format(rc))
          print("stdout={}".format(stdout))
          print("stderr={}".format(stderr))


        for line in stdout.split("\n"):
            line_data = line.strip().split()
	    if DEBUG_MODE:
	      print('line_data={}'.format(line_data))

            if len(line_data) != 7:
                continue
	    newService = {}
	    newService['path'] = line_data[0]
	    newServiceName = newService['path'].split('/')[-1]
	    newService['state'] = line_data[1]
	    newService['status'] = line_data[6]

	    try:
	      newService['pid'] = int(line_data[3].replace(')',''))
	    except Exception as e:
	      newService['pid'] = None

	    try:
	      newService['seconds'] = int(line_data[4])
	    except Exception as e:
	      newService['seconds'] = None

	    if newService['state'] == 'up':
		pass
	    else:
		pass

	    if DEBUG_MODE:
	      print("newService={}".format(newService))

            services[newServiceName] = newService

        return services


def run_module():

    if DEBUG_MODE:
      print("RUN GATHERING SERVICES")

    service_modules = (DaemontoolsScanService,)
    all_services = {}
    incomplete_warning = False


    module_args = dict(
        name=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        msg='',
        services={},
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    """
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    if module.params['new']:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the msg and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)
    """

    svcmod = DaemontoolsScanService(module)
    services = svcmod.gather_services()

    if services == None or len(services) == 0:
        result['skipped'] = True
	result['msg'] = "Failed to find any services. Sometimes this is due to insufficient privileges."


    result['services'] = services

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()




def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def getTimestampMilliseconds():
    return int(time.time() * 1000)

def getTimestamp():
    return int(time.time())
