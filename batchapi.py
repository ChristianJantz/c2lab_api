#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ast import arg
from calendar import c
from configparser import ConfigParser
import azure.batch.models as batchmodels
import argparse
import os
import common.helpers


# execute_batch
def execute_batch(global_config: ConfigParser, batch_config: ConfigParser, args_conf: argparse.Namespace)-> None:
    
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
    
    # Environment settings
    env_conf = [
        batchmodels.EnvironmentSetting(
            name="BATCH_DOWNLOAD_URL",
            value="https://github.com/Azure/batch-insights/releases/download/{}/batch-insights".format(global_config.get("INSIGHTS", "batch_git_version"))
        ),
        batchmodels.EnvironmentSetting(
            name="APP_INSIGHTS_APP_ID",
            value=global_config.get("INSIGHTS", "app_insights_app_id")
        ),
        batchmodels.EnvironmentSetting(
            name="APP_INSIGHTS_INSTRUMENTATION_KEY",
            value=global_config.get("INSIGHTS", "app_insights_instrumentation_key")
        ),
        
    ]
    
    try:
        pass
    except batchmodels.BatchErrorException as e:
        common.helpers.print_batch_exception(e)
        raise

if __name__ == "__main__":
    
    global_cfg = ConfigParser()
    global_cfg.read(common.helpers.CONFIGURATION_FILE_NAME)
    
    batch_cfg = ConfigParser()
    batch_cfg.read("resources/"+ os.path.splitext(os.path.basename(__file__))[0] + ".cfg")
    
    args_conf = common.helpers.get_arguments()
    
    execute_batch(global_config=global_cfg, batch_config=batch_cfg, args_conf=args_conf)