from pathlib import Path
import os
from applehealthtool.app import AppleHealthTool

if __name__ == '__main__':
    app = AppleHealthTool()
    app.setup()
    app.run()
