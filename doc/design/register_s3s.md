# s3s Registration via Discord Bot

This document summarizes the input prompts and display items involved in the s3s initial registration process when integrated into the Discord Bot. Each item is mapped to its original location in the s3s scripts.

## 1. stat.ink API Key

- Prompt:
  ```
  stat.ink API key: 
  ```
- Re-prompt on invalid input:
  ```
  Invalid stat.ink API key. Please re-enter it below.
  stat.ink API key: 
  ```
- Original code: [`s3s/s3s.py`](s3s/s3s.py:1318-1323)

## 2. Locale / Language Code

- Display:
  ```
  Default locale is en-US. Press Enter to accept, or enter your own (see readme for list).
  ```
- Prompt for input:
  ```
  (empty prompt, waiting for locale code)
  ```
- Re-prompt on invalid code:
  ```
  Invalid language code. Please try entering it again:
  ```
- Original code: [`s3s/s3s.py`](s3s/s3s.py:1332-1347)

## 3. Nintendo Account Automatic Login Flow

- Display instructional text:
  ```
  Make sure you have read the "Token generation" section of the readme before proceeding. To manually input your tokens instead, enter "skip" at the prompt below.

  Navigate to this URL in your browser:
  https://accounts.nintendo.com/connect/1.0.0/authorize?...
  ```
- Prompt:
  ```
  Log in, right click the "Select this account" button, copy the link address, and paste it below:
  ```
- Input:
  - User pastes the `use_account_url`
  - Or enters `skip` to bypass automatic login and use manual token entry
- Original code: [`s3s/iksm.py`](s3s/iksm.py:187-195)

## 4. Manual Token Entry (gtoken & bulletToken)

- Display instructions:
  ```
  Go to the page below to find instructions to obtain your gtoken and bulletToken:
  https://github.com/frozenpandaman/s3s/wiki/mitmproxy-instructions
  ```
- Prompts and validation loops:
  - Prompt:
    ```
    Enter your gtoken: 
    ```
    - On invalid (length != 926):
      ```
      Invalid token - length should be 926 characters. Try again.
      Enter your gtoken: 
      ```
  - Prompt:
    ```
    Enter your bulletToken: 
    ```
    - On invalid (length != 124):
      ```
      Invalid token - length should be 124 characters. Try again.
      Enter your bulletToken: 
      ```
- Original code: [`s3s/iksm.py`](s3s/iksm.py:511-524)