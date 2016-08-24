#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from . import run_command, logger, ArgsNotCorrect, CommandNotFound, CommandRunFailed, VM_DEFAULT_CONFIG
from model import CBMC


def get_ipmi():
    try:
        code, ipmi_cmd = run_command("which /usr/local/bin/ipmi_sim")
        return ipmi_cmd.strip(os.linesep)
    except CommandRunFailed as e:
        raise CommandNotFound("/usr/local/bin/ipmi_sim")


def status_ipmi():
    try:
        run_command("pidof ipmi_sim")
        print "InfraSim IPMI service is running"
    except CommandRunFailed as e:
        print "Infrasim IPMI service is stopped"


def start_ipmi(conf_file=VM_DEFAULT_CONFIG):
    try:
        with open(conf_file, 'r') as f_yml:
            conf = yaml.load(f_yml)
        if "bmc" in conf:
            bmc = CBMC(conf["bmc"])
        else:
            bmc = CBMC()
        bmc.set_type(conf["type"])
        bmc.init()
        bmc.precheck()
        cmd = bmc.get_commandline()
        logger.debug(cmd)
        run_command(cmd+" &", True, None, None)

        logger.info("bmc start")
    except CommandRunFailed as e:
        logger.error(e.value)
        raise e
    except ArgsNotCorrect as e:
        logger.error(e.value)
        raise e


def stop_ipmi():
    ipmi_stop_cmd = "pkill ipmi_sim"
    try:
        run_command(ipmi_stop_cmd, True, None, None)
        logger.info("ipmi stopped")
    except CommandRunFailed as e:
        logger.error("ipmi stop failed")
