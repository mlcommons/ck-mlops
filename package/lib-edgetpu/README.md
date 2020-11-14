## Coral edgetpu package

This package installs the driver required to run the Coral edgetpu.

There are two versions; std and max.

```
$ ck install package --tags=lib,edgetpu,std_14.1_arm64
$ ck install package --tags=lib,edgetpu,max_14.1_arm64
```

Warning from the Coral.ai website

```
Caution: When operating the device using the maximum clock frequency, the metal on the USB Accelerator can become very hot to the touch. This might cause burn injuries. To avoid injury, either keep the device out of reach when operating it at maximum frequency, or use the reduced clock frequency.
```
