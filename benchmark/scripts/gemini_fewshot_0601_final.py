import time
import google.generativeai as genai
import PIL.Image
import os
import json
import argparse
from collections import defaultdict


def encode_example(weather_parameters: list[str], mcq: list[str], area_ans: int, concerning_ans: str, example_id: int, hint=None) ->  list[str]:
    assert len(mcq) == 4, 'the length of multiple choice is set to 4'
    mapping = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H", 8: "I", 9: "J", 10: "K", 11: "L", 12: "M"}
    q1_options = f"""
        <Question 1 Options>
          <Option value='A'>{mcq[0]}</Option>s
          <Option value='B'>{mcq[1]}</Option>
          <Option value='C'>{mcq[2]}</Option>
          <Option value='D'>{mcq[3]}</Option>
        </Question 1 Options>
        """
    example_answers = f"""
      <Question 1 answer>{mapping[area_ans]}</Question 1 answer>
      <Question 2 answer>{mapping[concerning_ans]}</Question 2 answer>
    """
    example_block = []
    example_block.append(f'<Example {example_id}>\n')
    example_block += weather_parameters
    example_block.append(q1_options)
    if hint is not None:
      example_block.append(f'<Hint>{hint}</Hint>')
    example_block.append(example_answers)
    example_block.append(f'</Example {example_id}>\n')

    return example_block


def encode_question(weather_parameters: list[str], mcq: list[str],) -> list[str]:
    assert len(mcq) == 4, 'the length of multiple choice is set to 4'
    problem_block = []
    q1_options = f"""
        <Question 1 Options>
          <Option value='A'>{mcq[0]}</Option>
          <Option value='B'>{mcq[1]}</Option>
          <Option value='C'>{mcq[2]}</Option>
          <Option value='D'>{mcq[3]}</Option>
        </Question 1 Options>
        """
    answers = f"""
    <Question 1 answer>Option</Question 1 answer>
    <Question 2 answer>Option</Question 2 answer>
    """
    problem_block.append('<Problem>\n')
    problem_block+=weather_parameters
    problem_block.append(q1_options)
    problem_block.append(answers)
    problem_block.append('</Problem>')
    return problem_block

def image_description(image_list: list, time: str, description_map: dict):
    # Define the base structure of the output
    output = []

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
    prompt_template = data["few_shot_prompt_template"]
    para_description = data["para_description"]
    media_type = "image/gif"
    time_sleep = 30
    result = defaultdict(dict)
    for index, sample in enumerate(data["samples"]):
        try:
            img_list = list()
            final_prompt = [prompt_template]
            for img_path in sample["para_paths"]:
                para_name = img_path.split("/")[-1].split('_')[-1].split('.')[0]
                image_data = PIL.Image.open(img_path).convert("RGB")
                img_list.append({
                        'abbrev':para_name,
                        'media_type':media_type,
                        'data':image_data
                    })
            
            parameter_question = image_description(img_list, sample["time"], para_description)
            prompt_question = encode_question(parameter_question, sample["choices"])
            for example_index, example_md in enumerate(sample["examples"]):
                example_img_list = list()
                for img_path in example_md["para_paths"]:
                    para_name = img_path.split("/")[-1].split('_')[-1].split('.')[0]
                    image_data = PIL.Image.open(img_path).convert("RGB")
                    example_img_list.append({
                        'abbrev':para_name,
                        'media_type':media_type,
                        'data':image_data
                    })

                parameter_example = image_description(example_img_list, example_md["time"], para_description)
                prompt_example = encode_example(parameter_example, example_md["choices"], example_md["area_ans"], example_md["concern_ans"], example_index + 1)
                final_prompt += prompt_example
            
            final_prompt.append('</Examples>')
            final_prompt += prompt_question

            response = model.generate_content(final_prompt)

            response_content = response.text
            answer = json.loads(response_content[:response_content.rfind("}") + 1])
            print(index, answer)
            time.sleep(time_sleep)     
            result[sample["md_id"]]["area_pred"] = answer['Area_Affected']
            result[sample["md_id"]]["concern_pred"] = answer['Concerning']
            result[sample["md_id"]]["area_gt"] = sample["area_ans"]
            result[sample["md_id"]]["concern_gt"] = sample["concern_ans"]
            with open(save_path, 'w+') as file:
                # Write text to the file
                json.dump(result, file, indent=4)
        
        except Exception as e:
            print(f"{e}")
