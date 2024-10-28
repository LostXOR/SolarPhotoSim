import argparse
import numpy
from PIL import Image

# Hide warning about large images
Image.MAX_IMAGE_PIXELS = 999999999

parser = argparse.ArgumentParser(
    description = "Converts Google Photo Sphere images to a properly aligned equirectangular projection"
)
parser.add_argument("FILE", help = "Path to the Google Photo Sphere file")
parser.add_argument("-H", "--heading", help = "Manually specify the heading of the center of the image", type = int)
parser.add_argument("-N", "--north", help = "Manually specify the X coordinate of true north in the image", type = int)
parser.add_argument("-O", "--output", help = "Output filename")
args = parser.parse_args()

print("Reading image...")
img = Image.open(args.FILE)

# Read metadata to determine image crop and heading
print("Parsing metadata...")
try:
    metadata = img.getxmp()["xmpmeta"]["RDF"]["Description"]
    full_size = (int(metadata["FullPanoWidthPixels"]), int(metadata["FullPanoHeightPixels"]))
    offset = (int(metadata["CroppedAreaLeftPixels"]), int(metadata["CroppedAreaTopPixels"]))
    heading = float(metadata["PoseHeadingDegrees"]) if args.heading is None else args.heading
    shift = heading / 360 * full_size[0] - full_size[0] // 2 if args.north is None else -args.north - offset[0]
except:
    print("Error: Image does not have the required metadata!")
    exit()

print(f"Full size: ({full_size[0]}, {full_size[1]})")
print(f"Offset: ({offset[0]}, {offset[1]})")
print(f"Heading: {heading}deg")

print(f"Expanding image to full equirectangular dimensions...")
img = img.crop((-offset[0], -offset[1], full_size[0] - offset[0], full_size[1] - offset[1]))

print(f"Shifting image {shift}px to align north...")
arr = numpy.array(img)
arr = numpy.roll(arr, int(shift), axis = 1)

# Save shifted array as image
filename = args.output if args.output is not None else args.FILE.removesuffix(".jpg") + "_equirectangular.png"
print(f"Saving image as {filename}...")
img = Image.fromarray(arr)
img.save(filename)
print("Done.")
