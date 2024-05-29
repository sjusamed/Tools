import digitalocean
import time
import paramiko
from scp import SCPClient
import numpy as np
import os
import pandas as pd

# Replace with your DigitalOcean API token
TOKEN = 'your_digitalocean_api_token'

# SSH key you added to DigitalOcean (find its ID on the SSH keys page)
SSH_KEY_ID = 'your_ssh_key_id'

# Replace with your local paths to the script and CSV files
SCRIPT_PATH = 'path/to/scrape_mck.py'
CSV_PATH = 'path/to/mck.csv'

# Number of droplets to create
NUM_DROPLETS = 5

# Droplet size slug (e.g., 's-1vcpu-1gb')
SIZE = 's-1vcpu-1gb'

# Droplet image (Ubuntu 20.04)
IMAGE = 'ubuntu-20-04-x64'

# Region (e.g., 'nyc3')
REGION = 'nyc3'

# Function to create a new droplet
def create_droplet(manager, name):
    droplet = digitalocean.Droplet(
        token=TOKEN,
        name=name,
        region=REGION,
        image=IMAGE,
        size_slug=SIZE,
        ssh_keys=[SSH_KEY_ID],
        backups=False
    )
    droplet.create()
    return droplet

# Function to wait for droplet creation
def wait_for_droplets(droplets):
    for droplet in droplets:
        actions = droplet.get_actions()
        for action in actions:
            action.load()
            while action.status != 'completed':
                time.sleep(5)
                action.load()

# Function to split CSV file
def split_csv(num_chunks):
    df = pd.read_csv(CSV_PATH)
    chunks = np.array_split(df, num_chunks)
    filenames = []
    for i, chunk in enumerate(chunks):
        filename = f'mck_part_{i}.csv'
        chunk.to_csv(filename, index=False)
        filenames.append(filename)
    return filenames

# Function to upload files and run the script on each droplet
def setup_and_run_script(droplet, csv_filename):
    ip_address = droplet.ip_address
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the droplet
    ssh.connect(ip_address, username='root')

    # Create SCP client
    scp = SCPClient(ssh.get_transport())

    # Upload files
    scp.put(SCRIPT_PATH, '/root/scrape_mck.py')
    scp.put(csv_filename, f'/root/{csv_filename}')

    # Install required packages and run the script
    commands = [
        'apt update',
        'apt install -y python3-pip',
        'pip3 install requests beautifulsoup4 pandas fake_useragent',
        f'python3 /root/scrape_mck.py /root/{csv_filename}'
    ]
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())

    # Close connections
    scp.close()
    ssh.close()

def main():
    manager = digitalocean.Manager(token=TOKEN)
    droplets = []

    # Create droplets
    for i in range(NUM_DROPLETS):
        name = f'scraper-droplet-{i}'  # Custom naming pattern
        droplet = create_droplet(manager, name)
        droplets.append(droplet)
        print(f'Created droplet: {name}')

    # Wait for droplets to be created
    wait_for_droplets(droplets)

    # Refresh droplet information to get IP addresses
    for droplet in droplets:
        droplet.load()
        print(f'Droplet {droplet.name} IP: {droplet.ip_address}')

    # Split the CSV file
    csv_filenames = split_csv(NUM_DROPLETS)

    # Setup and run the script on each droplet
    for i, droplet in enumerate(droplets):
        setup_and_run_script(droplet, csv_filenames[i])

if __name__ == '__main__':
    main()
