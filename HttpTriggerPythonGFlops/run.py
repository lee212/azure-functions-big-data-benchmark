import os 
import sys, os.path 
import json 
import time 
import tarfile
import hashlib

lcnt = 10
msize = 2048

iparam = "req"
oparam = "res"

cur_path = os.path.dirname( __file__ )
numpy_download = 'https://venv.blob.core.windows.net/python27/numpy.tar.gz'
numpy_hash = '35eff563a232fd2b7e93137f549ec2c9'
numpy_venv = "venv/myvenv/Lib/site-packages"
venv_numpy = os.path.abspath(os.path.join(cur_path, numpy_venv))
psutil_download = 'https://venv.blob.core.windows.net/python27/psutil.tar.gz'
psutil_hash = 'c78295993b38e2a78930d9d074e74b6a'
psutil_venv = "venv/psutil/Lib/site-packages"
venv_psutil = os.path.abspath(os.path.join(cur_path, psutil_venv))

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
        filename = os.path.basename(url)
        if not os.path.isfile(filename):
            _urlretrieve(url, filename)
        hstr = hashlib.md5(open(filename, 'rb').read()).hexdigest()
        if hstr != fhash:
            print 'md5sum is incorrect'
        fabspath = os.path.join(cur_path, filename)
        c = tarfile.open(fabspath)
        c.extractall()
        os.remove(fabspath)

download_venv(venv_numpy, numpy_download, numpy_hash)
sys.path.append(venv_numpy)
import numpy as np 

download_venv(venv_psutil, psutil_download, psutil_hash)
sys.path.append(venv_psutil)
import psutil

process = psutil.Process(os.getpid())

# Copied from https://github.com/pywren/examples/blob/master/benchmark_flops/compute.py
# Written by Eric Jonas @ ericjonas.com
def compute_flops(loopcount, MAT_N):
    
    A = np.arange(MAT_N**2, dtype=np.float64).reshape(MAT_N, MAT_N)
    B = np.arange(MAT_N**2, dtype=np.float64).reshape(MAT_N, MAT_N)
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

res, mi = compute_flops(lcnt, msize) 
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

response.write(str(res/1e9) + "," + str(mi.vms/1024.0**2)+ "," +
        str(mi.rss/1024.0**2))
response.close() 
