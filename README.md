# SolarPhotoSim

Simulator for solar panels in semi-shady environments using 360 photos. WIP.

## Usage

Convert Google Photo Sphere photos to a full equirectangular projection with `convert.py`:

```shell
python3 convert.py <photo sphere image> -o [output filename]
```

Using your favorite image editor, replace clear sky with white (#FFFFFF), and obstructed areas with neutral gray (#7F7F7F). Black areas are considered undefined.

Run the simulation with:

```shell
python3 simulator.py --lat <latitude> --lon <longitude> --azimuth <panel azimuth> --tilt <panel tilt> <image path>
```
