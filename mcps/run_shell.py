from fastmcp import FastMCP
import subprocess

mcp = FastMCP("run-shell")

@mcp.tool()
def run_powershell(command: str) -> str:
    """
    PowerShell 명령어를 실행하고 결과를 반환합니다.

    Args:
        command: 실행할 PowerShell 명령어 (예: "Get-Process")

    Returns:
        PowerShell 명령어의 실행 결과
    """
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True, encoding="utf-8")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    
@mcp.tool()
def run_cmd(command: str) -> str:
    """
    CMD 명령어를 실행하고 결과를 반환합니다.

    Args:
        command: 실행할 CMD 명령어 (예: "dir")

    Returns:
        CMD 명령어의 실행 결과
    """
    try:
        result = subprocess.run(["cmd", "/c", command], capture_output=True, text=True, shell=True, check=True, encoding="utf-8")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    
@mcp.tool()
def run_bash(command: str) -> str:
    """
    Bash 명령어를 실행하고 결과를 반환합니다.

    Args:
        command: 실행할 Bash 명령어 (예: "ls -la")

    Returns:
        Bash 명령어의 실행 결과
    """
    try:
        result = subprocess.run(["bash", "-c", command], capture_output=True, text=True, check=True, encoding="utf-8")
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run()