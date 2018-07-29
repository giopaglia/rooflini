from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker

import numpy as np
import sys
import pylab
import re
import json
import math

# Filename
filename = "roofline.pdf"
if(sys.argc==1):
  filename = sys.argv[1]

# Figure
fig = plt.figure(figsize=(10, 40));
ax = plt.subplot(1,1,1)
ax.grid(color="#dddddd", zorder=-1)
ax.set_xlabel("Arithmetic Intensity (FLOP/Byte)", fontsize=15)
ax.set_ylabel("Performance (GFLOP/s)", fontsize=15)

# Architecture-specific roofs
cpu_roofs = [
  {"name" : "Scalar Add Peak",    "val" : 98.48},
  {"name" : "DP Vector Add Peak", "val" : 843.06},
  {"name" : "DP Vector FMA Peak", "val" : 1691.96}
]
mem_bottlenecks = [
  {"name" : "L1 Bandwidth",     "val" : 7398.95},
  {"name" : "L2 Bandwidth",     "val" : 1237.34},
  {"name" : "MCDRAM Bandwidth", "val" : 393.75},
  {"name" : "DDR Bandwidth",    "val" : 81.35}
]

## Plot settings

# Window rectangle (axis limits)
xmin, xmax, ymin, ymax = 0.6, 60, 40, 4000


##########################################################
########################## Data ##########################

AI_v = {"taylor-green3D" : 2.29, "couette-flow" : 4.26}
datapoints = [
  {"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CAoSoA",  192, 192,  0], "GFLOPs" : 627.51},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "caosoa", 192,  192,  0], "GFLOPs" : 545.51},
  {"type" : "couette-flow", "label" : "Flat Mode + prefetch", "prop" : ["D3Q27", "caosoa", 192,  64,  0], "GFLOPs" : 1151.03},
  
]

##############################################
def get_color(point):
  if point["label"] == "Flat Mode":
    return "C0"
  elif point["label"] == "Flat Mode + prefetch":
    return "C1"
  elif point["label"] == "Cache Mode: 1.4GB lattice":
    return "C2"
  elif point["label"] == "Cache Mode: 27GB lattice":
    return "C3"
  else:
    print "need new color for \"" +  point["label"] + "\""
    sys.exit()

def get_marker(point):
  if point["prop"][1].lower() == "aos":
    return "X"
  elif point["prop"][1].lower() == "soa":
    return "o"
  elif point["prop"][1].lower() == "csoa":
    return "D"
  elif point["prop"][1].lower() == "caosoa":
    return "*"
  else:
    print "need new marker for \"" +  point["prop"][1] + "\""
    sys.exit()

def get_markersize(point):
  base=30
  if point["prop"][1].lower() == "aos":
    return base*1.2
  elif point["prop"][1].lower() == "soa":
    return base*1.2
  elif point["prop"][1].lower() == "csoa":
    return base*1
  elif point["prop"][1].lower() == "caosoa":
    return base*2
  else:
    print "need new markersize for \"" +  point["prop"][1] + "\""
    sys.exit()

def str_benchmark(benchmark):
  if benchmark == "taylor-green3D" or benchmark == "taylor-green2D":
    return "Taylor Green"
  elif benchmark == "couette-flow":
    return "Couette Flow"
##############################################

def set_size(w,h, ax=None):
  """ w, h: width, height in inches """
  if not ax: ax=plt.gca()
  l = ax.figure.subplotpars.left
  r = ax.figure.subplotpars.right
  t = ax.figure.subplotpars.top
  b = ax.figure.subplotpars.bottom
  figw = float(w)/(r-l)
  figh = float(h)/(t-b)
  ax.figure.set_size_inches(figw, figh)


##########################################################

window_rect = [xmin, xmax, ymin, ymax]

max_roof = cpu_roofs[0]["val"]
max_slip = mem_bottlenecks[0]["val"]

for roof in cpu_roofs:
  if roof["val"] > max_roof:
    max_roof = roof["val"]

for slip in mem_bottlenecks:
  print slip

  y = [0, max_roof]
  x = [yy/slip["val"] for yy in y]
  ax.loglog(x, y, linewidth=1.0,
    linestyle='-.',
    marker="2",
    color="grey",
    zorder=10)

# ...
#  pos = np.array((window_rect[0]*1.1, window_rect[0]*slip["val"]*1.35))
#  trans_angle = plt.gca().transData.transform_angles(np.array((45,)), pos.reshape((1, 2)))[0]
#  print trans_angle
#  trans_angle = 45 # *3/5

  ax.annotate(slip["name"] + ": " + str(slip["val"]) + " GB/s", (window_rect[0]*1.1, window_rect[0]*slip["val"]*1.35),
    rotation="23.3",
    #rotation=trans_angle, rotation_mode='anchor',
    fontsize=11,
    ha="left", va='bottom',
    color="grey")
    
  if slip["val"] > max_slip:
    max_slip = slip["val"]

for roof in cpu_roofs:
  print roof

  x = [roof["val"]/max_slip, window_rect[1]*10]
  ax.loglog(x, [roof["val"] for xx in x], linewidth=1.0,
    linestyle='-.',
    marker="2",
    color="grey",
    zorder=10)

  ax.text(
    #roof["val"]/max_slip*10,roof["val"]*1.1,
    window_rect[1]/1.1, roof["val"]*1.1,
    roof["name"] + ": " + str(roof["val"]) + " GFLOPs",
    ha="right",
    fontsize=11,
    color="grey")

#plt.xticks(list(plt.xticks()[0]) + [AI for n,AI in AI_v.items()], list(plt.xticks()[0]) + [str(AI) for n,AI in AI_v.items()])
for benchmark in AI_v:
  AI = AI_v[benchmark]
  print benchmark
  print AI

  plt.axvline(x=AI, dashes=[10, 10, 3, 10], linewidth=0.4, color="#aaaaaa")

  ax.text(
    AI/1.15, window_rect[2]*1.24,
    str_benchmark(benchmark),
    fontsize=12,
    rotation="90",
    va="bottom",
    color="k")

i = 0
for point in datapoints:
  AI = AI_v[point["type"]]

  ax.scatter(AI, point["GFLOPs"], marker=get_marker(point), s=get_markersize(point), color=get_color(point),
    zorder=100)

  if i < 4:
    ax.plot([], [], linestyle="", marker=get_marker(point), ms=get_markersize(point)/6, color="black", label=point["prop"][1])
  if i % 4 == 0:
    ax.plot([], [], linestyle="", marker="s", color=get_color(point), label=point["label"])

  i += 1
set_size(6,3)

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# axis labels format
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))

handles,labels = ax.get_legend_handles_labels()
handles = [handles[0], handles[2], handles[3], handles[4]]
labels = [labels[0], labels[2], labels[3], labels[4]]
#plt.figlegend(handles=handles,  labels=labels, loc="lower center", bbox_to_anchor=(0.25, 0.18))
plt.figlegend(handles=handles,  labels=labels, loc="upper center", bbox_to_anchor=(0.7, 0.97), ncol=4, fontsize=10)

plt.tight_layout()
plt.show()

pp = PdfPages(filename)
pp.savefig(fig)
pp.close()