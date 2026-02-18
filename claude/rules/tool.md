# tool use rules
## File Operations
- If a file cannot be read or appears corrupted due to encoding issues, use the mcp file-handler to ensure proper data recovery.

## Named Pipe Communication (Transport & Protocol)
### Transport
Use the named-pipe-mcp as the primary communication layer for interacting with external Windows applications.

### Protocol & Logic
Before sending any message, strictly follow the protocol definitions (message formats, commands, and sequences) described in the "Skill" or "Tool Description" section of the target tool.

### Verification
Use pipe_list or pipe_exists to identify the correct pipe name as defined in the target tool's specifications before initiating a connection.

### Message Format
Every Protocol must be JSON Format.