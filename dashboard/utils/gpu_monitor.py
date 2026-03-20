import subprocess

def get_gpu_temperature():
    try:
        # We use subprocess.check_output because it closes the pipe automatically
        cmd = ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"]
        output = subprocess.check_output(cmd, encoding='utf-8').strip()
        return int(output)
    except Exception:
        return 0
