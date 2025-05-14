import subprocess, time, cv2, os, shortpath83
import numpy

class ADB:
    def __init__(self):
        self.ospath = os.path.dirname(os.path.abspath(__file__))
        subprocess.check_call(f"{self.ospath}\\libs\\adb start-server", shell=True)
    
    def GetDevices(self, isMuMu: bool = False, pathMuMu: str = ""):
        if isMuMu:
            try:
                for i in range(40):
                    path = shortpath83.get_short_path_name(pathMuMu + '\\shell\\MuMuManager.exe')
                    subprocess.call([path, 'adb', '-v', str(i), 'connect'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True, timeout=15)
            except Exception as err:
                pass
        
        listdevice = []
        devices = str(subprocess.check_output(f"{self.ospath}\\libs\\adb devices", shell=True)).replace("b'List of devices attached\\r\\n", '').replace("'", '').replace('bList of devices attached ', '').split('\\r\\n')
        for device in devices:
            if device != '' and not "offline" in device:
                listdevice.append(device.split('\\tdevice')[0])
        return listdevice
    
    def ReloadServer(self):
        subprocess.check_call(f"{self.ospath}\\libs\\adb kill-server", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        subprocess.check_call(f"{self.ospath}\\libs\\adb start-server", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        
    def OpenTCP(self, device: str, port: int):
        subprocess.Popen(f"{self.ospath}\\libs\\adb -s {device} reverse tcp:{port} tcp:{port}", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    def OpenApp(self, device, package):
        subprocess.call(f"{self.ospath}\\libs\\adb -s {device} shell monkey -p {package} -c android.intent.category.LAUNCHER 1", shell=True)
        
    def PushFile(self, device, pathpc, pathphone):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} push {pathpc} {pathphone}", shell=True)
        
    def InstallApp(self, device, path):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} install {path}", shell=True)

    def OpenLink(self, device, link):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s "+device+" shell am start -a android.intent.action.VIEW -d '"+link+"'", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False, timeout=20)
        
    def StopApp(self, device, package):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s "+device+f" shell am force-stop {package}", shell=True)
    
    def ScreenCaptureSave(self, device):
        subprocess.call(f"{self.ospath}\\libs\\adb -s {device} exec-out screencap -p > MySnapshot.jpg", shell=True)
        return "./MySnapshot.jpg"
    
    def ScreenCaptureNoSave(self, device):
        pipe = subprocess.Popen(f"{self.ospath}\\libs\\adb -s {device} exec-out screencap -p", stdout=subprocess.PIPE, shell=True)
        img_bytes = pipe.stdout.read()
        return img_bytes
    
    def Pull(self, device, path, path1):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} pull {path} {path1}", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        
    def Push(self, device, path, path1):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} push {path} {path1}", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        
    def Click(self, device, x, y):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} shell input tap {int(x)} {int(y)}", shell=True)
    
    def CheckImg(self, device, target_pic_name):
        try:
            img = cv2.imread(target_pic_name, cv2.IMREAD_UNCHANGED)
            img2 = self.ScreenCaptureNoSave(device)
            result = cv2.matchTemplate(img, img2, cv2.TM_CCOEFF_NORMED) 
            min_val, max_value, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_value > 0.7:
                return True
            else:
                return False
        except:
            return False
        
    def ImgCrop(self, device, x, y, w, h):
        try:
            img2 = self.ScreenCaptureNoSave(device)

            img2_cropped = img2[y:y+h, x:x+w]
            _, threshold_img = cv2.threshold(img2_cropped, 128, 255, cv2.THRESH_BINARY)
            return threshold_img
        except Exception as e:
            print(e)
            return None
    
    def KeyEvent(self, device, key):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} shell input keyevent {str(key)}")
    
    def Swipe(self, device, x1, y1, x2, y2, duration: int = 1000):
        subprocess.check_call(f"{self.ospath}\\libs\\adb -s {device} shell input touchscreen swipe {x1} {y1} {x2} {y2} {duration}")

    def SetTextClipbroad(self, device, text):
        subprocess.check_call(f'{self.ospath}\\libs\\adb -s {device} shell am broadcast -a clipper.set -e text "{text}"', shell=True)
        
    def Paste(self, device):
        subprocess.check_call(f'{self.ospath}\\libs\\adb -s {device} shell input keyevent 279', shell=True)
    
    def TypeText(self, device, text):
        subprocess.check_call(f'{self.ospath}\\libs\\adb -s {device} shell input text "{text}"', shell=True)
        
    def CheckAppRunning(self, device, package):
        try:
            pid = subprocess.check_output(f'{self.ospath}\\libs\\adb -s {device} shell pidof {package}', shell=True)
            if pid: return True
            else: return False
        except:
            return False

    def CheckAppInstalled(self, device, package):
        try:
            pids = subprocess.check_output(f'{self.ospath}\\libs\\adb -s {device} shell pm list packages {package}', shell=True)
            if package in str(pids.decode()): return True
            else: return False
        except: return False

    def GetPackageNames(self, device):
        try:
            pids = subprocess.check_output(f'{self.ospath}\\libs\\adb -s {device} shell pm list packages', shell=True)
            return str(pids.decode()).split('\n')
        except: return []

    def UninstallApp(self, device, package):
        subprocess.check_call(f'{self.ospath}\\libs\\adb -s {device} uninstall {package}', shell=True)

    def DeleteFile(self, device, path):
        subprocess.check_output(f'{self.ospath}\\libs\\adb -s {device} shell rm {path}')