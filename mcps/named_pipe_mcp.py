from fastmcp import FastMCP
import ctypes
import ctypes.wintypes
import os

mcp = FastMCP("windows-named-pipe")

kernel32 = ctypes.windll.kernel32

# Windows API 상수 (클라이언트 전용)
GENERIC_READ         = 0x80000000
GENERIC_WRITE        = 0x40000000
OPEN_EXISTING        = 3
INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value


def _pipe_path(name: str) -> str:
    """파이프 이름을 전체 경로로 변환합니다."""
    if name.startswith(r'\\.\pipe'):
        return name
    return rf'\\.\pipe\{name}'


@mcp.tool()
def pipe_send(pipe_name: str, message: str, encoding: str = "utf-8", read_response: bool = True, timeout_ms: int = 5000) -> str:
    """
    Named Pipe 클라이언트: 파이프 서버에 연결하여 메시지를 전송하고 응답을 받습니다.

    Args:
        pipe_name: 파이프 이름 (예: "mypipe") 또는 전체 경로 (\\\\.\pipe\mypipe)
        message: 전송할 메시지 문자열
        encoding: 인코딩 (기본값: utf-8)
        read_response: True이면 서버 응답을 읽어서 반환
        timeout_ms: 파이프가 열릴 때까지 대기할 타임아웃 (밀리초)

    Returns:
        서버 응답 문자열 또는 성공/오류 메시지
    """
    pipe_path = _pipe_path(pipe_name)

    # 파이프가 준비될 때까지 대기
    if not kernel32.WaitNamedPipeW(pipe_path, timeout_ms):
        err = kernel32.GetLastError()
        return f"[Error] 파이프 대기 실패 (파이프 없음 또는 타임아웃). GetLastError={err}"

    handle = kernel32.CreateFileW(
        pipe_path,
        GENERIC_READ | GENERIC_WRITE,
        0, None, OPEN_EXISTING, 0, None
    )
    if handle == INVALID_HANDLE_VALUE:
        err = kernel32.GetLastError()
        return f"[Error] 파이프 연결 실패. GetLastError={err}"

    try:
        data = message.encode(encoding)
        bytes_written = ctypes.wintypes.DWORD(0)
        ok = kernel32.WriteFile(handle, data, len(data), ctypes.byref(bytes_written), None)
        if not ok:
            err = kernel32.GetLastError()
            return f"[Error] 메시지 전송 실패. GetLastError={err}"

        if not read_response:
            return f"Success: {bytes_written.value} 바이트 전송 완료"

        buf = ctypes.create_string_buffer(65536)
        bytes_read = ctypes.wintypes.DWORD(0)
        ok = kernel32.ReadFile(handle, buf, ctypes.sizeof(buf), ctypes.byref(bytes_read), None)
        if not ok:
            err = kernel32.GetLastError()
            return f"[Error] 응답 읽기 실패. GetLastError={err}"

        return buf.raw[:bytes_read.value].decode(encoding, errors='replace')

    finally:
        kernel32.CloseHandle(handle)


@mcp.tool()
def pipe_write_only(pipe_name: str, message: str, encoding: str = "utf-8", timeout_ms: int = 5000) -> str:
    """
    Named Pipe에 단방향으로 메시지만 전송합니다 (응답 수신 없음).
    응답을 기다리지 않는 fire-and-forget 방식입니다.

    Args:
        pipe_name: 파이프 이름 또는 전체 경로
        message: 전송할 메시지
        encoding: 인코딩 (기본값: utf-8)
        timeout_ms: 파이프 대기 타임아웃 (밀리초)

    Returns:
        성공 메시지 또는 오류 메시지
    """
    return pipe_send(pipe_name, message, encoding=encoding, read_response=False, timeout_ms=timeout_ms)


@mcp.tool()
def pipe_list() -> str:
    """
    현재 시스템에 존재하는 모든 Named Pipe 목록을 반환합니다.

    Returns:
        파이프 이름 목록 (줄바꿈 구분), 없으면 안내 메시지
    """
    try:
        pipes = os.listdir(r'\\.\pipe')
        if not pipes:
            return "사용 가능한 Named Pipe가 없습니다."
        return "\n".join(sorted(pipes))
    except Exception as e:
        return f"[Error] 파이프 목록 조회 실패: {str(e)}"


@mcp.tool()
def pipe_exists(pipe_name: str) -> str:
    """
    지정한 Named Pipe가 현재 존재하는지 확인합니다.

    Args:
        pipe_name: 파이프 이름 (예: "mypipe") 또는 전체 경로

    Returns:
        "exists" 또는 "not found"
    """
    name = pipe_name
    if name.startswith(r'\\.\pipe\\') or name.startswith(r'\\.\pipe/'):
        name = name.split('\\')[-1].split('/')[-1]
    elif name.startswith(r'\\.\pipe'):
        name = name[len(r'\\.\pipe'):]
        name = name.lstrip('\\/')

    try:
        pipes = os.listdir(r'\\.\pipe')
        return "exists" if name in pipes else "not found"
    except Exception as e:
        return f"[Error] 확인 실패: {str(e)}"


if __name__ == "__main__":
    mcp.run()
