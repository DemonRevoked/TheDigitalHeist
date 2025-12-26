# ai-02-cerberus — Walkthrough

## Goal
Make the API return the hidden label **VAULT-ACCESS** (it will also return the flag and key).

## Steps
1. **Open the API docs**
   - Visit:
     - `/analyze` (GET)
   - You will see how to send data.

2. **Send 20 numbers**
   - You must POST JSON like:
     - `{"features":[...20 numbers...]}`

3. **Hit the hidden trigger**
   - The hidden trigger is:
     - feature[7] > 0.8
     - feature[9] < -0.5
     - feature[13] > 0.9

4. **Example request**
   - Send features like this (20 values):
     - all zeros, but set:
       - index 7  = 0.9
       - index 9  = -0.6
       - index 13 = 0.95

5. **Read the response**
   - If you did it right, the API replies with:
     - `"label": "VAULT-ACCESS"`
     - the **flag**
     - the **key**

