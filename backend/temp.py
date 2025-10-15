import google.generativeai as genai

    # Configure your API key
genai.configure(api_key="AIzaSyCT0xiv-7bAx02mCNx7qSn92VV6WOHXjdM")

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)