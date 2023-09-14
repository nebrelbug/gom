import datetime
import pynvml
from tabulate import tabulate
import click

import importlib.util
docker_spec = importlib.util.find_spec("docker")
is_docker_available = docker_spec is not None

if is_docker_available:
    import docker

# Initialize the NVIDIA Management Library (NVML)
pynvml.nvmlInit()

# Get the number of available GPUs
num_gpus = pynvml.nvmlDeviceGetCount()

def get_gpu_info():
    gpus = []

    # Iterate through each GPU and query process information
    for gpu_index in range(num_gpus):
        gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)

        memory = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
        processes = pynvml.nvmlDeviceGetComputeRunningProcesses(gpu_handle)

        nice_processes = []

        for process in processes:
            nice_processes.append({
                "pid": process.pid,
                "used_memory": process.usedGpuMemory
            })

        gpus.append({
            "index": gpu_index,
            "total_memory": memory.total,
            "used_memory": memory.used,
            "used_memory_nocontainer": memory.used,
            "processes": nice_processes
        })
        

    return gpus

def get_docker_details():
    client = docker.from_env()
    containers = client.containers.list()
    docker_details = []

    for container in containers:
        procs = container.top(ps_args="-o pid")["Processes"]  # get all PIDs
        procs = [int(item) for sublist in procs for item in sublist]  # flatten

        docker_details.append({
            "name": container.name,
            "id": container.id,
            "procs": procs,
            "total": 0, # fill in later
            "gpus": {} # fill in later: dict<gpu_index, memory>
        })

    return docker_details

class bcolors:
    GREEN = "\033[32m"
    ORANGE = "\033[33m"
    RED = "\033[31m"
    ENDC = "\033[0m"

def colorize(num):
    res = "{0:.0%}".format(num)
    if num == 0:
        return res
    elif num < 0.25:
        return bcolors.GREEN + res + bcolors.ENDC
    elif num < 0.5:
        return bcolors.ORANGE + res + bcolors.ENDC
    else:
        return bcolors.RED + res + bcolors.ENDC

def truncate_string(string, length):
    if len(string) <= length:
        return string
    else:
        truncated = string[: length - 3] + "..."
        return truncated
    
def show_table(watch = False):
    gpus = get_gpu_info()

    max_gpu_index_len = len(
        str(max([gpu["index"] for gpu in gpus])))


    table = [
        [
            str(gpu["index"])
            + " " * (max_gpu_index_len - len(str(gpu["index"])))
            + " - "
            + colorize(float(gpu["used_memory"]) / float(gpu["total_memory"]))
        ]
        for gpu in gpus
    ]

    headers = ["GPUs"]

    if is_docker_available:

        table += [["TOTAL"]]

        containers = get_docker_details()

        for gpu in gpus:
            for proc in gpu["processes"]:
                for container in containers:
                    if proc["pid"] in container["procs"]:
                        if gpu["index"] not in container["gpus"]:
                            container["gpus"][gpu["index"]] = 0
                        container["gpus"][gpu["index"]] += proc["used_memory"]
                        container["total"] += proc["used_memory"]
                        gpu["used_memory_nocontainer"] -= proc["used_memory"]

        containers = [container for container in containers if len(container["gpus"]) > 0]
        containers.sort(key=lambda x: x["total"], reverse=True)

        for container in containers:
            headers.append(truncate_string(container["name"], 15))

            for gpu in gpus:
                gpu_index = gpu["index"]
                gpu_usage = float(container["gpus"].get(gpu_index, 0)) / float(gpu["total_memory"])

                table[gpu_index].append(colorize(gpu_usage))

            table[-1].append(str(int(container["total"] / 1024 / 1024)) + " MiB")
        
        headers.append("OTHER")

        for gpu in gpus:
            non_docker_gpu_usage = float(gpu["used_memory_nocontainer"]) / float(gpu["total_memory"])
            table[gpu["index"]].append(colorize(non_docker_gpu_usage))

        table[-1].append(str(int(sum([gpu["used_memory_nocontainer"] for gpu in gpus]) / 1024 / 1024)) + " MiB")

    if watch:
        click.clear()

    print(
        tabulate(
            table,
            headers,
            tablefmt="mixed_outline",
            stralign="center",
            colalign=("left",),
        )
    )

    if watch:
        print("Last updated: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Shutdown NVML to release resources
pynvml.nvmlShutdown()
