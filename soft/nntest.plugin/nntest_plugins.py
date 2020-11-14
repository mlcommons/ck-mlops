import os
import sys
import pathlib
import importlib

def getPlugin(unit, impl):
    unit = unit.upper()
    impl = impl.upper()
    for k, v in os.environ.items():
        if k.find("CK_NNTEST_PLUGIN") != -1:
            if k.find(unit) != -1:
                if k.find(impl) != -1:
                    directory = os.path.dirname(v)
                    sys.path.append(directory)
                    module_name = pathlib.Path(v).stem
                    return importlib.import_module(module_name)
    return None

