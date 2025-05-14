import base64
from mcp.server.fastmcp import FastMCP, Image
from adbfunc import ADB
from PIL import Image as PILImage
# Initialize FastMCP server
mcp = FastMCP("MCPEmulatorController")

adb = ADB()

@mcp.tool()
async def get_devices(isMuMu: bool = False, pathMuMu: str = "D:\\MuMuPlayerGlobal-12.0"):
    """
    Get list of devices connected from MumuEmulator or ADB

    if use MumuEmulator, set isMuMu = True and pathMuMu = path to MumuEmulator

    isMuMu: bool = False, pathMuMu: str = ""
    example: 
        isMuMu = True, pathMuMu = "D:\\MuMuPlayerGlobal-12.0"
    """
    devices = adb.GetDevices(isMuMu, pathMuMu)
    return {"devices": devices, "status": "success"}

@mcp.tool()
async def reload_server():
    """
    Reload ADB server
    """
    adb.ReloadServer()
    return {"status": "success"}

@mcp.tool()
async def open_tcp(device: str, port: int):
    """
    Open TCP port
    """
    adb.OpenTCP(device, port)
    return {"device": device, "port": port, "status": "success"}

@mcp.tool()
async def get_allpackage(device: str):
    """
    Get all package name from device
    """
    return {"packages": adb.GetPackageNames(device), "device": device, "status": "success"}

@mcp.tool()
async def open_app(device: str, package: str):
    """
    Open app from package name
    """
    adb.OpenApp(device, package)
    return {"status": "success"}

@mcp.tool()
async def stop_app(device: str, package: str):
    """
    Stop app from package name
    """
    adb.StopApp(device, package)
    return {"package": package, "device": device, "status": "success"}

@mcp.tool()
async def tap(device: str, x: int, y: int):
    """
    Tap on device with coordinate
    """
    adb.Click(device, x, y)
    return {"device": device, "x": x, "y": y, "status": "success"}

@mcp.tool()
async def swipe(device: str, x1: int, y1: int, x2: int, y2: int, duration: int = 1000):
    """
    Swipe on device with coordinate
    """
    adb.Swipe(device, x1, y1, x2, y2, duration)
    return {"device": device, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "duration": duration, "status": "success"}

@mcp.tool()
async def screen_capture(device: str):
    """
    Screen capture from device
    """
    image = adb.ScreenCaptureSave(device)
    img = PILImage.open(image)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

if __name__ == "__main__":
    mcp.run(transport='stdio')