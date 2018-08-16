#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2018 David Tellenbach <david.tellenbach@tellnotes.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# For parsing cli arguments
import argparse

# For parsing JSON files
import json

# Plotting library
import matplotlib as plt
plt.use('Agg')
import matplotlib.pyplot as pyplot

# To access more matplotlib functionality, i.e., default calculated figure
# size
from pylab import rcParams

_version = 0.2

def getVersion(parser):
  '''Print program name, description and current version'''
  return "{} - {} - Version {}".format(parser.prog, parser.description, _version)

class PlottingConfiguration:
  '''Configuration of the benchmark plot'''

  def __init__(self, args):
    self.inputFile = args.inputFile
    self.outputFile = args.outputFile
    self.plotTitle = args.plotTitle
    self.timeUnit = args.timeUnit
    self.xValue = args.xValue
    self.yValue = args.yValue

    if args.xLabel is None:
        self.xLabel = args.xValue
    else:
      self.xLabel = args.xLabel

    if args.yLabel is None:
        self.yLabel = "Time in {}".format(args.timeUnit)
    else:
      self.yLabel = args.yLabel
    
    self.xTickBegin = args.xTickBegin
    self.xTickEnd = args.xTickEnd
    self.xTickStep = args.xTickStep
    self.benchmarkDescription = args.benchmarkDescription
    self.xSize = args.xSize
    self.ySize = args.ySize
    self.dpi = args.dpi

def convertTimeUnit(value, src, dest):
  '''Convert time units'''

  # This function is necessary since popular libraries like datatime cannot
  # handle nanoseconds

  if src == dest:
    return value
  if src == "ns":
    if dest == "us":
      return value / 1000
    if dest == "ms":
      return value / 1000000
  elif src == "us":
    if dest == "ns":
      return value * 1000
    if dest == "ms":
      return value / 1000
  elif src == "ms":
    if dest == "ns":
      return value * 1000000
    if dest == "us":
      return value * 10000

def parseJSON(configuration):
  '''Parses JSON file containing benchmark results'''

  with open(configuration.inputFile) as fd:
    data = json.load(fd)

  ret = []
  for bench in data["benchmarks"]:
    # Convert time units if necessary
    if bench["time_unit"] != configuration.timeUnit:
      bench[configuration.yValue] = convertTimeUnit(bench[configuration.yValue],
                                      bench["time_unit"],
                                      configuration.timeUnit)
    ret.append((bench["benchmark_visualizer_group"], bench[configuration.xValue],
          bench[configuration.yValue], configuration.timeUnit))

  return ret


def plot(data, configuration):

  benchmarkDict = dict()

  for bench in data:
    # If no list for this benchmark (group) exist, we create one
    if bench[0] not in benchmarkDict:
      benchmarkDict.update({bench[0]: ([], [])})

    # Append x value if necessary
    if bench[1] not in benchmarkDict[bench[0]][0]:
      benchmarkDict[bench[0]][0].append(bench[1])

    # Append y value
    benchmarkDict[bench[0]][1].append(bench[2])
  
  # Use passed arguments if possible, otherwise use automatically calculated
  # figure size
  if configuration.xSize is None and configuration.xSize is None:
    pyplot.figure(dpi=configuration.dpi)
  elif configuration.xSize is None:
    pyplot.figure(figsize=(rcParams['figure.figsize'][0],
                           float(configuration.ySize)),
                  dpi=configuration.dpi)
  elif configuration.ySize is None:
    pyplot.figure(figsize=(float(configuration.xSize),
                           rcParams['figure.figsize'][1]),
                  dpi=configuration.dpi)
  else:
    pyplot.figure(figsize=(float(configuration.xSize), 
                           float(configuration.ySize)),
                  dpi=configuration.dpi)

  for key, value in benchmarkDict.items():
    # Add plotting data
    pyplot.plot(value[0], value[1], marker='o',
                label=configuration.benchmarkDescription[int(key)])

  pyplot.title(configuration.plotTitle)
  pyplot.ylabel(configuration.yLabel)
  pyplot.xlabel(configuration.xLabel)
  pyplot.legend()
  pyplot.grid()

  # If no end for the x values is set, just take the maximum of them
  if configuration.xTickEnd == -1:
    for key, val in benchmarkDict.items():
      if max(val[0]) > configuration.xTickEnd:
        configuration.xTickEnd = max(val[0])

  if configuration.xTickStep != "auto":
    pyplot.xticks(range(int(configuration.xTickBegin),
                  int(configuration.xTickEnd)+1, int(configuration.xTickStep)))

  pyplot.savefig(configuration.outputFile, bbox_inches='tight')

