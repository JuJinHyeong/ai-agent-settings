import { GetInputData, Notify } from "../hook-utils.js";

const main = async () => {
  const inputData = GetInputData();
  let title = "알림";
  const message = inputData.message || "메시지";
  const notiType = inputData.notification_type;
  if (notiType === "permission_prompt"){
    title = "권한 요청";
  }
  else if(notiType === "idle_prompt") {
    title = "입력 대기";
  }
  else if(notiType === "auth_success"){
    title = "인증 성공";
  }
  else if(notiType === "elicitation_dialog"){
    title = "MCP 도구 추출";
  }
  await Notify(title, message, true);
  process.exit(0);
}
main();