#!/usr/bin/env python3.8

import sqlite3
from datetime import datetime
from kickable_vpn_tunnel_groups import gateway_kgroup_pairs
from admins import admins


def create_kick_group_throttiling_table(conn, initial_entries):
    try:
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kick_group_throttling (
                gateway TEXT NOT NULL,
                group_name TEXT NOT NULL,
                time INTEGER NOT NULL,
                PRIMARY KEY (gateway, group_name)
            )
        """)
        
        # Prepare the data for insertion
        # Set initial time to 0 (epoch) to allow immediate access
        data_to_insert = [
            (entry['gateway'], entry['group'], 0) for entry in initial_entries['kgroups']
        ]
        
        # Insert or ignore to avoid duplicate entries
        cursor.executemany("""
            INSERT OR IGNORE INTO kick_group_throttling (gateway, group_name, time)
            VALUES (?, ?, ?)
        """, data_to_insert)
        
        # Commit the changes
        conn.commit()
        print("Database table kick_group_throttling initialized successfully.")
    finally:
        # Close the connection
        conn.close()

def create_admins_table(conn, initial_entries):
    try:
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                username TEXT NOT NULL,
                hash TEXT NOT NULL,
                last_user_kick_time INTEGER NOT NULL,
                PRIMARY KEY (username)
            )
        """)
        
        # Prepare the data for insertion
        # Set initial time to 0 (epoch) to allow immediate access
        data_to_insert = [
            (entry['username'], entry['hash'], 0) for entry in initial_entries['admins']
        ]
        
        # Insert or ignore to avoid duplicate entries
        cursor.executemany("""
            INSERT OR IGNORE INTO admins (username, hash, last_user_kick_time)
            VALUES (?, ?, ?)
        """, data_to_insert)
        
        # Commit the changes
        conn.commit()
        print("Database table admins initialized successfully.")
    finally:
        # Close the connection
        conn.close()

def initialize_db(db_path, initial_entries):
    """
    Initializes the SQLite database with the required table and pre-fills it.

    Args:
        db_path (str): Path to the SQLite database file.
        initial_entries (list of dict): List of dictionaries with 'gateway' and 'group' keys.
    """
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    create_kick_group_throttiling_table(conn, initial_entries)

    conn = sqlite3.connect(db_path)
    create_admins_table(conn, initial_entries)

if __name__ == "__main__":
    # Define the path to the SQLite database file
    DATABASE_PATH = 'vpnmapp.db'
    
    # Define the initial gateway and group combinations
    initial_data = dict()
    initial_data['kgroups'] = gateway_kgroup_pairs
    initial_data['admins'] = admins
    
    # Initialize the database
    initialize_db(DATABASE_PATH, initial_data)