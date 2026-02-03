import platform
import sys
import os

def fetch_cores():
    cpu = os.cpu_count()
    print(cpu)
    pretty_cpu = f"{cpu}" + " Cores"
    print(pretty_cpu)
    return cpu


def fetch_ram():
    mem = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    print(mem)
    pretty_mem = mem / 1000000000
    pretty_mem = f"{pretty_mem}" + " GB"
    print(pretty_mem)
    return pretty_mem
    return mem

def fetch_storage():
    stat = os.statvfs('/')
    freespace = stat.f_bavail * stat.f_frsize
    print(freespace)

    pretty_freespace = freespace / 1000000000
    pretty_freespace = f"{pretty_freespace}" + " GB"
    print(pretty_freespace)
    return freespace


fetch_storage()
fetch_ram()
fetch_cores()