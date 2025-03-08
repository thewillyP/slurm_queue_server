import subprocess
import json
import os
import fcntl

# File path for the job queue
queue_file = "/scratch/wlp9800/queue_server/job_queue.json"


# Ensure the file exists, create it if it doesn't (now inside a function)
def ensure_file_exists():
    if not os.path.exists(queue_file):
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)  # Create the directory if not exists
        with open(queue_file, "w") as f:
            json.dump([], f)  # Initialize with an empty list if the file is created


# Load the queue from file with locking
def load_queue():
    job_queue = []
    try:
        with open(queue_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)  # Lock the file for reading
            job_queue = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)  # Release the read lock
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return job_queue


# Save the queue to file with locking
def save_queue(job_queue):
    with open(queue_file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)  # Lock the file for writing
        json.dump(job_queue, f)
        fcntl.flock(f, fcntl.LOCK_UN)  # Release the write lock


# Submit a job to the queue
def submit_job(total_jobs, t, sweep_id):
    job = {"total_jobs": total_jobs, "time": t, "sweep_id": sweep_id}
    job_queue = load_queue()
    job_queue.append(job)
    save_queue(job_queue)
    print("Job added to the queue.")


if __name__ == "__main__":
    ensure_file_exists()

    # Check SLURM availability
    result = subprocess.run("squeue -V", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SLURM is accessible. Version: {result.stdout.strip()}")
    else:
        print("SLURM access test failed.")
        print(f"Error: {result.stderr.strip()}")

    import sys

    if len(sys.argv) != 4:
        print("Usage: python submit.py <total_jobs> <time> <sweep_id>")
        sys.exit(1)

    submit_job(int(sys.argv[1]), sys.argv[2], sys.argv[3])