def main():
  # Parse command line arguments
  parser = argparse.ArgumentParser(description = "Visualize Google Benchmark.",
                                   prog = "Benchmark Visualizer")

  parser.add_argument("--version", "-v",
                      version = getVersion(parser),
                      action = "version")
  parser.add_argument("--input_file", "-i",
                      metavar = "FILE", 
                      help = "Path to JSON file with benchmark results",
                      dest = "inputFile",
                      required = True)
  parser.add_argument("--output_file", "-o",
                      metavar = "FILE",
                      help = "Path to file where the image of the diagram will "
                             "be stored.",
                      dest = "outputFile",
                      required = True)
  parser.add_argument("--title",
                      metavar = "TITLE",
                      help = "Diagram title",
                      dest = "plotTitle",
                      default = "Benchmark Results")
  parser.add_argument("--time_unit",
                      choices = ["ns", "us", "ms"],
                      help = "Time unit for measured durations",
                      dest = "timeUnit",
                      default = "ns")
  parser.add_argument("--x_label",
                      metavar = "X_LABEL",
                      dest = "xLabel",
                      help = "Label on the x axis")
  parser.add_argument("--y_label",
                      metavar = "Y_LABEL",
                      dest = "yLabel",
                      help = "Lable on the y axis")
  parser.add_argument("--x_value", "-x",
                      metavar = "X_VALUE",
                      dest = "xValue",
                      help = "Name of the counter that stores the x value",
                      required = True)
  parser.add_argument("--y_value", "-y",
                      choices = ["real_time", "cpu_time"],
                      metavar = "y_VALUE",
                      dest = "yValue",
                      help = "Name of the y value that will be considered",
                      default = "real_time")
  parser.add_argument("--x_tick_begin",
                      metavar = "VALUE",
                      help = "Set the begin of the x ticks manually",
                      dest = "xTickBegin",
                      default = 0)
  parser.add_argument("--x_tick_end",
                      metavar = "VALUE",
                      help = "Set the end of the x ticks manually",
                      dest = "xTickEnd",
                      default = -1)
  parser.add_argument("--x_tick_step",
                      metavar = "VALUE",
                      help = "Set the steps of the x ticks manually",
                      dest = "xTickStep",
                      default = "auto")
  parser.add_argument("--benchmark_description", "-d",
                      metavar = "DESC",
                      nargs='*',
                      help = "Description of benchmarks",
                      dest = "benchmarkDescription",
                      required = True)
  parser.add_argument("--x_size",
                      metavar = "VALUE",
                      help = "The horizontal size of the produced plot in inches",
                      dest = "xSize")
  parser.add_argument("--y_size",
                      metavar = "VALUE",
                      help = "The vertical size of the produced plot in inches",
                      dest = "ySize")
  parser.add_argument("--dpi",
                      type=int,
                      metavar = "VALUE",
                      help = "DPI of the produced plot",
                      dest = "dpi",
                      default = None)

  args = parser.parse_args()

  configuration = PlottingConfiguration(args)
  data = parseJSON(configuration)
  plot(data, configuration)

if __name__ == "__main__":
  main()
