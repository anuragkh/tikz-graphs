#!/usr/bin/python

from math import pow, log10, floor
import argparse

pattern_types_tikz = ['north east lines', 'north west lines', 'grid', 'crosshatch', 'dots', 'crosshatch dots']
pattern_colors_tikz = ['red', 'cyan', 'green', 'black', 'gray', 'brown']
patterns_tikz = zip(pattern_types_tikz, pattern_colors_tikz)

def compute_bar_widths(data):
  # Determine number of rows, cols; each row correspond to a 'bar-group', each col is a single 'bar'.
  nrows = len(data)
  ncols = 0
  for row in data:
    ncols += len(row)
  nspaces = nrows + 1
  bar_width = float(100) / float(ncols + nspaces)

  return bar_width

def scale_data(data, ymin, ymax):
  return [[(value / (ymax - ymin)) * 100.0 for value in row] for row in data]

def get_yrange(data, args):
  ymin, ymax = (args.ymin, args.ymax)
  if ymax is None:
    data_max = max(map(max, data))
    ymax = round(data_max, -int(floor(log10(data_max))))
  if ymin is None:
    ymin = 0
  return ymin, ymax

def validate_data(data, ncols):
  for row in data:
    assert len(row) == ncols

def intify(val):
  if val.is_integer():
    return int(val)
  return val

def generate_tikz(args):
  input = open(args.data, 'r')

  # Get the bar labels
  blabels = map(str, input.readline().split())
  ncols = len(blabels)

  # Read the remainder of the file
  file_data = [line for line in input]

  xscale, yscale = args.xscale, args.yscale

  if xscale is None:
    xscale = 0.1

  if yscale is None:
    yscale = 0.1

  header = '''\
    \\begin{tikzpicture}[xscale=%.2f,yscale=%.2f]

    \\draw[preaction={fill=black,opacity=.5, transform canvas={xshift=1mm,yshift=-1mm}}, black][fill=white] (0,0) rectangle (100, 100);

    \\draw[dashed, gray] (-1, 25) -- (101, 25);
    \\draw[dashed, gray] (-1, 50) -- (101, 50);
    \\draw[dashed, gray] (-1, 75) -- (101, 75);

  ''' % (xscale, yscale)

  footer = '''\
    \\end{tikzpicture}\
  '''

  # Obtain the y label
  ylabel = args.ylabel
  if ylabel is None:
    ylabel = 'Y-Axis Label (Unit)'
  ylabel_tikz = '  \\node (label-align) [thick, black, align=center, rotate=90] at (-12.5, 50) {%s};\n\n' % ylabel

  # Get the data to plot, and validate it
  data = [map(float, line.split()[1:]) for line in file_data]
  validate_data(data, ncols)

  # Convert the data to logscale if requested
  if args.logscale:
    data = [map(log10, row) for row in data]
    if args.ymax is not None:
      args.ymax = log10(args.ymax)
    if args.ymin is not None:
      args.ymin = log10(args.ymin)

  # Scale the data to our plot
  ymin, ymax = get_yrange(data, args)
  data = scale_data(data, ymin, ymax)

  # Generate the y-axis marks
  ymarks_tikz = ''
  for mark in [25.0, 50.0, 75.0]:
    ymark = ymin + (mark * (ymax - ymin) / 100.0)
    if args.logscale:
      ymark = pow(10, ymark)
    ymarks_tikz += '  \\draw[thick, black] (-5, %.2f) node {%s};\n' % (mark, intify(ymark))

  ymarks_tikz += '\n'

  # Obtain the column widths
  width = compute_bar_widths(data)
  bar_grp_width = width * ncols

  # Generate plot data
  cur_bar_off = width
  plot_data_tikz = ''
  for row in data:
    # Generate data for a group of bars
    bar_grp_tikz = ''
    pattern_iter = iter(patterns_tikz)
    for col in row:
      pattern = pattern_iter.next()
      bar_grp_tikz += '  \draw[thick, pattern=%s, pattern color=%s] (%.2f,0) rectangle (%.2f,%.2f);\n' % \
                      (pattern[0], pattern[1], cur_bar_off, cur_bar_off + width, col)
      cur_bar_off += width
    plot_data_tikz += (bar_grp_tikz + '\n')
    cur_bar_off += width

  # Generate x-axis labels
  xlabels = [line.split()[0] for line in file_data]
  xlabel_offsets = [width + x * (bar_grp_width + width) + 0.5 * bar_grp_width for x in range(0, len(xlabels))]
  xlabels_tikz = ''
  for xlabel in zip(xlabel_offsets, xlabels):
    xlabels_tikz += '  \draw[thick, black] (%.2f, -5) node {%s};\n' % xlabel

  xlabels_tikz += '\n'

  # Generate bar label legend
  blabel_dist = 100 / ncols
  blabel_offsets = [x * blabel_dist for x in range(0, len(blabels))]
  blabels_tikz = ''
  pattern_iter = iter(patterns_tikz)
  for blabel in zip(blabel_offsets, blabels):
    pattern = pattern_iter.next()
    blabels_tikz += '  \draw[thick, pattern=%s, pattern color=%s] (%.2f, 102.5) rectangle (%.2f, 107.5);\n' \
                    % (pattern[0], pattern[1], blabel[0], blabel[0] + 5)
    blabels_tikz += '  \draw[thick, black] (%.2f, 105) node[text width=10] {%s};\n' % (blabel[0] + 10, blabel[1])

  blabels_tikz += '\n'

  # Generate entire tikz code and dump it to output file
  tikz = header + ymarks_tikz + ylabel_tikz + plot_data_tikz + xlabels_tikz + blabels_tikz + footer
  output = open(args.out, 'w')
  output.write(tikz)

def main():
  parser = argparse.ArgumentParser(description='Generates a TiKZ bar plot from an input file.')
  parser.add_argument('-d', '--data', type=str, metavar='DATA_FILE', required=True, help='The input data file.')
  parser.add_argument('-o', '--out', type=str, metavar='OUTPUT_FILE', required=True, help='The output TiKZ file.')
  parser.add_argument('--ymin', type=float, help='Lower limit to y-axis.')
  parser.add_argument('--ymax', type=float, help='Upper limit to y-axis.')
  parser.add_argument('--ylabel', type=str, help='Label for y-axis.')
  parser.add_argument('--xscale', type=float, help='Scale for x-axis.')
  parser.add_argument('--yscale', type=float, help='Scale for y-axis.')
  parser.add_argument('--logscale', '-l', action='store_true', help='Set logscale for y-axis')
  args = parser.parse_args()
  generate_tikz(args)

if __name__ == "__main__":
  main()
