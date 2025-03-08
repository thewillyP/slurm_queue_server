import subprocess
import json
import os
import time
from flask import Flask, request, jsonify
from threading import Thread
import fcntl  # File locking

# Global variables
queue_file = "/scratch/queue_server/job_queue.json"


# Load the queue from file with locking
def load_queue():
    job_queue = []
    try:
        with open(queue_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)  # Lock the file for reading
            job_queue = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)  # Release the read lock
    except FileNotFoundError:
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
def submit_job(user, t, array, sweep_id):
    sbatch_command = f"cd /myqueue && /opt/slurm/bin/sbatch --export=USER={user},IMAGE={os.getenv('IMAGE')},WANDB_SWEEP_ID={sweep_id},WANDB_API_KEY={os.getenv('WANDB_API_KEY')} --time={t} --array={array} run.slurm"
    subprocess.run(sbatch_command, shell=True)


# Process and submit jobs from the queue
def process_queue():
    while True:
        job_queue = load_queue()  # Always load from the file
        running_jobs = get_running_jobs()
        if running_jobs < 1990 and job_queue:
            job = job_queue.pop(0)  # Get the next job from the queue
            total_jobs = job["total_jobs"]
            t = job["time"]
            sweep_id = job["sweep_id"]
            jobs_to_submit = min(2000 - running_jobs, total_jobs)

            # Submit jobs in batches (up to the remaining slots available)
            submit_job(job["user"], t, f"1-{jobs_to_submit}", sweep_id)

            # If there are remaining jobs to submit, requeue them at the front
            if total_jobs > jobs_to_submit:
                job["total_jobs"] -= jobs_to_submit
                job_queue.insert(0, job)  # Append to the front
            # If the job is fully submitted, don't requeue it
            save_queue(job_queue)  # Persist the queue after modifying

        time.sleep(300)  # Sleep for 5 minutes


# Flask API to submit jobs
app = Flask(__name__)


@app.route("/submit_job", methods=["POST"])
def submit_job_api():
    data = request.get_json()
    if "total_jobs" not in data or "time" not in data or "sweep_id" not in data:
        return jsonify({"error": "Missing parameters"}), 400

    user = os.getenv("USER", "wlp9800")  # Default to 'wlp9800' or user environment variable
    total_jobs = data["total_jobs"]
    t = data["time"]
    sweep_id = data["sweep_id"]

    job = {"total_jobs": total_jobs, "time": t, "sweep_id": sweep_id, "user": user}

    job_queue = load_queue()  # Read the queue from the file
    job_queue.append(job)  # Add the new job to the queue
    save_queue(job_queue)  # Write the updated queue back to the file

    return jsonify({"message": "Job added to the queue"}), 200


# Start the background thread for processing the queue
def start_processing_thread():
    thread = Thread(target=process_queue)
    thread.daemon = True  # Ensure it exits when the main program exits
    thread.start()


if __name__ == "__main__":
    result = subprocess.run("squeue -V", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SLURM is accessible. Version: {result.stdout.strip()}")
    else:
        print("SLURM access test failed. Check your SLURM installation or permissions.")

    start_processing_thread()  # Start processing the job queue in the background
    app.run(host="0.0.0.0", port=5000)  # Run the Flask app
