#!/usr/bin/env python3
import subprocess
import sys
import time

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
                        print(f"ERROR: {program_name} is {status}")
                        all_running = False
                    else:
                        print(f"OK: {program_name} is running")
        
        return all_running
        
    except Exception as e:
        print(f"ERROR checking supervisor status: {e}")
        return False

if __name__ == "__main__":
    # Give services time to start
    time.sleep(5)
    
    if check_supervisor_status():
        print("All services are running")
        sys.exit(0)
    else:
        print("Some services are not running")
        sys.exit(1)
