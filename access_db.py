#!/usr/bin/env python3.8

import sqlite3
import datetime
import traceback
from admins import get_admin_last_user_kick_time

db = 'vpnmapp.db'

def kick_user_throttle(admin_username, db_path=db, threshold_seconds=20):
    action_permission = True

    current_time = int(datetime.datetime.now().timestamp())
    last_user_kick_time = get_admin_last_user_kick_time(db_path, admin_username)
    if (current_time - last_user_kick_time) >= threshold_seconds:
        action_permission = True
        wait_time = 0
        print(f"Action kicking user by {admin_username} is permitted by throttling")  # Entry does not exist # change to logging
    else:
        action_permission = False
        wait_time = threshold_seconds - (current_time - last_user_kick_time)
        print(f'Action kicking user by {admin_username} is denied by throttling, wait {wait_time}')  # Entry does not exist # change to logging

    return action_permission, wait_time





def kick_group_throttle(gateway='default', group='default', db_path=db, threshold_minutes=7):
    """
    Writes the current access time to the database if the last access was more than
    'threshold_minutes' ago. Outputs "SUCCESSFUL" or "HAS TO WAIT" accordingly.

    Args:
        gateway (str): The gateway name. Defaults to 'default'.
        group (str): The group name. Defaults to 'default'.
        db_path (str): Path to the SQLite database file. Defaults to 'throttling.db'.
        threshold_minutes (int): The threshold in minutes. Defaults to 10.
    """
    # Calculate threshold in seconds
    wait_time = 0
    action_permission = False
    threshold_seconds = threshold_minutes * 60
    
    # Get current Unix epoch time
    current_time = int(datetime.datetime.now().timestamp())
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # Fetch the last access time for the given gateway and group
        cursor.execute("""
            SELECT time FROM kick_group_throttling
            WHERE gateway = ? AND group_name = ?
        """, (gateway, group))
        result = cursor.fetchone()
        
        if result is None:
            print(f"GROUP {group} on {gateway} IS NOT THROTTLED, UPDATE THE DB")  # Entry does not exist # change to logging
            action_permission = True
            return action_permission, 0
        
        last_access_time = result[0]
        

        # Check if the threshold has been exceeded
        if (current_time - last_access_time) >= threshold_seconds:
            # Update the access time to current time
            cursor.execute("""
                UPDATE kick_group_throttling
                SET time = ?
                WHERE gateway = ? AND group_name = ?
            """, (current_time, gateway, group))
            conn.commit()
            action_permission = True
            print(f"ACTION Kicking {group} from {gateway} is PERMITTED BY THROTTLING") # change to logging
        else:
            action_permission = False
            wait_time = threshold_seconds - (current_time - last_access_time)
            print(f"Kicking group {group} from {gateway}"
                  f" IS NOT PERMITTED BY THROTTLING, "
                  f"WAIT: {wait_time} seconds")
    except:
        print('An error occured while running keep group throtting ({group} on {gateway})')
        print(e)
        traceback.print_exc()
    finally:
        # Close the connection                
        conn.close()
        return action_permission, wait_time

if __name__ == "__main__":
    #unnecessary for the broader module:
    import argparse

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Access Throttling Script")
    parser.add_argument('--gateway', type=str, default='default', help='Gateway name')
    parser.add_argument('--group', type=str, default='default', help='Group name')
    parser.add_argument('--db', type=str, default='vpnmapp.db', help='Path to the SQLite DB file')
    parser.add_argument('--threshold', type=int, default=10, help='Threshold in minutes')
    
    args = parser.parse_args()
    
    # Call the function with parsed arguments
    kick_group_throttle(
        gateway=args.gateway,
        group=args.group,
        db_path=args.db,
        threshold_minutes=args.threshold
    )