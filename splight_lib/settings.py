import os
import sys

TESTING = "test" in sys.argv or "pytest" in sys.argv
SPLIGHT_HOME = os.path.join(os.getenv('HOME'), '.splight')
USE_TZ = True
