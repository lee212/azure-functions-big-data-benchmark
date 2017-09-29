import os 
import sys, os.path 
import json 
import time 
import tarfile
import hashlib

lcnt = 3
msize = 1024

iparam = "req"
oparam = "res"

#cur_path = os.path.dirname( __file__ )
work_path = "/local/Temp/"
numpy_download_url = 'https://venv.blob.core.windows.net/python27/numpy.tar.gz'
numpy_hash = '35eff563a232fd2b7e93137f549ec2c9'
numpy_venv = work_path + "venv/numpy/Lib/site-packages"
psutil_download_url = 'https://venv.blob.core.windows.net/python27/psutil.tar.gz'
psutil_hash = 'c78295993b38e2a78930d9d074e74b6a'
psutil_venv = work_path + "venv/psutil/Lib/site-packages"

t0 = time.time()
try:
    # 3.5+
    import urllib.request
    _urlretrieve = urllib.request.urlretrieve
except ImportError:
    # "2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)]"
    import urllib
    _urlretrieve = urllib.urlretrieve

# Initial download if venv is not available to load
def download_venv(venv_path, url, fhash):
    if not os.path.isdir(venv_path):
        filepath = work_path + os.path.basename(url)
        if not os.path.isfile(filepath):
            _urlretrieve(url, filepath)
        hstr = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
        if hstr != fhash:
            print 'md5sum is incorrect'
        c = tarfile.open(filepath)
        c.extractall(work_path)
        c.close()
        os.remove(filepath)

download_venv(numpy_venv, numpy_download_url, numpy_hash)
sys.path.append(numpy_venv)
import numpy as np 

download_venv(psutil_venv, psutil_download_url, psutil_hash)
sys.path.append(psutil_venv)
import psutil

t_import = time.time()

process = psutil.Process(os.getpid())

# Copied from https://github.com/pywren/examples/blob/master/benchmark_flops/compute.py
# Written by Eric Jonas @ ericjonas.com
def compute_flops(loopcount, MAT_N, precision):
    
    A = np.arange(MAT_N**2, dtype=precision).reshape(MAT_N, MAT_N)
    B = np.arange(MAT_N**2, dtype=precision).reshape(MAT_N, MAT_N)
    t1 = time.time()
    for i in range(loopcount):
        c = np.sum(np.dot(A, B))
    FLOPS = 2 * MAT_N**3 * loopcount
    t2 = time.time()
    mi=process.memory_info()
    return (FLOPS / (t2-t1), mi)

try:
    postreqdata = json.loads(open(os.environ[iparam]).read()) 
except ValueError as e:
    postreqdata = {}
    
if 'number_of_loop' in postreqdata:
    lcnt = postreqdata['number_of_loop'] 

if 'number_of_matrix' in postreqdata:
    msize = postreqdata['number_of_matrix'] 

# Default: double precision
precision = np.float64

if 'single_or_double' in postreqdata:a
    if int(postreqdata['single_or_double']) == 32:
        precision = np.float32

res, mi = compute_flops(lcnt, msize, precision) 
response = open(os.environ[oparam], 'w')

# Descriptions from psutil

# rss: aka 'Resident Set Size', this is the non-swapped physical memory a
# process has used. On UNIX it matches 'top's RES column (see doc). On Windows
# this is an alias for wset field and it matches 'Mem Usage' column of
# taskmgr.exe.
# vms: aka 'Virtual Memory Size', this is the total amount of virtual memory used
# by the process. On UNIX it matches top's VIRT column (see doc). On Windows
# this is an alias for pagefile field and it matches 'Mem Usage' 'VM Size' column
# of taskmgr.exe.

# Note that based on a few tests, vms is close to real usage on Windows, rss is
# close to real use on Linux

t_end = time.time()

response.write("{0}, {1}, {2}, {3}, {4}".format(res/1e9, mi.vms/1024.0**2,
        mi.rss/1024.0**2, t_import - t0, t_end-t0))
response.close() 
