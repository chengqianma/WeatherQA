import anthropic
import base64
import json
import time
import argparse
from collections import defaultdict


def format_message(image_list: list, question: str, time: str, area_choices: list, description_map: dict):
    # Define the base structure of the output
    output = []

    begnining = f"<Parameters> \n The following {len(image_list)} figures represent weather condition at {time} and each figure contains multiple weather parameters, the most important variable in each figure is provided as follow: "
    end = "</Parameters>"
    output.append({
      "type": "text",
            "text": begnining
    })
    # Iterate through the image list
    for i, image_info in enumerate(image_list):
        # Append the text description for the image
        output.append({
            "type": "text",
            "text": f"{description_map[image_info['abbrev']]}"
        })

        # Append the image data
        output.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_info['media_type'],
                "data": image_info['data']
            }
        })
    output.append({
        "type": "text",
        "text": end
    })

    question = question.format(choice_a=area_choices[0], choice_b=area_choices[1], choice_c=area_choices[2], choice_d=area_choices[3])

    # Append the final question text
    output.append({
        "type": "text",
        "text": question
    })

    return output


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="settings")
    parser.add_argument("-s", "--save_path", type=str, default="./tmp_data", help="output results file path")
    parser.add_argument("-i", "--input_path", type=str, default="./tmp_data", help="input prompt file path")
    parser.add_argument("-m", "--model", type=str, default="gpt-4o-2024-05-13", help="model id")
    parser.add_argument("-k", "--key", type=str, default="", help="api key")

    opt = parser.parse_args()
    save_path = opt.save_path
    input_path = opt.input_path
    MODEL = opt.model
    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=opt.key,
    )
    with open(input_path, 'r') as file:
        data = json.load(file)
    
    time_sleep = 15
    sys_prompt = data["sys_prompt"]
    prompt_template = data["zero_shot_prompt_template"]
    para_description = data["para_description"]
    media_type = "image/gif"
    result = defaultdict(dict)
    for index, sample in enumerate(data["samples"]):
        try:
            img_list = list()
            for img_path in sample["para_paths"]:
                para_name = img_path.split("/")[-1].split('_')[-1].split('.')[0]
                with open(img_path, 'rb') as image_file:
                    img = image_file.read()
                    image_data = base64.b64encode(img).decode('utf-8')
                    img_list.append({
                    'abbrev':para_name,
                    'media_type':media_type,
                    'data':image_data
                    })

            prompt = format_message(img_list, prompt_template, sample["time"], sample["choices"], para_description)
        
            message = client.messages.create(
                    model=MODEL,
                    max_tokens=40,
                    temperature=0.1,
                    system=sys_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        },
                        {
                            "role": "assistant",
                            "content": "Here is the JSON requested:\n{"
                        }
                    ],
                    )
            message_content = message.content[0].text
            retrieved_answer = json.loads("{" + message_content[:message_content.rfind("}") + 1])
            print(index, retrieved_answer)
            time.sleep(time_sleep)
            result[sample["md_id"]]["area_pred"] = retrieved_answer['Area_Affected']
            result[sample["md_id"]]["area_gt"] = sample["area_ans"]
            result[sample["md_id"]]["concern_pred"] = retrieved_answer['Concerning']
            result[sample["md_id"]]["concern_gt"] = sample["concern_ans"]
            with open(save_path, 'w') as file:
                # Write text to the file
                json.dump(result, file, indent=4)

        except Exception as e:
                print(f"{e}")
