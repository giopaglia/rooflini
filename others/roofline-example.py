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
  #elif point["label"] == "HT + vec + prefetch":
  #  return "g"
  #elif point["label"] == "Cache Mode: HT + vec + prefetch":
  #  return "b"
  #elif point["label"] == "Cache Mode: HT + vec + prefetch, 512^3":
  #  return "k"
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

fig = plt.figure(figsize=(10, 40));
ax = plt.subplot(1,1,1)

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

ax.grid(color="#dddddd", zorder=-1)
ax.set_xlabel("Arithmetic Intensity (FLOP/Byte)", fontsize=15)
ax.set_ylabel("Performance (GFLOP/s)", fontsize=15)

##########################################################
################# Architecture Specific ##################

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

##########################################################

##########################################################
##################### Plot settings ######################

# Roofline window: Rect (x0, x1, y0, y1)
window_rect = [0.6, 60, 40, 4000]
#window_rect = [0.1, 10000, 0.1, 10000]
#window_rect = [1, 60, 10, 4000]
##########################################################


##########################################################
########################## Data ##########################

AI_v = {"taylor-green3D" : 2.29, "couette-flow" : 4.26}
datapoints = [
  # Hyper-Threading
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "AoS", 64,  192,  0], "GFLOPs" : 216.91}, # oppure 250.51
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "AoS", 128, 192,  0], "GFLOPs" : 237.53},
  {"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "AoS", 192, 192,  0], "GFLOPs" : 367.12},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "AoS", 256, 192,  0], "GFLOPs" : 276.65},
  {"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "SoA", 64,  192,  0], "GFLOPs" : 266.09},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "SoA", 128, 192,  0], "GFLOPs" : 177.39},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "SoA", 192, 192,  0], "GFLOPs" : 203.61},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "SoA", 256, 192,  0], "GFLOPs" : 139.79},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CSoA",  64,  192,  0], "GFLOPs" : 185.27},
  {"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CSoA",  128, 192,  0], "GFLOPs" : 299.47},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CSoA",  192, 192,  0], "GFLOPs" : 271.37},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CSoA",  256, 192,  0], "GFLOPs" : 182.17},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CAoSoA",  64,  192,  0], "GFLOPs" : 438.47},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CAoSoA",  128, 192,  0], "GFLOPs" : 445.19},
  {"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CAoSoA",  192, 192,  0], "GFLOPs" : 627.51},
  #{"type" : "taylor-green3D", "label" : "Flat Mode", "prop" : ["D3Q27", "CAoSoA",  256, 192,  0], "GFLOPs" : 385.39},
  
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "aos", 192,  64,  0], "GFLOPs" : 263.18},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "aos", 192,  192,  0], "GFLOPs" : 372.02},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "soa", 192,  64,  0], "GFLOPs" : 281.45},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "soa", 192,  192,  0], "GFLOPs" : 208.85},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "csoa", 192,  64,  0], "GFLOPs" : 177.66},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "csoa", 192,  192,  0], "GFLOPs" : 279.87},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "caosoa", 192,  64,  0], "GFLOPs" : 427.97},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "caosoa", 192,  192,  0], "GFLOPs" : 545.51},

  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "aos", 512, 64, 1], "GFLOPs" : 128.49},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "aos", 512, 128, 1], "GFLOPs" : 130.39},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "aos", 512, 256, 1], "GFLOPs" : 123.59},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "soa", 512, 64, 1], "GFLOPs" : 119.04},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "soa", 512, 128, 1], "GFLOPs" : 123.89},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "soa", 512, 256, 1], "GFLOPs" : 124.34},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "csoa", 512, 64, 1], "GFLOPs" : 108.63},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "csoa", 512, 128, 1], "GFLOPs" : 119.01},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "csoa", 512, 256, 1], "GFLOPs" : 122.69},
  {"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "caosoa", 512, 64, 1], "GFLOPs" : 128.43},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "caosoa", 512, 128, 1], "GFLOPs" : 127.20},
  #{"type" : "taylor-green3D", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "caosoa", 512, 256, 1], "GFLOPs" : 123.52},

  {"type" : "taylor-green3D", "label" : "Flat Mode + prefetch", "prop" : ["D3Q27", "CAoSoA",  192, -1,  0], "GFLOPs" : 650.5},
  
  # Couette Flow
  
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "aos", 64, 192,  0], "GFLOPs" : 448.77},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "aos", 128, 192,  0], "GFLOPs" : 445.39},
  {"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "aos", 192, 192,  0], "GFLOPs" : 680.77},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "aos", 256, 192,  0], "GFLOPs" : 603.21},
  {"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "soa", 64, 192,  0], "GFLOPs" : 508.32},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "soa", 128, 192,  0], "GFLOPs" : 376.28},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "soa", 192, 192,  0], "GFLOPs" : 379.79},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "soa", 256, 192,  0], "GFLOPs" : 266.37},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "csoa", 64,  192,  0], "GFLOPs" : 539.26},
  {"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "csoa", 128,  192,  0], "GFLOPs" : 559.66},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "csoa", 192,  192,  0], "GFLOPs" : 497.83},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "csoa", 256,  192,  0], "GFLOPs" : 300.76},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "caosoa", 64,  192,  0], "GFLOPs" : 847.87},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "caosoa", 128,  192,  0], "GFLOPs" : 922.98},
  {"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "caosoa", 192,  192,  0], "GFLOPs" : 1145.41},
  #{"type" : "couette-flow", "label" : "Flat Mode", "prop" : ["D3Q27", "caosoa", 256,  192,  0], "GFLOPs" : 795.07},

  #{"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "aos", 192,  64,  0], "GFLOPs" : 466.78},
  {"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "aos", 192,  192,  0], "GFLOPs" : 672.69},
  {"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "soa", 192,  64,  0], "GFLOPs" : 501.47},
  #{"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "soa", 192,  192,  0], "GFLOPs" : 378.47},
  {"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "csoa", 192,  64,  0], "GFLOPs" : 536.60},
  #{"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "csoa", 192,  192,  0], "GFLOPs" : 492.56},
  #{"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "caosoa", 192,  64,  0], "GFLOPs" : 831.09},
  {"type" : "couette-flow", "label" : "Cache Mode: 1.4GB lattice", "prop" : ["D3Q27", "caosoa", 192,  192,  0], "GFLOPs" : 1113.10},

  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "aos", 512, 64, 1], "GFLOPs" : 235.94},
  {"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "aos", 512, 128, 1], "GFLOPs" : 242.78},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "aos", 512, 256, 1], "GFLOPs" : 230.92},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "soa", 512, 64, 1], "GFLOPs" : 220.35},
  {"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "soa", 512, 128, 1], "GFLOPs" : 232.69},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "soa", 512, 256, 1], "GFLOPs" : 230.16},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "csoa", 512, 64, 1], "GFLOPs" : 220.72},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "csoa", 512, 128, 1], "GFLOPs" : 220.88},
  {"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "csoa", 512, 256, 1], "GFLOPs" : 224.35},
  {"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "caosoa", 512, 64, 1], "GFLOPs" : 240.40},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "caosoa", 512, 128, 1], "GFLOPs" : 233.98},
  #{"type" : "couette-flow", "label" : "Cache Mode: 27GB lattice", "prop" : ["D3Q27", "caosoa", 512, 256, 1], "GFLOPs" : 229.57}
  
  {"type" : "couette-flow", "label" : "Flat Mode + prefetch", "prop" : ["D3Q27", "caosoa", 192,  64,  0], "GFLOPs" : 1151.03},
  
]

##########################################################

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

ax.set_xlim(window_rect[0], window_rect[1])
ax.set_ylim(window_rect[2], window_rect[3])

ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))

handles,labels = ax.get_legend_handles_labels()
handles = [handles[0], handles[2], handles[3], handles[4]]
labels = [labels[0], labels[2], labels[3], labels[4]]
#plt.figlegend(handles=handles,  labels=labels, loc="lower center", bbox_to_anchor=(0.25, 0.18))
plt.figlegend(handles=handles,  labels=labels, loc="upper center", bbox_to_anchor=(0.7, 0.97), ncol=4, fontsize=10)

handles,labels = ax.get_legend_handles_labels()
handles = [handles[1], handles[7], handles[5], handles[6]]
labels = [labels[1], labels[7], labels[5], labels[6]]
#plt.figlegend(handles=handles,  labels=labels, loc="lower center", bbox_to_anchor=(0.5, 0.2), ncol=4)
plt.figlegend(handles=handles,  labels=labels, loc="lower right", bbox_to_anchor=(0.96, 0.38), fontsize=11)

plt.tight_layout()
plt.show()

pp = PdfPages("d3q27-roofline.pdf")
pp.savefig(fig)
pp.close()