import os 
import sys, os.path 
import json 
import time 
import tarfile

lcnt = 10
msize = 2048

iparam = "req"
oparam = "res"

numpy_download = 'https://pywren9cc1.blob.core.windows.net/numpy/numpy.tar.gz'
numpy_venv = "myvenv/Lib/site-packages"

venv_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
    numpy_venv))

try:
    # 3.5+
    import urllib.request
    _urlretrieve = urllib.request.urlretrieve
except ImportError:
    # "2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)]"
    import urllib
    _urlretrieve = urllib.urlretrieve

# Initial download if venv is not available to load
if not os.path.isdir(venv_path):
    url = numpy_download
    filename = os.path.basename(url)
    _urlretrieve(url, filename)
    fabspath = os.path.join(os.path.dirname( __file__ ), filename)
    c = tarfile.open(fabspath)
    c.extractall()
    
sys.path.append(venv_path)
import numpy as np 

def compute_flops(loopcount, MAT_N):
    
    A = np.arange(MAT_N**2, dtype=np.float64).reshape(MAT_N, MAT_N)
    B = np.arange(MAT_N**2, dtype=np.float64).reshape(MAT_N, MAT_N)
    t1 = time.time()
    for i in range(loopcount):
        c = np.sum(np.dot(A, B))
    FLOPS = 2 * MAT_N**3 * loopcount
    t2 = time.time()
    return FLOPS / (t2-t1)

try:
    postreqdata = json.loads(open(os.environ[iparam]).read()) 
except ValueError as e:
    postreqdata = {}
    
if 'number_of_loop' in postreqdata:
    lcnt = postreqdata['number_of_loop'] 

if 'number_of_matrix' in postreqdata:
    msize = postreqdata['number_of_matrix'] 

res = compute_flops(lcnt, msize) 
response = open(os.environ[oparam], 'w')
response.write(str(res/1e9)) 
response.close() 
