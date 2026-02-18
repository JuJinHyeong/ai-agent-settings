import json
from fastmcp import FastMCP
import ctypes
import ctypes.wintypes
import os

mcp = FastMCP("windows-named-pipe")

kernel32 = ctypes.windll.kernel32

# Windows API Constants
GENERIC_READ         = 0x80000000
GENERIC_WRITE        = 0x40000000
OPEN_EXISTING        = 3
INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value

def _pipe_path(name: str) -> str:
    """Normalize pipe name to full Windows path format."""
    clean_name = name.replace("/", "\\").strip()
    
    if clean_name.startswith(r"\\.\pipe"):
        return clean_name
    
    clean_name = clean_name.lstrip("\\")
    return rf"\\.\pipe\{clean_name}"

@mcp.tool()
def pipe_send(pipe_name: str, message: str, read_response: bool = True, timeout_ms: int = 5000) -> str:
    """
    Named Pipe Client: Validates JSON and sends message via UTF-8.

    Args:
        pipe_name: Name of the pipe (e.g., "mypipe")
        message: JSON string to send (UTF-8)
        read_response: Whether to wait for a server response
        timeout_ms: Timeout for waiting for the pipe to become available
    """
    # 1. JSON Validation
    try:
        json.loads(message)
    except json.JSONDecodeError as e:
        return f"[ValidationError] Invalid JSON format: {str(e)}"

    pipe_path = _pipe_path(pipe_name)

    # 2. Wait for the pipe to be available
    if not kernel32.WaitNamedPipeW(pipe_path, timeout_ms):
        err = kernel32.GetLastError()
        return f"[Error] Pipe wait failed. Target not found or timed out. (Code: {err})"

    # 3. Open the pipe
    handle = kernel32.CreateFileW(
        pipe_path,
        GENERIC_READ | GENERIC_WRITE,
        0, None, OPEN_EXISTING, 0, None
    )

    if handle == INVALID_HANDLE_VALUE:
        return f"[Error] Failed to connect to pipe. (Code: {kernel32.GetLastError()})"

    try:
        # 4. Send message (UTF-8)
        data = message.encode("utf-8")
        bytes_written = ctypes.wintypes.DWORD(0)
        
        if not kernel32.WriteFile(handle, data, len(data), ctypes.byref(bytes_written), None):
            return f"[Error] Message transmission failed. (Code: {kernel32.GetLastError()})"

        # Ensure data is flushed to the server
        kernel32.FlushFileBuffers(handle)

        if not read_response:
            return f"Success: {bytes_written.value} bytes sent."

        # 5. Receive response (UTF-8)
        buf = ctypes.create_string_buffer(65536)
        bytes_read = ctypes.wintypes.DWORD(0)
        
        if not kernel32.ReadFile(handle, buf, ctypes.sizeof(buf), ctypes.byref(bytes_read), None):
            return f"[Error] Failed to read response. (Code: {kernel32.GetLastError()})"

        return buf.raw[:bytes_read.value].decode("utf-8", errors='replace')

    finally:
        kernel32.CloseHandle(handle)

@mcp.tool()
def pipe_write_only(pipe_name: str, message: str, timeout_ms: int = 5000) -> str:
    """Sends a one-way message to the Named Pipe (Fire-and-forget)."""
    return pipe_send(pipe_name, message, read_response=False, timeout_ms=timeout_ms)

@mcp.tool()
def pipe_list() -> str:
    """Returns a list of all currently available Named Pipes in the system."""
    try:
        pipes = os.listdir(r'\\.\pipe')
        return "\n".join(sorted(pipes)) if pipes else "No Named Pipes available."
    except Exception as e:
        return f"[Error] Failed to list pipes: {str(e)}"

@mcp.tool()
def pipe_exists(pipe_name: str) -> str:
    """Checks if a specific Named Pipe exists."""
    pipe_path = _pipe_path(pipe_name)
    target = pipe_path.split("\\")[-1]

    try:
        pipes = os.listdir(r'\\.\pipe')
        return "exists" if target in pipes else "not found"
    except Exception as e:
        return f"[Error] Check failed: {str(e)}"

if __name__ == "__main__":
    mcp.run()