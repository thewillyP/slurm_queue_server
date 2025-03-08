import subprocess
import json
import time
import fcntl
import sys

# File path for the job queue
queue_file = "/scratch/queue_server/job_queue.json"


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


# Polling for the number of running jobs
def get_running_jobs():
    result = subprocess.run(
        "squeue -u wlp9800 -h -t pending,running -r | wc -l", shell=True, capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


# Submit a job to SLURM using sbatch
def submit_job(user, image, wandb_api_key, t, array, sweep_id):
    sbatch_command = f"cd /home/{user}/dev/rnn-test && /opt/slurm/bin/sbatch --export=USER={user},IMAGE={image},WANDB_SWEEP_ID={sweep_id},WANDB_API_KEY={wandb_api_key} --time={t} --array={array} run.slurm"
    subprocess.run(sbatch_command, shell=True)


# Process and submit jobs from the queue
def process_queue(user, image, wandb_api_key):
    while True:
        job_queue = load_queue()
        running_jobs = get_running_jobs()
        if running_jobs < 1990 and job_queue:
            job = job_queue.pop(0)
            total_jobs = job["total_jobs"]
            t = job["time"]
            sweep_id = job["sweep_id"]
            jobs_to_submit = min(1990 - running_jobs, total_jobs)

            submit_job(user, image, wandb_api_key, t, f"1-{jobs_to_submit}", sweep_id)

            if total_jobs > jobs_to_submit:
                job["total_jobs"] -= jobs_to_submit
                job_queue.insert(0, job)
            save_queue(job_queue)
        time.sleep(10)


if __name__ == "__main__":
    # Check SLURM availability
    result = subprocess.run("squeue -V", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SLURM is accessible. Version: {result.stdout.strip()}")
    else:
        print("SLURM access test failed.")
        print(f"Error: {result.stderr.strip()}")

    if len(sys.argv) != 4:
        print("Usage: python poller.py <user> <image> <wandb_api_key>")
        sys.exit(1)

    process_queue(sys.argv[1], sys.argv[2], sys.argv[3])
