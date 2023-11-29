#!/usr/bin/env python3

# wattmon.py
# ==========
#
# This is a little Python script to monitor/log the power usage of
# an NVIDIA GPU with NVML capabilities [1].
#
# Periodically print a timestamp (nanoseconds since epoch) and the current
# power usage in milliwatts to stdout.
# Adjust `DELTA_T` to control sampling time.
#
# Example usage:
#   wattmon.py ./a.out arg1 arg2
#
# ---
# [1] https://developer.nvidia.com/nvidia-management-library-nvml

import sys
import asyncio
import time

from pynvml import *


# sampling time
DELTA_T = 1 / 100


async def log_power_consumption(flag, handle):
    # block until flag is set
    await flag.wait()

    # sample power usage while `flag` is `True`
    while flag.is_set():
        # query power usage at the current time step
        current_usage = nvmlDeviceGetPowerUsage(handle)
        # TODO capture clock speed too
        print(time.time_ns(), current_usage)
        await asyncio.sleep(DELTA_T)


async def main():
    # initialize the NVML context
    nvmlInit()

    # stop execution if there are no available devices
    if nvmlDeviceGetCount() < 1:
        print("No CUDA devices attached!", file=sys.stderr)
        sys.exit(1)

    # TODO get device index from command line args
    handle = nvmlDeviceGetHandleByIndex(0)

    # join command line args to one command with arguments
    cmd = " ".join(sys.argv[1:])

    # create flag for communication with async task
    flag = asyncio.Event()

    # create the async task for logging to stdout
    logging_task = asyncio.create_task(log_power_consumption(flag, handle))

    # start async task operation by setting the flag
    flag.set()

    # add some time padding to better estimate power usage during idle
    await asyncio.sleep(1)

    # launch subprocess and wait for it to finish
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    # show errors if there were any
    if not proc.returncode:
        print(stderr, file=sys.stderr)

    # add some more padding
    await asyncio.sleep(3)

    # halt async task by resetting flag
    flag.clear()

    # cancel the async task
    logging_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())

