#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=2-00:00:00
#SBATCH --job-name=queue
#SBATCH --cpus-per-task=1
#SBATCH --output="/scratch/wlp9800/logs/queue-%j.out"
#SBATCH --error="/scratch/wlp9800/logs/queue-%j.err"

set -e

if [ -z "$USER" ]; then
    echo "Error: USER environment variable must be set!"
    exit 1
fi

if [ -z "$IMAGE" ]; then
    echo "Error: IMAGE environment variable must be set!"
    exit 1
fi

# Ensure WANDB_API_KEY is set
if [ -z "$WANDB_API_KEY" ]; then
    echo "Error: WANDB_API_KEY environment variable must be set!"
    exit 1
fi


python /home/${USER}/dev/slurm_queue_server/poller.py $USER $IMAGE $WANDB_API_KEY