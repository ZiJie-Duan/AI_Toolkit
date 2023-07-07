import openai
openai.api_key = "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"


while True:

    uinput = input("\n\nUser: ")
    

    for chunk in openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": uinput,
        }],
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            print(content,end="",flush=True)

