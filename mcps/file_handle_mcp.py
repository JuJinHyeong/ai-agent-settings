from fastmcp import FastMCP
import os
from itertools import islice
from concurrent.futures import ThreadPoolExecutor
from typing import List
import chardet

mcp = FastMCP("file-handler-with-encoding")

@mcp.tool()
def get_file_encoding(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        # Read a reasonable portion of the file (or the whole file for better accuracy)
        raw_data = f.read(20000) # Read first 1KB for analysis
        result = chardet.detect(raw_data)
        return result['encoding']

@mcp.tool()
def count_total_lines(file_path: str, encoding: str) -> int:
    """파일의 전체 줄 수를 셉니다 (메타데이터 제공용)"""
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return -1

@mcp.tool()
def read_file_with_encoding(file_path: str, start_line: int = 1, num_lines: int = 50, encoding: str = "utf-8") -> str:
    """
    Args:
        file_path: 파일 경로
        start_line: 시작 줄 번호 (1부터 시작)
        num_lines: 읽을 줄의 개수
        force_encoding: 강제 지정할 인코딩
    """
    if not os.path.exists(file_path):
        return f"[Error] 파일이 존재하지 않습니다: {file_path}"

    try:
        lines_content = []
        start_index = max(0, start_line - 1)
        end_index = start_index + num_lines

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            target_lines = islice(f, start_index, end_index)
            for line in target_lines:
                lines_content.append(line.rstrip())
        body = "\n".join(lines_content)
        return body

    except UnicodeDecodeError:
        return f"[Error] '{encoding}' 인코딩 디코딩 실패."
    except Exception as e:
        return f"[Error] 읽기 실패: {str(e)}"

@mcp.tool()
def write_file_with_encoding(file_path: str, content: str, target_encoding: str = 'utf-8') -> str:
    """
    내용을 지정된 인코딩과 Windows 스타일 줄바꿈(\r\n)으로 저장합니다.
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w', encoding=target_encoding, errors='replace', newline='\r\n') as f:
            f.write(content)
            
        return f"Success"

    except UnicodeEncodeError as e:
        return f"[Error] 인코딩 변환 실패: {str(e)}"
    except Exception as e:
        return f"[Error] 파일 저장 실패: {str(e)}"
   
@mcp.tool() 
def replace_text_with_encoding(file_path: str, old_text: str, new_text: str, encoding: str = "utf-8") -> str:
    """
    파일 내의 특정 텍스트를 다른 텍스트로 교체합니다.

    Args:
        file_path: 파일 경로
        old_text: 교체할 기존 텍스트
        new_text: 새로 대체할 텍스트
        encoding: 파일 인코딩
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        if old_text not in content:
            return "No Match"
        updated_content = content.replace(old_text, new_text)

        with open(file_path, 'w', encoding=encoding, errors='replace', newline='\r\n') as f:
            f.write(updated_content)

        return "Success"

    except Exception as e:
        return f"[Error] 텍스트 교체 실패: {str(e)}"

@mcp.tool()
def search_in_file_with_encoding(file_path: str, search_text: str, encoding: str = "utf-8") -> str:
    """
    개별 파일 내에서 특정 텍스트를 검색하여 포맷팅된 문자열로 반환합니다.
    Format:
      file: {filename}
      {line_num}: {content}
      ...
    """
    matches = []
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                if search_text in line:
                    matches.append(f"{line_num}:{line.strip()}")
    except Exception as e:
        return f"file: {file_path}\nError: {str(e)}"
    
    if matches:
        # 파일명 헤더와 매치된 라인들을 줄바꿈으로 연결
        return f"file: {file_path}\n" + "\n".join(matches)
    
    return ""

@mcp.tool()
def search_in_dir_with_encoding(root_dir: str, search_text: str, extensions: List[str], encoding: str = "utf-8") -> str:
    """
    프로젝트 폴더 내 지정된 확장자 파일들을 8개 스레드로 검색하여 결과를 문자열로 합칩니다.
    """
    target_files = []
    
    # 1. 검색 대상 파일 수집
    for root, dirs, files in os.walk(root_dir):
        # 제외할 폴더
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                target_files.append(os.path.join(root, file))
    
    # 2. 병렬 처리 및 결과 수집
    results = []
    total_line_count = 0  # 출력량 제한을 위한 라인 수 카운트

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(search_in_file_with_encoding, f, search_text, encoding) for f in target_files]
        
        for future in futures:
            res = future.result()
            if res:  # 결과가 빈 문자열이 아닌 경우만 추가
                results.append(res)
                
                # 대략적인 라인 수 계산 (파일명 줄 + 내용 줄 수)
                total_line_count += res.count('\n') + 1
            
            # 결과가 너무 많으면 중단 (약 100줄 기준)
            if total_line_count >= 100:
                # 남은 작업 취소 시도 (Python 3.9+ 에서는 cancel_futures=True 사용 가능)
                executor.shutdown(wait=False, cancel_futures=True)
                results.append("\n...Output Truncated Too Many Results...")
                break

    return "\n".join(results) if results else "No Match"

if __name__ == "__main__":
    mcp.run()