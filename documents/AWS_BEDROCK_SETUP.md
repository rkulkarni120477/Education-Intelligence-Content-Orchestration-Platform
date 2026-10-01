# AWS Bedrock Setup Guide

## Problem
The Chat is showing "Server error: Not Found" because AWS credentials are not configured.

## Solution

### 1. Get AWS Credentials

You need an AWS account with Bedrock access. Follow these steps:

1. **Go to AWS Console**: https://console.aws.amazon.com/
2. **Log in** with your AWS account
3. **Navigate to IAM** → Users → Create User (if needed)
4. **Attach Bedrock Policy**: Attach `AmazonBedrockFullAccess` or create a custom policy
5. **Create Access Keys**: 
   - Go to User → Security Credentials
   - Click "Create access key"
   - Choose "Other"
   - Copy the Access Key ID and Secret Access Key

### 2. Update .env File

Edit `backend/.env` and replace the placeholders:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE        # Your actual access key
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # Your secret key
BEDROCK_MODEL_ID=anthropic.claude-3-5-haiku-20241022-v1:0
```

### 3. Verify Bedrock Access

Make sure your AWS account has access to Claude models in Bedrock:

1. Go to AWS Console → Bedrock → Models
2. Check if `anthropic.claude-3-5-haiku-20241022-v1:0` is available
3. If not, request access (Model Access → Manage model access)

### 4. Restart Backend

After updating `.env`:

```bash
# Kill the old process
pkill -f "uvicorn app:app"

# Start fresh
cd backend
python -m uvicorn app:app --reload --port 8000
```

### 5. Test the Chat

1. Go to http://127.0.0.1:3000/custom-content-development
2. Type a message in the chat
3. Click Send
4. Watch for streaming response

---

## Troubleshooting

### Error: "InvalidClientTokenId"
- Check AWS Access Key ID is correct
- Check AWS Secret Access Key is correct
- Verify credentials are active (not deleted)

### Error: "User is not authorized to perform: bedrock:InvokeModelWithResponseStream"
- Missing Bedrock permission
- Add `AmazonBedrockFullAccess` policy to your IAM user

### Error: "Model not found"
- Check model ID is correct: `anthropic.claude-3-5-haiku-20241022-v1:0`
- Request model access in Bedrock console

### No streaming response
- Check backend logs for detailed error message
- Verify AWS credentials are loaded: `python -c "import os; print(os.getenv('AWS_ACCESS_KEY_ID'))"`

---

## Security Note

⚠️ **Never commit `.env` to git!** It contains sensitive credentials.

The `.env` file is already in `.gitignore` - it will not be pushed to the repository.

---

## What Happens When Credentials Are Configured

1. User sends message in chat
2. Frontend calls `/api/v1/custom-content/conversations/{id}/messages/stream`
3. Backend LLMService:
   - Loads AWS Bedrock client
   - Builds system prompt with file context
   - Calls Claude Haiku model
   - Streams response via SSE
4. Frontend receives chunks in real-time
5. Message displays with typing indicator
6. Conversation auto-saves

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJal...` |
| `BEDROCK_MODEL_ID` | Model to use | `anthropic.claude-3-5-haiku-20241022-v1:0` |
| `LLM_MAX_FILE_CONTEXT_SIZE` | Max file context (bytes) | `1000000` (1MB) |
| `LLM_RESPONSE_TIMEOUT` | Response timeout (seconds) | `300` (5 min) |

---

## Getting AWS Free Tier

If you don't have AWS yet:
1. Sign up: https://aws.amazon.com/free/
2. Free tier includes some Bedrock API calls
3. Monitor usage to avoid charges: https://console.aws.amazon.com/cost-management/
