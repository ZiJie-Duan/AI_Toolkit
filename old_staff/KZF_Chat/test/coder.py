import base64

with open(r"C:\Users\Peter Duan\Desktop\AI_Toolkit\KZF_Chat\Client\dist\logo.ico", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

print(encoded_string)
input()
