'''
*********************************************************
Copyright @ 2015 EMC Corporation All Rights Reserved
*********************************************************
'''
import unittest
import os
import subprocess
import re
import time
from infrasim import model
from infrasim import helper
from infrasim import InfraSimError
from test import fixtures
import urllib


test_img_file = "/tmp/kcs.img"
# ipmitool commands to test
cmd_prefix = 'ipmitool -H 127.0.0.1 -U admin -P admin raw '

get_vpd_cmd = cmd_prefix + '0x30 0xE1 0x0a 0x00 0x00 0x4c'
get_vpd_error_cmd = cmd_prefix + '0x30 0xE1 0x0a 0x00 0x00 0x4f'


def load_oem_data(oem_data_file):
    MD5 = '0a4885a2f3d72e7cd0508c0fc6445aae'
    DOWNLOAD_URL = 'https://raw.eos2git.cec.lab.emc.com/InfraSIM/emu_data/master/warnado/warnado_pp_bmc_a/oem_data.json?token=AAAKUo37ecNyHS-YPgDikxwUYx5omC5sks5aZabPwA%3D%3D'
    try:
        helper.fetch_image(DOWNLOAD_URL, MD5, oem_data_file)
    except InfraSimError, e:
        print e.value
        assert False
    '''
    info = urllib.urlopen(url)
    info = info.read()
    with open('oem_data.json', 'w') as f:
        f.write(info)
    '''

def run_command(cmd="", shell=True, stdin=None, stdout=None, stderr=None):
    child = subprocess.Popen(cmd, shell=shell, stdout=stdout, stderr=stderr)
    cmd_result = child.communicate()
    cmd_return_code = child.returncode
    return cmd_return_code, cmd_result


class test_ipmi_oem_command(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        node_info = {}
        fake_config = fixtures.FakeConfig()
        node_info = fake_config.get_node_info()
        '''
        node_info["compute"]["storage_backend"] = [{
                "type": "ahci",
                "max_drive_per_controller": 6,
                "drives": [
                    {
                        "size": 8,
                    }
                ]}, {
                "type": "nvme",
                "cmb_size": 256,
                "drives": [{"size": 8}]
            }]
        '''
        node = model.CNode(node_info)
        node.init()
        node.precheck()
        node.start()
        # FIXME: sleep is not a good way to wait qemu starts up.
        time.sleep(3)
        oem_file_path = os.path.join(node.workspace.get_workspace(), "data/oem_data.json")
        load_oem_data(oem_file_path)

    @classmethod
    def tearDownClass(cls):
        fake_config = fixtures.FakeConfig()
        node_info = fake_config.get_node_info()
        node = model.CNode(node_info)
        node.init()
        node.stop()
        node.terminate_workspace()

    def test_get_drive_healthdata(self):
        try:
            returncode, output = run_command(get_vpd_cmd,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
            self.assertEqual(returncode, 0)
        except:
            assert False

    def test_get_drive_healthdata_error(self):
        try:
            returncode, output = run_command(get_vpd_error_cmd,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
            self.assertEqual(returncode, 1)
        except:
            assert False
