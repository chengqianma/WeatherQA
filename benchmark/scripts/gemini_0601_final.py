import time
import google.generativeai as genai
import PIL.Image
import os
import json
import argparse
from collections import defaultdict


def format_message(image_list: list, question: str, time: str, area_choices: list, description_map: dict):
    # Define the base structure of the output
    output = []

    # Dictionary to map the abbreviation to its full description
    begnining = f"<Parameters> \n The following {len(image_list)} figures represent weather condition at {time} and each figure contains multiple weather parameters, the most important variable in each figure is provided as follow: "
    end = "</Parameters>"
    output.append(begnining)
    # Iterate through the image list
    for i, image_info in enumerate(image_list):
        # Append the text description for the image
        output.append(description_map[image_info['abbrev']])

        # Append the image data
        output.append(image_info['data'])
    output.append(end)
    
    question = question.format(choice_a=area_choices[0], choice_b=area_choices[1], choice_c=area_choices[2], choice_d=area_choices[3])

    # Append the final question text
    output.append(question)

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
    genai.configure(api_key=opt.key)
    
    with open(input_path, 'r') as file:
        data = json.load(file)
    
    model = genai.GenerativeModel(MODEL,
                            system_instruction=data["sys_prompt"],
                            generation_config={"response_mime_type": "application/json", "temperature":0.1,"max_output_tokens":1024})
    prompt_template = data["zero_shot_prompt_template"]
    para_description = data["para_description"]
    media_type = "image/gif"
    time_sleep = 15
    result = defaultdict(dict)
    for index, sample in enumerate(data["samples"]):
        try:
            img_list = list()
            for img_path in sample["para_paths"]:
                para_name = img_path.split("/")[-1].split('_')[-1].split('.')[0]
                image_data = PIL.Image.open(img_path).convert("RGB")
                img_list.append({
                        'abbrev':para_name,
                        'media_type':media_type,
                        'data':image_data
                    })
            content_in = format_message(img_list, prompt_template, sample["time"], sample["choices"], para_description)
            response = model.generate_content(content_in)

            response_content = response.text
            answer = json.loads(response_content[:response_content.rfind("}") + 1])
            
            print(index, answer)
            time.sleep(time_sleep)

            result[sample["md_id"]]["area_pred"] = answer['Area_Affected']
            result[sample["md_id"]]["area_gt"] = sample["area_ans"]
            result[sample["md_id"]]["concern_pred"] = answer['Concerning']
            result[sample["md_id"]]["concern_gt"] = sample["concern_ans"]

            with open(save_path, 'w') as file:
                # Write text to the file
                json.dump(result, file, indent=4)

        except Exception as e:
            print(f"{e}")