#!/bin/bash
MODEL='GPT'
FEWSHOT=true
MODEL_ID='gpt-4o-2024-05-13'
# MODEL_ID='gemini-1.5-flash-latest'
# MODEL_ID='claude-3-opus-20240229'
API_KEY='Your API Key'
PROMPT_PATH=/gscratch/ubicomp/cm74/climate/processed_prompt/WeatherQA_test_3_shot_mcq_cls_600.json
RESULT_PATH=/gscratch/ubicomp/cm74/climate/sota_test/results/final.json

if [ $MODEL = 'GPT' ]; then
    if $FEWSHOT; then
    echo "Run few-shot GPT Test"
    python gpt_fewshot_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    else
    echo "Run 0-shot GPT Test"
    python gpt_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    fi
elif [ $MODEL = 'Gemini' ]; then
    if $FEWSHOT; then
    echo "Run few-shot Gemini Test"
    python gemini_fewshot_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    else
    echo "Run 0-shot Gemini Test"
    python gemini_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    fi
elif [ $MODEL = 'Claude' ]; then
    echo "Run 0-shot Claude Test"
    python claude3_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
else
    echo "Wrong MODEL, Please check the input!"
fi
# python gpt_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
# python gpt_fewshot_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY