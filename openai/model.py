import time
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

prompt_template = """
Write a PRD for Spotify's Discover Weekly feature. 
Discover Weekly is a personalised playlist of 30 songs 
generated every Monday based on a user's listening 
history, saved songs, and listening behaviour of users 
with similar taste.

Include the following sections:
1. Problem Statement
2. Overarching Goal
3. User Persona
5. Functional Requirements
6. Non-Functional Requirements  
7. Success Metrics

Be specific, detailed, and grounded. Avoid generic 
statements. Every requirement should be testable and 
every metric should be measurable.

"""


client = OpenAI()

def run_openai():
    start_time = time.time()
    first_token_time = None
    output_tokens = 0
    input_tokens = 0
    full_response = ""

    stream = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {"role": "user", "content": prompt_template}
        ],
        stream=True,
        stream_options={"include_usage": True}
    )

    for chunk in stream:
        if chunk.usage:
            input_tokens = chunk.usage.prompt_tokens
            output_tokens = chunk.usage.completion_tokens

        if chunk.choices and chunk.choices[0].delta.content:
            if first_token_time is None:
                first_token_time = time.time()
            content = chunk.choices[0].delta.content
            full_response += content

    end_time = time.time()

    #time to first token
    ttft = first_token_time - start_time
    #how long it took to finish writing the response from start
    #e2e latency
    total_latency = end_time - start_time
    #tokens per second
    tps = output_tokens / total_latency
    total_tokens = input_tokens + output_tokens

    return {
        "model": "gpt-5.4",
        "ttft": round(ttft, 3),
        "total_latency": round(total_latency, 3),
        "tps": round(tps, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "response": full_response
    }

def write_results(result):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_path = os.path.join(root_dir, "results.txt")

    with open(results_path, "a") as f:
        f.write("=" * 50 + "\n")
        f.write(f"Model:          {result['model']}\n")
        f.write(f"TTFT:           {result['ttft']}s\n")
        f.write(f"Total Latency:  {result['total_latency']}s\n")
        f.write(f"TPS:            {result['tps']} tokens/sec\n")
        f.write(f"Input Tokens:   {result['input_tokens']}\n")
        f.write(f"Output Tokens:  {result['output_tokens']}\n")
        f.write(f"Total Tokens:   {result['total_tokens']}\n")
        f.write("\n--- RESPONSE ---\n")
        f.write(result['response'])
        f.write("\n" + "=" * 50 + "\n\n")

if __name__ == "__main__":
    result = run_openai()
    write_results(result)
    print(f"Done. Results written to results.txt")