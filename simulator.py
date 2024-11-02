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
parser.add_argument("--step", help = "Simulation time step (seconds)", type = int, default = 600)
#parser.add_argument("--start", help = "Simulation start time (unix)", type = int, default = 1672552800)
#parser.add_argument("--end", help = "Simulation end time (unix)", type = int, default = 1704088800)
args = parser.parse_args()

print("Reading image...")
img = Image.open(args.FILE)
arr = numpy.array(img)[:,:,0]

# White = clear, black = undefined, gray = blocked
print("Parsing image...")
arr[arr == 255] = 1
arr[arr == 0] = 2
arr[arr == 127] = 0
if arr.max() > 2:
    print("Error: Image contains invalid pixels.")
    exit()

panel = Panel(args.lat, args.lon, arr, args.azimuth, args.tilt)

print("Simulating...")
months = [1704067200, 1706745600, 1709251200, 1711929600, 1714521600, 1717200000, 1719792000, 1722470400, 1725148800, 1727740800, 1730419200, 1733011200, 1735689600]
month_efficiencies = [0] * 12
for month in range(12):
    start = months[month]
    end = months[month + 1]
    efficiency_sum = 0
    efficiency_count = 0
    for t in range(start, end, args.step):
        efficiency_sum += panel.get_panel_efficiency(t)
        efficiency_count += 1
    month_efficiencies[month] = efficiency_sum / efficiency_count
    print(f"Finished month {month + 1}...")

print("Done.")
for month in range(12):
    print(f"Month {month + 1}: {month_efficiencies[month] * 100:.2f}%")
print(f"Average: {sum(month_efficiencies) * 100 / 12:.2f}%")
