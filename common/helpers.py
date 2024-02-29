import argparse
import re
from configparser import ConfigParser
from azure.batch import BatchServiceClient
import azure.batch.models as batchmodels

from typing import List

CONFIGURATION_FILE_NAME="azure-configuration.cfg"
OS_TYPE={"linux", "winbdows"}

# Configuration 
def print_configuration(config: ConfigParser):
    """print the Configuration

    Args:
        config (ConfigParser): the Configuration
    """
    configuration_dict = {s: dict(config.items(s))
                          for s in config.sections()}
    print("----------------------")
    print(configuration_dict)
    print("----------------------")

# print_batch_exception
def print_batch_exception(batch_exception: batchmodels.BatchErrorException):
    """
    Prints the contents of the specified Batch exception.
    :param batch_exception:
    """
    print('-------------------------------------------')
    print('Exception encountered:')
    if batch_exception.error and \
            batch_exception.error.message and \
            batch_exception.error.message.value: # type: ignore
        print(batch_exception.error.message.value) # type: ignore
        if batch_exception.error.values: # type: ignore
            print()
            for mesg in batch_exception.error.values: # type: ignore
                print(f'{mesg.key}:\t{mesg.value}')
    print('-------------------------------------------')

# create pool
def create_pool_if_not_exist(batch_client: BatchServiceClient, pool: str)-> None:
    """Creates a pool if it doesn't already exist.

    Args:
        batch_client (BatchServiceClient): Batch client object.
        pool (str): Name of the pool to create.
    """
    try:
        print("Attempting to create pool:", pool)
        batch_client.pool.add(pool)
        print("Created pool:", pool)
    except batchmodels.BatchErrorException as e:
        if e.error and e.error.code != "PoolExists": # type: ignore
            raise
        else:
            print("Pool {!r} already exists".format(pool))

# wrap_commands
def wrap_commands_in_shell(ostype: str, commands: list)-> str:
    """Create a shell script that executes a list of commands in order.

    Args:
        ostype (str): OS type of the node.  Currently, only linux is supported.
        commands (List): List of commands to execute.

    Returns:
        str: A string containing the contents of the shell script.
    """
    if ostype.lower() != 'linux':
        return (f'/bin/bash -c \'set -e; set -o pipefail; {";".join(commands)}\'')
    elif ostype.lower() != 'windows':
        return (f'cmd.exe /c {" & ".join(commands)}')
    else:
        raise ValueError(f'Unknown OS type: {ostype}')

# create argparser configuration
def get_arguments():

    parser = argparse.ArgumentParser(description="Welcome to create your Batch Configuration")
    parser.add_argument("-pi", "--pool", type=str, dest="pool_id", help="Name of the VM Pool for Azure Batch", default="testpool")
    parser.add_argument("-os", "--ostype", dest='os_type', type=str, choices=OS_TYPE, help="The type of operating system default is 'linux'", default="linux")
    parser.add_argument("-vm", "--vm-size", dest="vm_size", type=str, help="The size of the VM", default="standard_a1_v2")
    options = parser.parse_args()
    if not options.pool_id:
        parser.error("[-] Please enter a name for the pool")
    return options

# create_pool
def create_pool_and_wait_for_nodes(batch_client: BatchServiceClient, pool_id: str):
    pass