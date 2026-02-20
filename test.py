import numpy as np


def scale_number_units(value, unit):
    prefixs = np.array(["T", "G", "M", "k", "", "m", "μ", "n", "p", "f"])
    scales = np.array(
        [1.0e12, 1.0e9, 1.0e6, 1.0e3, 1.0, 1.0e-3, 1.0e-6, 1.0e-9, 1.0e-12, 1.0e-15]
    )
    sel = np.array(value / scales, dtype="int") > 0
    prefix = prefixs[sel][0]
    scale = scales[sel][0]
    print("{:5.1f}{}{}".format(value / scale, prefix, unit))


scale_number_units(3000, "m")
