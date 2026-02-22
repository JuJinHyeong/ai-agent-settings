import { GetInputData, Notify } from "../hook-utils.js";

const main = async () => {
  const inputData = GetInputData();
  const title = "종료";
  const message = inputData.last_assistant_message;
  await Notify(title, message, true);
  process.exit(0);
}

main();