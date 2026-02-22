import { WindowsToaster } from "node-notifier"
import fs from "fs"
import lineReader from "reverse-line-reader"

// 함수가 Promise를 반환하도록 변경
export const GetLastMessage = (filePath, defaultMessage) => {
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
export const Notify = (title, message, mobile) => {
  const toastPromise = new Promise((resolve) => {
    const notifier = new WindowsToaster({ withFallback: false });
    notifier.notify({
      title,
      message,
      appID: process.env.APP_ID || "Anthropic.Claude.Code",
      icon: process.env.ICON_PATH,
      sound: true,
    }, (error, response) => {
      if (error) console.error("오류:", error);
      else console.log("성공:", response);
      resolve();
    });
  });

  const mobilePromise = mobile
    ? (() => {
        const encodedTitle =
          "=?utf-8?B?" + Buffer.from(title, "utf-8").toString("base64") + "?=";
        return fetch(process.env.NTFY_URL, {
          method: "POST",
          body: message,
          headers: { Title: encodedTitle },
        })
          .then((res) => console.log("모바일 알림 전송 성공:", res))
          .catch((err) => {
            fs.appendFileSync(
              "error.log",
              `${new Date().toISOString()} - 모바일 알림 전송 실패: ${err}\n`
            );
            console.error("모바일 알림 전송 실패:", err);
          });
      })()
    : Promise.resolve();

  return Promise.all([toastPromise, mobilePromise]);
};

export const GetInputData = () => {
  const input = fs.readFileSync(0, "utf-8");
  const inputData = input ? JSON.parse(input) : {};
  return inputData;
}