#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=14G
#SBATCH --time=00:15:00
#SBATCH --job-name=build
#SBATCH --error=build.err
#SBATCH --output=build.out
#SBATCH --cpus-per-task=10
#SBATCH --mail-type=END
#SBATCH --mail-user=wlp9800@nyu.edu

# Dynamically pass user, image, and tag as environment variables
USER=${USER:-"wlp9800"}  # Default to wlp9800 if not provided

# Docker URL constructed dynamically with IMAGE and TAG
DOCKER_URL="docker://thewillyp/slurm-queue-server:${TAG}"
SAVE_DIR="/scratch/${USER}/"

# Build the Singularity image
singularity build --force /scratch/${USER}/images/slurm_queue_server.sif ${DOCKER_URL}

# Create the overlay
singularity overlay create --size 512 /scratch/${USER}/images/slurm_queue_server.sif

# 0.5 GiB
