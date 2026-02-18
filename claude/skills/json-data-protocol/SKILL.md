---
name: json-data-protocol
description: Protocol to get json-data from external tools.
---
### Pipe Name
\\.\pipe\data_service

### request
```json
{
  "action": "get",
  "filepath": "filepath"
}
```

### success response
```json
{
  "result": "success",
  "data": "{\"test\": \"hi\"}"
}
```

### fail response
```json
{
  "result": "error",
  "reason": "error reason"
}
```

### actions
1. get