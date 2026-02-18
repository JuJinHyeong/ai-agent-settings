const WindowsToaster = require("node-notifier").WindowsToaster;
const fs = require("fs");
const path = require("path");
const lineReader = require("reverse-line-reader");
require("dotenv").config({ path: path.join(__dirname, ".env"), quiet: true });

// 함수가 Promise를 반환하도록 변경
const GetLastMessage = (filePath, defaultMessage) => {
  return new Promise((resolve, reject) => {
    // 파일이 없으면 즉시 기본값 반환
    if (!fs.existsSync(filePath)) {
      return resolve(defaultMessage);
    }

    lineReader.eachLine(filePath, (line, last) => {
      try {
        // 빈 라인 방어
        if (!line || line.trim() === "") {
          if (last) resolve(defaultMessage); // 파일 끝인데 못 찾음
          return true; // 계속 읽기
        }

        const data = JSON.parse(line);
        const message = data.message;

        if (!message) {
          if (last) resolve(defaultMessage);
          return true;
        }

        const content = message.content;
        if (!content || !Array.isArray(content) || content.length === 0) {
          if (last) resolve(defaultMessage);
          return true;
        }

        const text = content[0].text ? content[0].text.trim() : "";

        // 유효한 텍스트를 찾았을 때
        if (text) {
          resolve(text); // Promise 완료 (값 찾음)
          return false; // 읽기 중단 (Stop loop)
        }
      } catch (err) {
        // JSON 파싱 에러 등은 무시하고 다음 줄로 진행
        console.error("Line parsing error:", err);
      }

      // 파일의 끝까지 왔는데도 유효한 메시지를 못 찾은 경우
      if (last) {
        resolve(defaultMessage);
      }

      return true; // 계속 읽기
    });
  });
};

const Notify = (title, message, mobile) => {
  const notifier = new WindowsToaster({
    withFallback: false,
  });
  notifier.notify(
    {
      title: title,
      message: message,
      appID: process.env.APP_ID, // 또는 "Claude Code"
      icon: process.env.ICON_PATH, // 아이콘 경로
      sound: true,
    },
    (error, response) => {
      if (error) {
        console.error("오류:", error);
      } else {
        console.log("성공:", response);
      }
    },
  );
  if (mobile) {
    const encodedTitle =
      "=?utf-8?B?" + Buffer.from(title, "utf-8").toString("base64") + "?=";
    fetch(process.env.NTFY_URL, {
      method: "POST",
      body: message,
      headers: {
        Title: encodedTitle,
      },
    })
      .then((res) => {
        console.log("모바일 알림 전송 성공:", res);
      })
      .catch((err) => {
        fs.writeFileSync(
          "error.log",
          `${new Date().toISOString()} - 모바일 알림 전송 실패: ${err}\n`,
          { flag: "a" },
        );
        console.error("모바일 알림 전송 실패:", err);
      });
  }
};

const PermissionRequestNotify = (inputData) => {
  const toolName = inputData.tool_name;
  const title = "권한 요청";
  const message = `도구 "${toolName}" 사용 권한이 요청되었습니다.`;
  Notify(title, message, true);
};

const StopNotify = async (inputData) => {
  const title = "작업 중지";
  const message = await GetLastMessage(
    inputData.transcript_path,
    "작업이 중지되었습니다.",
  );
  Notify(title, message, true);
};

const SubagentStartNotify = (inputData) => {
  const subAgentType = inputData.agent_type;
  const title = "서브 에이전트 시작";
  const message = `서브 에이전트 ${subAgentType}가 시작되었습니다.`;
  Notify(title, message, true);
};

const SubagentStopNotify = (inputData) => {
  const subAgentType = inputData.agent_type;
  if (!subAgentType) {
    return;
  }
  const title = "서브 에이전트 종료";
  const message = `서브 에이전트 ${subAgentType}가 종료되었습니다.`;
  Notify(title, message, true);
};

const TaskCompletedNotify = (inputData) => {
  const taskName = inputData.task_subject;
  const taskDescription = inputData.task_description;
  const title = `작업 완료: ${taskName}`;
  const message = taskDescription;
  Notify(title, message, true);
};

const PrecompactNotify = (inputData) => {
  const title = "대화 압축 시작";
  const message = "대화 압축이 시작되었습니다.";
  Notify(title, message, true);
};

const main = async () => {
  const input = fs.readFileSync(0, "utf-8");
  const inputData = input ? JSON.parse(input) : {};
  const hookEventName = inputData.hook_event_name;
  if (hookEventName === "PermissionRequest") {
    PermissionRequestNotify(inputData);
  } else if (hookEventName === "Stop") {
    await StopNotify(inputData);
  } else if (hookEventName === "SubagentStart") {
    SubagentStartNotify(inputData);
  } else if (hookEventName === "SubagentStop") {
    SubagentStopNotify(inputData);
  } else if (hookEventName === "TaskCompleted") {
    TaskCompletedNotify(inputData);
  } else if (hookEventName === "PreCompact") {
    PrecompactNotify(inputData);
  }
};

main();
