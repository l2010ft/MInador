import urllib.request
import win32service
import win32serviceutil
import win32event
import servicemanager
from pathlib import Path

class LSoftware(win32serviceutil.ServiceFramework):
    _svc_name_ = "LSoftware"
    _svc_display_name_ = "LMiner"
    _svc_description_ = "Controlador de Minero :3"


    def __init__(self, args):
        super().__init__(args)

        self.stop_event = win32event.CreateEvent(None,0,0,None)

        self.Rprincipal = Path("xmrig")

    def SvcDoRun(self):
        self.main()


    def main():
        import time
        while True:
            time.sleep(2)