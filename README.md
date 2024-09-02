# xai
Translate any human instruction into a unix command


https://github.com/user-attachments/assets/261bbab5-34f9-4855-9a9e-07f1f29074d6



# Getting started
Before you get started, you need to create a `.env` file in the project's root directory.

This file will store your `API_KEY` as an environment variable, necessary for the application to interact with the [API](https://platform.openai.com/docs/api-reference/authentication) (make sure to add the file to your `.gitignore` if you are using GIT).

```plaintext
API_KEY=your_openai_api_key
```

# Usage
1. Setup `xai` for the first time running `xai --setup`
2. Make any request to xai. For example:
   ```bash
   xai make post request
   # returns:
   # curl -X POST https://example.com/resource -d 'param1=value1&param2=value2'
   ```
