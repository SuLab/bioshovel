import subprocess
import sys
from pathlib import Path

def submit_pbs_job(job_file_path, queue='new'):

    ''' Submits a PBS job file at job_file_path to queue

        Returns new PBS job ID if successful or None if unsuccessful
    '''

    path = Path(job_file_path)
    try:
        out = subprocess.check_output(['qsub', '-q',
                                       queue,
                                       path.name],
                                       cwd=str(path.parent))
        return out.decode('utf-8').rstrip('\n').split('.')[0]
    except subprocess.CalledProcessError as err:
        string_error = err.output.decode(encoding='UTF-8').rstrip('\n')
        print(string_error, file=sys.stderr)
        return None