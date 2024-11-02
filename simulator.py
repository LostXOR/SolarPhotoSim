from PIL import Image
import numpy
import argparse
from panel import Panel

# Hide warning about large images
Image.MAX_IMAGE_PIXELS = 999999999

parser = argparse.ArgumentParser(
    description = "Simulates solar panel efficiency in a shaded area"
)
parser.add_argument("FILE", help = "Path to the equirectangular projection image")
parser.add_argument("--lat", help = "Panel latitude", type = float, required = True)
parser.add_argument("--lon", help = "Panel longitude", type = float, required = True)
parser.add_argument("--azimuth", help = "Panel azimuth", type = float, required = True)
parser.add_argument("--tilt", help = "Panel tilt angle", type = float, required = True)
parser.add_argument("--start", help = "Simulation start time (unix)", type = int, default = 1672552800)
parser.add_argument("--end", help = "Simulation end time (unix)", type = int, default = 1704088800)
args = parser.parse_args()

print("Reading image...")
img = Image.open(args.FILE)
arr = numpy.array(img)[:,:,0]

# White = clear, black = undefined, gray = blocked
arr[arr == 255] = 1
arr[arr == 0] = 2
arr[arr == 127] = 0
arr[arr > 2] = 2

panel = Panel(args.lat, args.lon, arr, args.azimuth, args.tilt)

eff_sums = []
eff_count = 0
for month in range(12):
    eff_count = 0
    eff_sums.append(0)
    for i in range(args.start + 86400 * 30 * month, args.start + 86400 * 30 * (month + 1), 60):
        eff_sums[month] += panel.get_panel_efficiency(i)
        eff_count += 1

for summ in eff_sums:
    print(summ / eff_count)

print(f"Final: {sum(eff_sums) / eff_count / 12}")
