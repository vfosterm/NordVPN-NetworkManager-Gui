# -*- coding: utf-8 -*-
import configparser
import getpass
import logging
import os
import re
logger = logging.getLogger(__name__)


network_connections_path = "/etc/NetworkManager/system-connections/"
KILLSWITCH_SCRIPT = "/etc/NetworkManager/dispatcher.d/nordnmgui_killswitch"
AUTO_CONNECT_SCRIPT = "/etc/NetworkManager/dispatcher.d/nordnmgui_autoconnect"


def format_std_string(input_string):
    return input_string.decode('utf-8').replace('\n', ' ')


class ConnectionConfig(object):
    def __init__(self, connection_name):
        self.config = configparser.ConfigParser(interpolation=None)
        self.path = None

        try:
            # Get all system-connection files and check for a match, with or without the new '.nmconnection' extension
            _, _, file_names = next(os.walk(network_connections_path, (None, None, [])))
            for file_name in file_names:
                if re.search(re.escape(connection_name) + "(.nmconnection)?", file_name):
                    # Found a match, so store the full path as self.path and break out
                    self.path = os.path.join(network_connections_path, file_name)
                    break

            if self.path and os.path.isfile(self.path):
                self.config.read(self.path)
            else:
                logger.error("VPN config file not found in system-connections! (%s)", connection_name)

        except Exception as ex:
            logger.error(ex)

    def save(self):
        try:
            if self.path:
                with open(self.path, 'w') as config_file:
                    self.config.write(config_file)

                return True
            else:
                logger.error("Could not save VPN Config. Invalid path.")
                return False

        except Exception as ex:
            logger.error(ex)
            return False

    def disable_ipv6(self):
        self.config['ipv6']['method'] = 'ignore'

    def set_dns_nameservers(self, dns_list):
        self.config['ipv4']['dns-priority'] = '-1'

        if dns_list:
            dns_string = ';'.join(map(str, dns_list))

            self.config['ipv4']['dns'] = dns_string
            self.config['ipv4']['ignore-auto-dns'] = 'true'

    def set_user(self, user):
        self.config['connection']['permissions'] = "user:" + user + ":;"

    def set_credentials(self, username, password):
        self.config['vpn']['password-flags'] = "0"
        self.config['vpn']['username'] = username
        self.config['vpn-secrets'] = {}
        self.config['vpn-secrets']['password'] = password


def get_current_user():
    username = os.getenv("SUDO_USER")
    if not username:
        username = str(getpass.getuser())

    return username
