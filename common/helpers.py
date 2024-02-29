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
    parser.add_argument("-pi", "--pool", type=str, dest="pool_id",required=True, help="Name of the VM Pool for Azure Batch", default="testpool")
    parser.add_argument("-os", "--ostype", dest='os_type', type=str, choices=OS_TYPE, help="The type of operating system default is 'linux'", default="linux")
    parser.add_argument("-vm", "--vm-size", dest="vm_size", type=str, help="The size of the VM", default="standard_a1_v2")
    
    options = parser.parse_args()
    # if not options.pool_id:
    #     parser.error("[-] Please enter a name for the pool")
    return options

# create_pool
def create_pool_and_wait_for_nodes(batch_client: BatchServiceClient, pool_id: str, pool_config: ConfigParser, vm_size: str, os_type: str, env_config: List[batchmodels.EnvironmentSetting] | None)-> None:
    """Create a pool of compute nodes with the specified OS settings.

    Args:
        batch_client (BatchServiceClient): The BatchServiceClient object used to interact with the Batch service.
        pool_id (str): The name of the pool to be created.
        pool_config (ConfigParser): The configuration object containing the pool settings.
        vm_size (str): The size of the virtual machines in the pool.
        os_type (str): The operating system type of the pool.
        env_config (List[batchmodels.EnvironmentSetting] | None): A list of environment settings for the pool.

    Returns:
        None: This function does not return anything.

    Raises:
        None: This function does not raise any exceptions.
    """
    # check if pool exists if not create it
    if not batch_client.pool.exists(pool_id=pool_id) and os_type.lower == "linux":
        new_pool = batchmodels.PoolAddParameter(
            id=pool_id,
            virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
                image_reference=batchmodels.ImageReference(
                    publisher= pool_config.get("POOL", "publisher"),
                    offer= pool_config.get("POOL", "offer"),
                    sku= pool_config.get("POOL", "sku"),
                    version= "latest"
                ),
                node_agent_sku_id= pool_config.get("POOL", "node_agent_sku_id"),
            ),
            vm_size=vm_size,
            enable_inter_node_communication=True,
            target_dedicated_nodes= int(pool_config.get("POOL", "target_dedicated_nodes")),
            start_task=batchmodels.StartTask(
                command_line=wrap_commands_in_shell(
                    os_type,
                    [
                        "echo 'Hello from the Batch Hello World start task!'",
                    ]
                ),
                environment_settings=env_config,
                user_identity=batchmodels.UserIdentity(
                    auto_user=batchmodels.AutoUserSpecification(
                        scope=batchmodels.AutoUserScope.pool,
                        elevation_level=batchmodels.ElevationLevel.admin
                    )
                ),
                max_task_retry_count=2,
                wait_for_success=True,
            ),
        )
        batch_client.pool.add(new_pool)
        # Windows pool creation
    elif not batch_client.pool.exists(pool_id=pool_id) and os_type.lower == "windows":
        new_pool = batchmodels.PoolAddParameter(
            id=pool_id,
            virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
                image_reference=batchmodels.ImageReference(
                    publisher= pool_config.get("WINPOOL", "publisher"),
                    offer= pool_config.get("WINPOOL", "offer"),
                    sku= pool_config.get("WINPOOL", "sku"),
                    version= "latest"
                ),
                node_agent_sku_id= pool_config.get("WINPOOL", "node_agent_sku_id"),
            ),
            vm_size=vm_size,
            target_dedicated_nodes= int(pool_config.get("WINPOOL", "target_dedicated_nodes")),
            start_task=batchmodels.StartTask(
                command_line=wrap_commands_in_shell(
                    os_type,
                    [
                        "echo 'Hello from the Batch Hello World start task!'",
                    ]
                ),
                environment_settings=env_config,
                user_identity=batchmodels.UserIdentity(
                    auto_user=batchmodels.AutoUserSpecification(
                        scope=batchmodels.AutoUserScope.pool,
                        elevation_level=batchmodels.ElevationLevel.admin
                    )
                ),
                max_task_retry_count=2,
                wait_for_success=True,
            ),
        )