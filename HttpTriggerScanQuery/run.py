import os
import json
import sys
import time
import urllib

"""
POST Example:

{
    "x": 9,
    "key": "part-00000",
    "output": "job1"
}
or
{
    "x": 9,
    "url":
    "https://bigdata0benchmark.blob.core.windows.net/pavlo/text/5nodes/rankings/part-00000",
    "output": "job1"
}
"""

t_start = time.time()

venv_psutil = "/local/Temp/venv/psutil/Lib/site-packages"
sys.path.append(venv_psutil)
import psutil

res = []

postreqdata = json.loads(open(os.environ['req']).read())
if "url" in postreqdata:
    url = postreqdata['url']
x = postreqdata['x']

t_start1 = time.time()
with open(os.environ['inputblob']) as f:
    contents = f.read()

"""
filename = os.path.basename(url)
if not os.path.isfile(os.path.basename(url)):   
    urllib.urlretrieve(url, filename)
t_start2 = time.time()
t_download = t_start2 - t_start1

with open(filename) as f:
        lines = f.readlines()
"""
lines = contents.split("\n")

t_start3 = time.time()
for line in lines:
    try:
        pageURL, pageRank, avgDuration = line.split(",")
    except ValueError:
        continue
    # SELECT pageURL, pageRank FROM rankings WHERE pageRank > X
    if int(pageRank) > int(x):
        res.append([pageURL, pageRank])

t_end = time.time()

r_num = len(res)
elapsed = t_end - t_start3

#os.remove(filename)
t_end2 = time.time()
nbytes = 0
with open(os.environ['outputBlob'], 'w') as outfile:
    for i in res:
        line = "{0}, {1}\n".format(i[0],i[1])
        outfile.write(line)
        nbytes+= len(line)
t_end3 = time.time()

t_write = t_end3 - t_end2

process = psutil.Process(os.getpid())
mi=process.memory_info()

# Note
# process.create_time()
# ,
# process.memory_full_info().uss
# or
# psutil.virtual_memory()
# useful to investigate system memory usage with process
# Ref: https://pythonhosted.org/psutil/

t_end4 = time.time()
elapsed_all = t_end4 - t_start

response = open(os.environ['res'], 'w')
response.write("{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(elapsed, elapsed_all,
    mi.vms/1024.0**2, mi.rss/1024.0**2, t_write, r_num, nbytes))
response.close()
