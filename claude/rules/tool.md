# tool use rules
## File Operations
- If a file cannot be read or appears corrupted due to encoding issues, use the mcp file-handler to ensure proper data recovery.

## Shell Operations
- If the output of a shell command is corrupted or unreadable due to encoding issues (e.g., broken characters), re-execute the command using the mcp run-shell tool to ensure proper character decoding and output integrity.

## Image Processing
- For any queries involving image identification, analysis, or manipulation, delegate the task to the Gemini CLI subagent.
- Getmini CLI subagent should be the primary tool for interpreting visual data or executing complex image-related workflows.

## Named Pipe Communication (Transport & Protocol)
### Transport
- Use the named-pipe-mcp as the primary communication layer for interacting with external Windows applications.

### Protocol & Logic
- Before sending any message, strictly follow the protocol definitions (message formats, commands, and sequences) described in the "Skill" or "Tool Description" section of the target tool.

### Verification
- Use pipe_list or pipe_exists to identify the correct pipe name as defined in the target tool's specifications before initiating a connection.

### Message Format
- Every Message must be JSON Format.
- Send Format: `{"action": "action_id", ...params }`
- Success Response Format: `{"result": "success", "value": "data"}`
- Failed Response Format: `{"result": "error", "reason": "reason"}`
