import sys
import time
import os
sys.path.append(os.path.abspath("../plot"))

import logging
from csv import writer
from config import get_config
from hpx_logger import setup_logging

import gaussian_process as gpppy
from plotting import *
import numpy as np

logger = logging.getLogger()
log_filename = "./hpx_logs.log"

def gpppy_run(config, output_csv_obj, n_train, l, cores):
    
    total_t = time.time()
    
    n_tile_size = gpppy.compute_train_tile_size(n_train, config["N_TILES"])
    m_tiles, m_tile_size = gpppy.compute_test_tiles(config["N_TEST"], config["N_TILES"], n_tile_size)
    hpar = gpppy.Hyperparameters(learning_rate=0.1, opt_iter=3, m_T=[0,0,0], v_T=[0,0,0])
    train_in = gpppy.GP_data(config["train_in_file"], n_train)
    train_out = gpppy.GP_data(config["train_out_file"], n_train)
    test_in = gpppy.GP_data(config["test_in_file"], config["N_TEST"])
    
    ###### GP object ######
    init_t = time.time()
    gp = gpppy.GP(train_in.data, train_out.data, config["N_TILES"], n_tile_size, trainable=[True, True, True])
    init_t = time.time() - init_t
    
    # Init hpx runtime but do not start it yet
    gpppy.start_hpx(sys.argv, cores)
    
    # Perform optmization
    opti_t = time.time()
    losses = gp.optimize(hpar)
    opti_t = time.time() - opti_t
    logger.info("Finished optimization.")
    
    # Predict
    pred_t = time.time()
    pr = gp.predict(test_in.data, m_tiles, m_tile_size)
    pred_t = time.time() - pred_t
    logger.info("Finished making predictions.") 
    
    # Stop HPX runtime
    gpppy.stop_hpx()
    
    TOTAL_TIME = time.time() - total_t
    INIT_TIME = init_t
    OPTI_TIME = opti_t
    PREDICTION_TIME = pred_t
    
    row_data = [config["N_CORES"], size_train, config["N_TEST"], config["N_REG"], 
                TOTAL_TIME, INIT_TIME, OPTI_TIME, PREDICTION_TIME, l]
    output_csv_obj.writerow(row_data)
    
    logger.info("Completed iteration.")

def execute():
    """
    Execute the main process:
        - Set up logging.
        - Load configuration file.
        - Initialize output CSV file.
        - Write header to the output CSV file.
        - Set up TensorFlow and GPflow configurations based on the loaded config.
        - Iterate through different training sizes and for each training size
        loop for a specified amount of times while executing `gpflow_run` function.
    """
    setup_logging(log_filename, True, logger)
    logger.info("\n")
    logger.info("-" * 40)
    logger.info("Load config file.")
    config = get_config()
    
    file_exists = os.path.isfile("./output.csv")
    output_file = open("./output.csv", "a", newline="")
    output_csv_obj = writer(output_file)
    
    if not file_exists:
        logger.info("Write output file header")
        header = ["Cores", "N_train", "N_test", "N_TILES", "N_regressor", "Total_time",
             "Init_time", "Optimization_Time", "Predict_time", "N_loop"]
        output_csv_obj.writerow(header)

    start = config["START"]
    end = config["END"]
    step = config["STEP"]
   
    for i in range(start, end+step, step):
        for l in range(config["LOOP"]):
            logger.info("*" * 40)
            logger.info(f"Train Size: {i}, Loop: {l}")
            gpppy_run(config, output_csv_obj, i, l, 1)
            
        
    for core in range(1, 6):
        for i in range(start, end+step, step):
            for l in range(config["LOOP"]):
                logger.info("*" * 40)
                logger.info(f"Train Size: {i}, Loop: {l}")
                gpppy_run(config, output_csv_obj, i, l, 2**core)
        
    
if __name__ == "__main__":
    execute()