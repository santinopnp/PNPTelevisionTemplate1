#!/usr/bin/env python3
import subprocess
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_supervisor_status():
    """Check if all programs are running"""
    try:
        result = subprocess.run(
            ['supervisorctl', 'status'],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        all_running = True
        
        for line in lines:
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    program_name = parts[0]
                    status = parts[1]
                    
                    if status != 'RUNNING':
                        logger.error("ERROR: %s is %s", program_name, status)
                        all_running = False
                    else:
                        logger.info("OK: %s is running", program_name)
        
        return all_running
        
    except Exception as e:
        logger.error("ERROR checking supervisor status: %s", e)
        return False

if __name__ == "__main__":
    # Give services time to start
    time.sleep(5)
    
    if check_supervisor_status():
        logger.info("All services are running")
        sys.exit(0)
    else:
        logger.error("Some services are not running")
        sys.exit(1)
