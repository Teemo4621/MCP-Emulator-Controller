import subprocess
import time
import cv2
import os
import shortpath83
import numpy as np
from typing import List, Optional, Tuple
import logging


class ADBController:
    """
    Android Debug Bridge (ADB) Controller for device automation
    
    This class provides methods to interact with Android devices through ADB,
    including screen capture, app management, input simulation, and file operations.
    """
    
    def __init__(self, adb_path: Optional[str] = None):
        """
        Initialize ADB Controller
        
        Args:
            adb_path: Custom path to ADB executable. If None, uses libs/adb in script directory.
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.adb_path = adb_path or os.path.join(self.script_dir, "libs", "adb")
        
        # Setup logging
        self._setup_logging()
        
        # Start ADB server
        self._start_server()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _start_server(self):
        """Start ADB server"""
        try:
            self._run_adb_command("start-server")
            self.logger.info("ADB server started successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to start ADB server: {e}")
            raise
    
    def _run_adb_command(self, command: str, device: Optional[str] = None, 
                        capture_output: bool = False, timeout: int = 30) -> Optional[str]:
        """
        Run ADB command with proper error handling
        
        Args:
            command: ADB command to execute
            device: Target device ID (optional)
            capture_output: Whether to capture and return output
            timeout: Command timeout in seconds
            
        Returns:
            Command output if capture_output=True, otherwise None
        """
        if device:
            full_command = f'"{self.adb_path}" -s {device} {command}'
        else:
            full_command = f'"{self.adb_path}" {command}'
        
        try:
            if capture_output:
                result = subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=True
                )
                return result.stdout.strip()
            else:
                subprocess.run(
                    full_command,
                    shell=True,
                    timeout=timeout,
                    check=True
                )
                return None
        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timed out: {full_command}")
            raise
        except subprocess.CalledProcessError as e:
            self.logger.error(f"ADB command failed: {full_command}, Error: {e}")
            raise
    
    def get_devices(self, enable_mumu: bool = False, mumu_path: str = "") -> List[str]:
        """
        Get list of connected devices
        
        Args:
            enable_mumu: Whether to connect MuMu emulator instances
            mumu_path: Path to MuMu emulator installation
            
        Returns:
            List of device IDs
        """
        if enable_mumu and mumu_path:
            self._connect_mumu_devices(mumu_path)
        
        try:
            output = self._run_adb_command("devices", capture_output=True)
            devices = []
            
            for line in output.split('\n')[1:]:  # Skip header line
                line = line.strip()
                if line and 'offline' not in line and 'unauthorized' not in line:
                    device_id = line.split('\t')[0]
                    if device_id:
                        devices.append(device_id)
            
            self.logger.info(f"Found {len(devices)} connected devices")
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get devices: {e}")
            return []
    
    def _connect_mumu_devices(self, mumu_path: str):
        """Connect MuMu emulator devices"""
        try:
            manager_path = os.path.join(mumu_path, 'shell', 'MuMuManager.exe')
            short_path = shortpath83.get_short_path_name(manager_path)
            
            for i in range(40):
                try:
                    subprocess.run(
                        [short_path, 'adb', '-v', str(i), 'connect'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=15,
                        check=False
                    )
                except subprocess.TimeoutExpired:
                    continue
        except Exception as e:
            self.logger.warning(f"Failed to connect MuMu devices: {e}")
    
    def reload_server(self):
        """Restart ADB server"""
        try:
            self._run_adb_command("kill-server")
            time.sleep(1)
            self._run_adb_command("start-server")
            self.logger.info("ADB server reloaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to reload ADB server: {e}")
            raise
    
    def setup_tcp_forward(self, device: str, port: int):
        """
        Setup TCP port forwarding
        
        Args:
            device: Target device ID
            port: Port number to forward
        """
        try:
            self._run_adb_command(f"reverse tcp:{port} tcp:{port}", device)
            self.logger.info(f"TCP forwarding setup for port {port} on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to setup TCP forwarding: {e}")
            raise
    
    def launch_app(self, device: str, package: str):
        """
        Launch an application
        
        Args:
            device: Target device ID
            package: Application package name
        """
        try:
            command = f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
            self._run_adb_command(command, device)
            self.logger.info(f"Launched app {package} on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to launch app {package}: {e}")
            raise
    
    def stop_app(self, device: str, package: str):
        """
        Force stop an application
        
        Args:
            device: Target device ID
            package: Application package name
        """
        try:
            command = f"shell am force-stop {package}"
            self._run_adb_command(command, device)
            self.logger.info(f"Stopped app {package} on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to stop app {package}: {e}")
            raise
    
    def capture_screen(self, device: str, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Capture device screen
        
        Args:
            device: Target device ID
            save_path: Optional path to save screenshot
            
        Returns:
            Screenshot as numpy array, or None if failed
        """
        try:
            # Capture screenshot as bytes
            result = subprocess.run(
                f'"{self.adb_path}" -s {device} exec-out screencap -p',
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"Screenshot command failed: {result.stderr}")
                return None
            
            # Convert bytes to numpy array
            img_bytes = result.stdout
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                self.logger.error("Failed to decode screenshot")
                return None
            
            # Save if path provided
            if save_path:
                cv2.imwrite(save_path, img)
                self.logger.info(f"Screenshot saved to {save_path}")
            
            return img
            
        except Exception as e:
            self.logger.error(f"Failed to capture screen: {e}")
            return None
    
    def tap(self, device: str, x: int, y: int):
        """
        Simulate touch tap
        
        Args:
            device: Target device ID
            x: X coordinate
            y: Y coordinate
        """
        try:
            command = f"shell input tap {x} {y}"
            self._run_adb_command(command, device)
            self.logger.debug(f"Tapped at ({x}, {y}) on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to tap at ({x}, {y}): {e}")
            raise
    
    def swipe(self, device: str, x1: int, y1: int, x2: int, y2: int, duration: int = 1000):
        """
        Simulate swipe gesture
        
        Args:
            device: Target device ID
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration: Swipe duration in milliseconds
        """
        try:
            command = f"shell input touchscreen swipe {x1} {y1} {x2} {y2} {duration}"
            self._run_adb_command(command, device)
            self.logger.debug(f"Swiped from ({x1}, {y1}) to ({x2}, {y2}) on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to swipe: {e}")
            raise
    
    def send_key_event(self, device: str, key_code: int):
        """
        Send key event
        
        Args:
            device: Target device ID
            key_code: Android key code
        """
        try:
            command = f"shell input keyevent {key_code}"
            self._run_adb_command(command, device)
            self.logger.debug(f"Sent key event {key_code} to device {device}")
        except Exception as e:
            self.logger.error(f"Failed to send key event {key_code}: {e}")
            raise
    
    def type_text(self, device: str, text: str):
        """
        Type text on device
        
        Args:
            device: Target device ID
            text: Text to type
        """
        try:
            # Escape special characters
            escaped_text = text.replace('"', '\\"').replace("'", "\\'")
            command = f'shell input text "{escaped_text}"'
            self._run_adb_command(command, device)
            self.logger.debug(f"Typed text on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to type text: {e}")
            raise
    
    def install_app(self, device: str, apk_path: str):
        """
        Install APK file
        
        Args:
            device: Target device ID
            apk_path: Path to APK file
        """
        try:
            command = f"install {apk_path}"
            self._run_adb_command(command, device, timeout=300)  # Longer timeout for installation
            self.logger.info(f"Installed app from {apk_path} on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to install app: {e}")
            raise
    
    def uninstall_app(self, device: str, package: str):
        """
        Uninstall application
        
        Args:
            device: Target device ID
            package: Package name to uninstall
        """
        try:
            command = f"uninstall {package}"
            self._run_adb_command(command, device)
            self.logger.info(f"Uninstalled app {package} from device {device}")
        except Exception as e:
            self.logger.error(f"Failed to uninstall app {package}: {e}")
            raise
    
    def push_file(self, device: str, local_path: str, remote_path: str):
        """
        Push file to device
        
        Args:
            device: Target device ID
            local_path: Local file path
            remote_path: Remote file path on device
        """
        try:
            command = f"push {local_path} {remote_path}"
            self._run_adb_command(command, device, timeout=120)
            self.logger.info(f"Pushed file {local_path} to {remote_path} on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to push file: {e}")
            raise
    
    def pull_file(self, device: str, remote_path: str, local_path: str):
        """
        Pull file from device
        
        Args:
            device: Target device ID
            remote_path: Remote file path on device
            local_path: Local file path
        """
        try:
            command = f"pull {remote_path} {local_path}"
            self._run_adb_command(command, device, timeout=120)
            self.logger.info(f"Pulled file {remote_path} to {local_path} from device {device}")
        except Exception as e:
            self.logger.error(f"Failed to pull file: {e}")
            raise
    
    def is_app_running(self, device: str, package: str) -> bool:
        """
        Check if application is running
        
        Args:
            device: Target device ID
            package: Package name to check
            
        Returns:
            True if app is running, False otherwise
        """
        try:
            command = f"shell pidof {package}"
            output = self._run_adb_command(command, device, capture_output=True)
            return bool(output and output.strip())
        except Exception:
            return False
    
    def is_app_installed(self, device: str, package: str) -> bool:
        """
        Check if application is installed
        
        Args:
            device: Target device ID
            package: Package name to check
            
        Returns:
            True if app is installed, False otherwise
        """
        try:
            command = f"shell pm list packages {package}"
            output = self._run_adb_command(command, device, capture_output=True)
            return package in output
        except Exception:
            return False
    
    def get_installed_packages(self, device: str) -> List[str]:
        """
        Get list of installed packages
        
        Args:
            device: Target device ID
            
        Returns:
            List of package names
        """
        try:
            command = "shell pm list packages"
            output = self._run_adb_command(command, device, capture_output=True)
            packages = []
            
            for line in output.split('\n'):
                if line.startswith('package:'):
                    package = line.replace('package:', '').strip()
                    if package:
                        packages.append(package)
            
            return packages
        except Exception as e:
            self.logger.error(f"Failed to get installed packages: {e}")
            return []
    
    def open_url(self, device: str, url: str):
        """
        Open URL in default browser
        
        Args:
            device: Target device ID
            url: URL to open
        """
        try:
            command = f"shell am start -a android.intent.action.VIEW -d '{url}'"
            self._run_adb_command(command, device)
            self.logger.info(f"Opened URL {url} on device {device}")
        except Exception as e:
            self.logger.error(f"Failed to open URL {url}: {e}")
            raise
    
    def find_image_on_screen(self, device: str, template_path: str, threshold: float = 0.7) -> Optional[Tuple[int, int]]:
        """
        Find image template on screen using template matching
        
        Args:
            device: Target device ID
            template_path: Path to template image
            threshold: Matching threshold (0.0 to 1.0)
            
        Returns:
            (x, y) coordinates of match center, or None if not found
        """
        try:
            # Capture current screen
            screen = self.capture_screen(device)
            if screen is None:
                return None
            
            # Load template image
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                self.logger.error(f"Failed to load template image: {template_path}")
                return None
            
            # Perform template matching
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Calculate center coordinates
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                self.logger.info(f"Found template at ({center_x}, {center_y}) with confidence {max_val:.2f}")
                return (center_x, center_y)
            else:
                self.logger.debug(f"Template not found (max confidence: {max_val:.2f})")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to find image on screen: {e}")
            return None


# Maintain backward compatibility
ADB = ADBController