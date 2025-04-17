#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=6:00:00
#SBATCH --job-name=queue
#SBATCH --cpus-per-task=1
#SBATCH --output="/scratch/wlp9800/logs/queue-%j.out"
#SBATCH --error="/scratch/wlp9800/logs/queue-%j.err"


python /home/${USER}/dev/slurm_queue_server/poller.py
