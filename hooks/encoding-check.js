const fs = require('fs');
const path = require('path');
const chardet = require('chardet');

const PreToolUseEncodingCheck = async (inputData) => {
    const toolName = inputData.tool_name;
    const toolInput = inputData.tool_input;
    if(toolName === "Read"){
        const filePath = toolInput.file_path;
        const encoding = await chardet.detectFile(filePath);
        if(encoding !== "UTF-8"){
            const output = {
                "decision": "deny",
                "reason": "file encoding is EUC-KR. Use Read mcp Server.",
                "suppressOutput": true  // Don't show in verbose mode
            }
            console.log(JSON.stringify(output));
        }
    }
    else if(toolName === "Write"){
        const filePath = toolInput.file_path;
        const ext = path.extname(filePath); // 파일 확장자 추출 (예: .txt, .md)
        if(ext === ".cpp" || ext === ".h"){
            const output = {
                "decision": "deny",
                "reason": "cpp/h file must be written in EUC-KR encoding. Use Write mcp Server.",
                "suppressOutput": true  // Don't show in verbose mode
            }
            console.log(JSON.stringify(output));
        }
    }
}

const main = async () => {
    const input = fs.readFileSync(0, 'utf-8');
    const inputData = input ? JSON.parse(input) : {};
    const hookEventName = inputData.hook_event_name;
    if(hookEventName === "PreToolUse"){
        PreToolUseEncodingCheck(inputData);
    }
    exit(0);
}

main();