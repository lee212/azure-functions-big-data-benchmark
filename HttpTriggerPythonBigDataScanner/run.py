import os
import json
import time
import tarfile
import hashlib
venv_start = time.time()
import sys, os.path

# "2.7.8 (default, Jun 30 2014, 16:03:49) [MSC v.1500 32 bit (Intel)]"
import urllib
_urlretrieve = urllib.urlretrieve

postreqdata = json.loads(open(os.environ['req']).read())
accountname=postreqdata['accountname']
accountkey=postreqdata['accountkey']
container_name = postreqdata["bucket"]
blob_name = postreqdata["fname"]

work_path = "/local/Temp/"
asb_download_url = postreqdata['virtualenv_download_url']
asb_download_name = postreqdata['virtualenv_download_name']
asb_venv = work_path + "/Lib/site-packages".format(asb_download_name)

# Initial download if venv is not available to load
def download_venv(venv_path, url, fhash=None):
    if not os.path.isdir(venv_path):
        filepath = work_path + os.path.basename(url)
        if not os.path.isfile(filepath):
            _urlretrieve(url, filepath)
        if fhash:
            hstr = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
            if hstr != fhash:
                print 'md5sum is incorrect'
        c = tarfile.open(filepath)
        c.extractall(work_path)
        c.close()
        os.remove(filepath)

download_venv(asb_venv, asb_download_url)
sys.path.append(asb_venv)
from azure.storage.blob import BlockBlobService
venv_end = time.time()

s3d_start = time.time()
block_blob_service = BlockBlobService(account_name=accountname, account_key=accountkey) 
blob = block_blob_service.get_blob_to_bytes(container_name, blob_name)
lines = blob.content.split(b"\n")
x = postreqdata['x']
res = []
s3d_end = time.time()

t_start = time.time()
for line in lines:
    try:
        pageURL, pageRank, avgDuration = line.split(",")
    except:
        continue
    # SELECT pageURL, pageRank FROM rankings WHERE

    # pageRank > X
    if int(pageRank) > int(x):
        res.append([pageURL, pageRank])

t_end = time.time()

r_num = len(res)
elapsed = t_end - t_start

response = open(os.environ['res'], 'w')
result = {"result":{"cnt": r_num, "elapsed":elapsed, "s3_elapsed": s3d_end - s3d_start, "venv_elapsed": venv_end - venv_start},
            "params": postreqdata }

#msg = ("{0}, {1}".format(r_num, elapsed))
print (result)
response.write(json.dumps(result))
response.close()
