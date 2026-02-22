import { GetInputData, Notify } from "../hook-utils.js";

const skillData = {

}

const main = async () => {
  const inputData = GetInputData();
  const prompt = inputData.prompt;
  const skillSet = new Set();
  for(const key in skillData){
    if(prompt.find(key)){
      skillSet.add(skillData[key]);
    }
  }
  const output = {
    continue: true
  };
  if(skillSet.size > 0){
    const skills = Array.from(skillSet);
    const addPrompt = `${skills.join(", ")} 스킬 참고해줘.`;
    output["systemMessage"] = `키워드 매칭으로 ${skills.join(", ")} 스킬 추가되었습니다.`
    output["hookSpecificOutput"] = {
      hookEventName: inputData.hookEventName,
      additionalContext: addPrompt
    };
  }
  console.log(JSON.stringify(output));
  process.exit(0);
};

main();
