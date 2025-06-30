import base64
import io
import logging
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Image
from adbfunc import ADBController
from PIL import Image as PILImage
import cv2
import numpy as np

# Initialize FastMCP server
mcp = FastMCP("MCPEmulatorController")

# Initialize ADB Controller
adb_controller = ADBController()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def numpy_to_pil_image(img_array: np.ndarray) -> PILImage.Image:
    """
    Convert numpy array to PIL Image
    
    Args:
        img_array: OpenCV image array (BGR format)
        
    Returns:
        PIL Image object
    """
    # Convert BGR to RGB
    if len(img_array.shape) == 3:
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = img_array
    
    return PILImage.fromarray(img_rgb)


def pil_to_base64(img: PILImage.Image, format: str = "PNG") -> str:
    """
    Convert PIL Image to base64 string
    
    Args:
        img: PIL Image object
        format: Image format (PNG, JPEG, etc.)
        
    Returns:
        Base64 encoded string
    """
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


@mcp.tool()
async def get_devices(enable_mumu: bool = False, mumu_path: str = "D:\\MuMuPlayerGlobal-12.0") -> Dict[str, Any]:
    """
    Get list of connected Android devices
    
    Args:
        enable_mumu: Enable MuMu emulator connection
        mumu_path: Path to MuMu emulator installation
        
    Returns:
        Dictionary containing device list and status
    """
    try:
        devices = adb_controller.get_devices(enable_mumu, mumu_path)
        logger.info(f"Retrieved {len(devices)} devices")
        
        return {
            "devices": devices,
            "count": len(devices),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        return {
            "devices": [],
            "count": 0,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def reload_adb_server() -> Dict[str, Any]:
    """
    Reload ADB server (kill and restart)
    
    Returns:
        Status dictionary
    """
    try:
        adb_controller.reload_server()
        logger.info("ADB server reloaded successfully")
        
        return {
            "status": "success",
            "message": "ADB server reloaded successfully"
        }
    except Exception as e:
        logger.error(f"Failed to reload ADB server: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def setup_tcp_port(device: str, port: int) -> Dict[str, Any]:
    """
    Setup TCP port forwarding for device
    
    Args:
        device: Target device ID
        port: Port number to forward
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.setup_tcp_forward(device, port)
        logger.info(f"TCP port {port} forwarding setup for device {device}")
        
        return {
            "device": device,
            "port": port,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to setup TCP port forwarding: {e}")
        return {
            "device": device,
            "port": port,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def get_installed_packages(device: str) -> Dict[str, Any]:
    """
    Get all installed packages from device
    
    Args:
        device: Target device ID
        
    Returns:
        Dictionary containing package list and status
    """
    try:
        packages = adb_controller.get_installed_packages(device)
        logger.info(f"Retrieved {len(packages)} packages from device {device}")
        
        return {
            "packages": packages,
            "count": len(packages),
            "device": device,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get packages: {e}")
        return {
            "packages": [],
            "count": 0,
            "device": device,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def launch_application(device: str, package: str) -> Dict[str, Any]:
    """
    Launch an application on device
    
    Args:
        device: Target device ID
        package: Application package name
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.launch_app(device, package)
        logger.info(f"Launched app {package} on device {device}")
        
        return {
            "device": device,
            "package": package,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to launch app: {e}")
        return {
            "device": device,
            "package": package,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def stop_application(device: str, package: str) -> Dict[str, Any]:
    """
    Stop (force close) an application on device
    
    Args:
        device: Target device ID
        package: Application package name
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.stop_app(device, package)
        logger.info(f"Stopped app {package} on device {device}")
        
        return {
            "device": device,
            "package": package,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to stop app: {e}")
        return {
            "device": device,
            "package": package,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def tap_screen(device: str, x: int, y: int) -> Dict[str, Any]:
    """
    Simulate touch tap on device screen
    
    Args:
        device: Target device ID
        x: X coordinate
        y: Y coordinate
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.tap(device, x, y)
        logger.info(f"Tapped at ({x}, {y}) on device {device}")
        
        return {
            "device": device,
            "x": x,
            "y": y,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to tap screen: {e}")
        return {
            "device": device,
            "x": x,
            "y": y,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def swipe_screen(device: str, x1: int, y1: int, x2: int, y2: int, duration: int = 1000) -> Dict[str, Any]:
    """
    Simulate swipe gesture on device screen
    
    Args:
        device: Target device ID
        x1, y1: Start coordinates
        x2, y2: End coordinates
        duration: Swipe duration in milliseconds
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.swipe(device, x1, y1, x2, y2, duration)
        logger.info(f"Swiped from ({x1}, {y1}) to ({x2}, {y2}) on device {device}")
        
        return {
            "device": device,
            "start_x": x1,
            "start_y": y1,
            "end_x": x2,
            "end_y": y2,
            "duration": duration,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to swipe screen: {e}")
        return {
            "device": device,
            "start_x": x1,
            "start_y": y1,
            "end_x": x2,
            "end_y": y2,
            "duration": duration,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def capture_screenshot(device: str, save_path: Optional[str] = None) -> Image:
    """
    Capture screenshot from device and return as image
    
    Args:
        device: Target device ID
        save_path: Optional path to save screenshot file
        
    Returns:
        MCP Image object containing the screenshot
    """
    try:
        # Capture screen as numpy array
        screen_array = adb_controller.capture_screen(device, save_path)
        
        if screen_array is None:
            logger.error(f"Failed to capture screen from device {device}")
            # Return a blank image as fallback
            blank_img = PILImage.new('RGB', (100, 100), color='black')
            buffer = io.BytesIO()
            blank_img.save(buffer, format='PNG')
            return Image(data=buffer.getvalue(), format="png")
        
        # Convert numpy array to PIL Image
        pil_image = numpy_to_pil_image(screen_array)
        
        # Convert to PNG bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        
        logger.info(f"Screenshot captured from device {device}")
        
        return Image(data=image_bytes, format="png")
        
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        # Return a blank image as fallback
        blank_img = PILImage.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        blank_img.save(buffer, format='PNG')
        return Image(data=buffer.getvalue(), format="png")


@mcp.tool()
async def type_text_on_device(device: str, text: str) -> Dict[str, Any]:
    """
    Type text on device
    
    Args:
        device: Target device ID
        text: Text to type
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.type_text(device, text)
        logger.info(f"Typed text on device {device}")
        
        return {
            "device": device,
            "text_length": len(text),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to type text: {e}")
        return {
            "device": device,
            "text_length": len(text),
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def send_key_event(device: str, key_code: int) -> Dict[str, Any]:
    """
    Send key event to device
    
    Args:
        device: Target device ID
        key_code: Android key code (e.g., 4 for BACK, 3 for HOME)
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.send_key_event(device, key_code)
        logger.info(f"Sent key event {key_code} to device {device}")
        
        return {
            "device": device,
            "key_code": key_code,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to send key event: {e}")
        return {
            "device": device,
            "key_code": key_code,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def install_application(device: str, apk_path: str) -> Dict[str, Any]:
    """
    Install APK file on device
    
    Args:
        device: Target device ID
        apk_path: Path to APK file
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.install_app(device, apk_path)
        logger.info(f"Installed app from {apk_path} on device {device}")
        
        return {
            "device": device,
            "apk_path": apk_path,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to install app: {e}")
        return {
            "device": device,
            "apk_path": apk_path,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def uninstall_application(device: str, package: str) -> Dict[str, Any]:
    """
    Uninstall application from device
    
    Args:
        device: Target device ID
        package: Package name to uninstall
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.uninstall_app(device, package)
        logger.info(f"Uninstalled app {package} from device {device}")
        
        return {
            "device": device,
            "package": package,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to uninstall app: {e}")
        return {
            "device": device,
            "package": package,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def push_file_to_device(device: str, local_path: str, remote_path: str) -> Dict[str, Any]:
    """
    Push file to device
    
    Args:
        device: Target device ID
        local_path: Local file path
        remote_path: Remote path on device
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.push_file(device, local_path, remote_path)
        logger.info(f"Pushed file {local_path} to {remote_path} on device {device}")
        
        return {
            "device": device,
            "local_path": local_path,
            "remote_path": remote_path,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to push file: {e}")
        return {
            "device": device,
            "local_path": local_path,
            "remote_path": remote_path,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def pull_file_from_device(device: str, remote_path: str, local_path: str) -> Dict[str, Any]:
    """
    Pull file from device
    
    Args:
        device: Target device ID
        remote_path: Remote file path on device
        local_path: Local file path
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.pull_file(device, remote_path, local_path)
        logger.info(f"Pulled file {remote_path} to {local_path} from device {device}")
        
        return {
            "device": device,
            "remote_path": remote_path,
            "local_path": local_path,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to pull file: {e}")
        return {
            "device": device,
            "remote_path": remote_path,
            "local_path": local_path,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def check_app_status(device: str, package: str) -> Dict[str, Any]:
    """
    Check application installation and running status
    
    Args:
        device: Target device ID
        package: Package name to check
        
    Returns:
        Dictionary containing app status information
    """
    try:
        is_installed = adb_controller.is_app_installed(device, package)
        is_running = adb_controller.is_app_running(device, package) if is_installed else False
        
        return {
            "device": device,
            "package": package,
            "is_installed": is_installed,
            "is_running": is_running,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to check app status: {e}")
        return {
            "device": device,
            "package": package,
            "is_installed": False,
            "is_running": False,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def open_url_on_device(device: str, url: str) -> Dict[str, Any]:
    """
    Open URL in default browser on device
    
    Args:
        device: Target device ID
        url: URL to open
        
    Returns:
        Status dictionary
    """
    try:
        adb_controller.open_url(device, url)
        logger.info(f"Opened URL {url} on device {device}")
        
        return {
            "device": device,
            "url": url,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to open URL: {e}")
        return {
            "device": device,
            "url": url,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def find_image_on_screen(device: str, template_path: str, threshold: float = 0.7) -> Dict[str, Any]:
    """
    Find image template on device screen using template matching
    
    Args:
        device: Target device ID
        template_path: Path to template image file
        threshold: Matching threshold (0.0 to 1.0, default 0.7)
        
    Returns:
        Dictionary containing match coordinates and confidence
    """
    try:
        match_result = adb_controller.find_image_on_screen(device, template_path, threshold)
        
        if match_result:
            x, y = match_result
            return {
                "device": device,
                "template_path": template_path,
                "found": True,
                "x": x,
                "y": y,
                "threshold": threshold,
                "status": "success"
            }
        else:
            return {
                "device": device,
                "template_path": template_path,
                "found": False,
                "x": None,
                "y": None,
                "threshold": threshold,
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Failed to find image on screen: {e}")
        return {
            "device": device,
            "template_path": template_path,
            "found": False,
            "x": None,
            "y": None,
            "threshold": threshold,
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def get_device_info(device: str) -> Dict[str, Any]:
    """
    Get device information and properties
    
    Args:
        device: Target device ID
        
    Returns:
        Dictionary containing device information
    """
    try:
        # Get basic device properties
        properties = {}
        
        prop_commands = {
            "model": "shell getprop ro.product.model",
            "brand": "shell getprop ro.product.brand",
            "version": "shell getprop ro.build.version.release",
            "sdk": "shell getprop ro.build.version.sdk",
            "resolution": "shell wm size",
            "density": "shell wm density"
        }
        
        for prop_name, command in prop_commands.items():
            try:
                result = adb_controller._run_adb_command(command, device, capture_output=True)
                properties[prop_name] = result.strip() if result else "Unknown"
            except:
                properties[prop_name] = "Unknown"
        
        return {
            "device": device,
            "properties": properties,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get device info: {e}")
        return {
            "device": device,
            "properties": {},
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    logger.info("Starting MCP Emulator Controller")
    mcp.run(transport='stdio')