# Convert TF models into OpenVINO format

## Calibration prerequisites (for the image classification variations only)

```bash
$ python3.6 -m pip install --user \
  nibabel numpy pillow progress py-cpuinfo pyyaml shapely sklearn tqdm xmltodict yamlloader
```

**NB:** The requirements specifically mandated `py-cpuinfo<=4.0` and `scipy<1.2` but `py-cpuinfo-5.0.0` and `scipy-1.3.1` seem to be fine.
