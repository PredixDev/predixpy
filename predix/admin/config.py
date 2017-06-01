
import os
import json
import errno


class ServiceConfig(object):
    """
    Base class for reading and writing service configuration
    files to disk.
    """
    def __init__(self, config_file):
        self.config_path = os.path.expanduser(config_file)
        self.data = self._get_service_config()

    def save(self, data):
        """
        Save the given configuration data.
        """
        self.data = data

    def _get_service_config(self):
        """
        Reads in config file of UAA credential information
        or generates one as a side-effect if not yet
        initialized.
        """
        # Should work for windows, osx, and linux environments
        if not os.path.exists(self.config_path):
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

            return {}

        with open(self.config_path, 'r') as data:
            return json.load(data)

    def _write_service_config(self):
        """
        Will write the config out to disk.
        """
        with open(self.config_path, 'w') as output:
            output.write(json.dumps(self.data, sort_keys=True, indent=4))

    def __del__(self):
        """
        Destructor to write out service config to disk at termination
        of a running process.
        """
        self._write_service_config()
