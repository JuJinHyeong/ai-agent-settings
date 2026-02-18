---
name: tool-protocol
description: 툴을 사용할 때 사용할 named pipe의 프로토콜이다. 툴과의 통신을 위해서 사용한다.
---
Tool Skill: Data Management Protocol
이 섹션은 Named Pipe를 통해 외부 데이터 관리 시스템과 통신하는 규칙을 정의합니다.

1. Connection Info
Pipe Name: \\.\pipe\data_service

Encoding: utf-8

2. Message Format (JSON)
모든 통신은 JSON 문자열로 이루어지며, 다음 형식을 준수해야 합니다.

A. 데이터 조회 (get_data)
저장된 특정 키의 값을 요청합니다.

Request: {"action": "get_data", "key": "string"}

Success Response: {"status": "success", "value": "any"}

Error Response: {"status": "error", "message": "reason"}