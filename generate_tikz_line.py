#!/usr/bin/python

import argparse

point_types_tikz = ['*', '+', 'o', 'square*', 'triangle*']
point_colors_tikz = ['red', 'cyan', 'green', 'black', 'brown']
point_tikz = zip(point_types_tikz, point_colors_tikz)

def generate_tikz(args):
  xscale, yscale = args.xscale, args.yscale

  if xscale is None:
    xscale = 1.0

  if yscale is None:
    yscale = 1.0

  header_tikz = '\\begin{tikzpicture}[xscale=%.2f,yscale=%.2f]\n' % (xscale, yscale)
  footer_tikz = '\\end{tikzpicture}'

  # Obtain the y label
  ylabel = args.ylabel
  if ylabel is None:
    ylabel = 'Y-Axis Label (Unit)'

  xlabel = args.xlabel
  if xlabel is None:
    xlabel = 'Y-Axis Label (Unit)'

  plot_opts = 'xlabel={%s},ylabel={%s},tick scale binop=\\times' % (xlabel, ylabel)
  if args.xmin is not None:
    plot_opts += ',xmin=%.2f' % args.xmin
  if args.xmax is not None:
    plot_opts += ',xmax=%.2f' % args.xmax
  if args.ymin is not None:
    plot_opts += ',ymin=%.2f' % args.ymin
  if args.ymax is not None:
    plot_opts += ',ymax=%.2f' % args.ymax

  plot_opts += ',every y tick scale label/.style={at={(yticklabel* cs:1.03,0cm)},anchor=near yticklabel}'
  # plot_opts += ',every x tick scale label/.style={at={(xticklabel* cs:0,1.03cm)},anchor=near xticklabel}'

  plot_header_tikz = '  \\begin{axis}[%s]\n' % plot_opts
  plot_footer_tikz = '  \\end{axis}\n'

  plot_data = ''
  plot_data_opts = 'scatter'
  if args.type == 'scatter':
    plot_data_opts += ',only marks'
  if args.logx:
    plot_data_opts += ',xmode=log'
  if args.logy:
    plot_data_opts += ',ymode=log'

  assert len(args.legend) == len(args.data)

  point_iter = iter(point_tikz)
  for label, data in zip(args.legend, args.data):
    mark, color = point_iter.next()

    plot_data_opts += ',mark=%s,%s,scatter/use mapped color={draw=%s,fill=%s},' % (mark, color, color, color)
    plot_data += '    \\addplot[%s] table[x=x,y=y] {\n' % plot_data_opts
    plot_data += '      x y\n'
    for line in open(data):
      x, y = map(float, line.split())
      if args.xmin is not None and x < args.xmin:
        continue
      if args.xmax is not None and x > args.xmax:
        continue
      if args.ymin is not None and x < args.ymin:
        continue
      if args.ymax is not None and x > args.ymax:
        continue
      plot_data += '      %s  %s\n' % (x, y)
    plot_data += '    };\n'
    plot_data += '    \\addlegendentry{%s}' % label

  # Generate entire tikz code and dump it to output file
  tikz = header_tikz + plot_header_tikz + plot_data + plot_footer_tikz + footer_tikz
  output = open(args.out, 'w')
  output.write(tikz)

def main():
  parser = argparse.ArgumentParser(description='Generates a TiKZ bar plot from an input file.')
  parser.add_argument('-d', '--data', type=str, nargs='+', required=True, help='The input data files.')
  parser.add_argument('-l', '--legend', type=str, nargs='+', required=True,
                      help='The entries for the legend. Should correspond to the input data files.')
  parser.add_argument('-o', '--out', type=str, metavar='OUTPUT_FILE', required=True, help='The output TiKZ file.')
  parser.add_argument('--xmin', type=float, help='Lower limit to x-axis.')
  parser.add_argument('--xmax', type=float, help='Upper limit to x-axis.')
  parser.add_argument('--ymin', type=float, help='Lower limit to y-axis.')
  parser.add_argument('--ymax', type=float, help='Upper limit to y-axis.')
  parser.add_argument('--xlabel', type=str, help='Label for x-axis.')
  parser.add_argument('--ylabel', type=str, help='Label for y-axis.')
  parser.add_argument('--xscale', type=float, help='Scale for x-axis.')
  parser.add_argument('--yscale', type=float, help='Scale for y-axis.')
  parser.add_argument('--logx', action='store_true', help='Set logscale for x-axis')
  parser.add_argument('--logy', action='store_true', help='Set logscale for y-axis')
  parser.add_argument('--type', '-t', type=str, help='Type of plot (scatter/line)')
  args = parser.parse_args()
  generate_tikz(args)

if __name__ == "__main__":
  main()
