#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
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


singularity run --writable-tmpfs \
  --env WANDB_API_KEY=${WANDB_API_KEY} \
  --env IMAGE=${IMAGE} \
  --env USER=${USER} \
  --bind /scratch/${USER}:/scratch,/home/${USER}/dev/rnn-test:/myqueue \
  -B /opt/slurm,/usr/lib64/libreadline.so.6,/usr/lib64/libhistory.so.6,/usr/lib64/libtinfo.so.5,/var/run/munge,/usr/lib64/libmunge.so.2,/usr/lib64/libmunge.so.2.0.0,/run/munge \
  /scratch/${USER}/images/slurm_queue_server.sif 
