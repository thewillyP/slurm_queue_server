#!/bin/bash

# Set environment variable for libraries
export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH

# Add slurmadmin user and group to /etc/passwd and /etc/group
echo "slurmadmin:x:300:300::/opt/slurm/slurm:/bin/false" >> /etc/passwd
echo "slurmadmin:x:300:" >> /etc/group

# Run the Python script (queue_server.py)
exec python /workspace/queue_server.py
