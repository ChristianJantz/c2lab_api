from calendar import c
from configparser import ConfigParser
from math import e
import azure.batch.models as batchmodels
import argparse
import os
import common.helpers


# execute_batch
def execute_batch(global_config: ConfigParser, batch_config: ConfigParser)-> None:
    
    batch_account_name = global_config.get("AZBATCH", "batch_account_name")
    batch_account_key = global_config.get("AZBATCH", "batch_account_key")
    batch_account_url = global_config.get("AZBATCH", "batch_account_url")
    
    blob_account_name = global_config.get("STORAGE", "storage_account_name")
    blob_account_key = global_config.get("STORAGE", "storage_account_key")  
    blob_account_url = global_config.get("STORAGE", "storage_account_url")
    
    pool_id = batch_config.get("POOL", "pool_id")    
    job_id = batch_config.get("JOB", "job_id")

    common.helpers.print_configuration(global_config)
    common.helpers.print_configuration(batch_config)
    
    if not common.helpers.create_pool_if_not_exist:
        pass

if __name__ == "__main__":
    
    global_cfg = ConfigParser()
    global_cfg.read(common.helpers.CONFIGURATION_FILE_NAME)
    
    batch_cfg = ConfigParser()
    batch_cfg.read("resources/"+ os.path.splitext(os.path.basename(__file__))[0] + ".cfg")
    
    
    execute_batch(global_config=global_cfg, batch_config=batch_cfg)