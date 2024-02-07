import subprocess

if __name__ == "__main__":
    # Get the job IDs of your active jobs
    # try:
    job_ids = subprocess.check_output(["squeue", "-h", "-u", "an.kandala", "-o", "%A"], universal_newlines=True).split()
    print(job_ids)
    # except subprocess.CalledProcessError:
    #     job_ids = []

    # Cancel each job
    for job_id in job_ids:
        output = subprocess.run(["scancel", job_id])
        print(f"Job {job_id} cancelled")
