#!/bin/bash
MODEL='GPT'
FEWSHOT=false
MODEL_ID='gpt-4o-2024-05-13'
API_KEY='Your API KEY'
PROMPT_PATH='Path to WeatherQA_test_3_shot_mcq_cls_600.json'
RESULT_PATH=result.json

if [ $MODEL = 'GPT' ]; then
    if $FEWSHOT; then
    echo "Run few-shot GPT Test"
    python scripts/gpt_fewshot_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    else
    echo "Run 0-shot GPT Test"
    python scripts/gpt_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    fi
elif [ $MODEL = 'Gemini' ]; then
    if $FEWSHOT; then
    echo "Run few-shot Gemini Test"
    python scripts/gemini_fewshot_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    else
    echo "Run 0-shot Gemini Test"
    python scripts/gemini_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
    fi
elif [ $MODEL = 'Claude' ]; then
    echo "Run 0-shot Claude Test"
    python scripts/claude3_0601_final.py --input_path $PROMPT_PATH --save_path $RESULT_PATH --model $MODEL_ID --key $API_KEY
else
    echo "Wrong MODEL, Please check the input!"
fi
