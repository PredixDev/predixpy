
import os
import logging

from cryptography.fernet import Fernet


def is_cf_env():
    # MAINT: consider CF_INSTANCE_ADDR
    return ('VCAP_SERVICES' in os.environ) or ('VCAP_APPLICATION' in os.environ)

def get_crypt_key(key_path):
    """
    Get the user's PredixPy manifest key.  Generate and store one if not
    yet generated.
    """
    key_path = os.path.expanduser(key_path)
    if os.path.exists(key_path):
        with open(key_path, 'r') as data:
            key = data.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'w') as output:
            output.write(key)

    return key

def get_env_key(obj, key=None):
    """
    Return environment variable key to use for lookups within a
    namespace represented by the package name.

    For example, any varialbes for predix.security.uaa are stored
    as PREDIX_SECURITY_UAA_KEY
    """
    return str.join('_', [obj.__module__.replace('.','_').upper(),
        key.upper()])

def get_env_value(obj, attribute):
    """
    Returns the environment variable value for the attribute of
    the given object.

    For example `get_env_value(predix.security.uaa, 'uri')` will
    return value of environment variable PREDIX_SECURITY_UAA_URI.

    """
    varname = get_env_key(obj, attribute)
    var = os.environ.get(varname)
    if not var:
        raise ValueError("%s must be set in your environment." % varname)

    return var

def set_env_value(obj, attribute, value):
    """
    Set the environment variable value for the attribute of the
    given object.

    For example, `set_env_value(predix.security.uaa, 'uri', 'http://...')`
    will set the environment variable PREDIX_SECURITY_UAA_URI to the given
    uri.
    """
    varname = get_env_key(obj, attribute)
    os.environ[varname] = value
    return varname

class PredixCloudRequiredError(Exception):
    """
    A Predix Cloud Requirement Error will be raised when trying to utilize
    a service that is blocked for access anywhere outside of the Predix Cloud.
    """
    def __init__(self, message=None):
        if not message:
            message = "Service only available running in Predix Cloud Foundry environment."

        logging.warn(message)
        super(PredixCloudRequiredError, self).__init__(message)
