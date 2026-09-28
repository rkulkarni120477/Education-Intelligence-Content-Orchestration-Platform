# AWS Bedrock Migration Guide

## Overview
This document describes the migration from Claude (Anthropic) API to AWS Bedrock as the AI service provider for the Education Intelligence & Content Orchestration Platform.

## Changes Made

### 1. Dependencies Updated
**File:** `backend/requirements.txt`

**Removed:**
- `langchain-anthropic`

**Added:**
- `langchain-aws`
- `boto3==1.35.0`
- `botocore==1.34.0`

### 2. Backend Services Updated

#### Requirements Extraction Service
**File:** `backend/services/requirements_extraction.py`
- Replaced `ChatAnthropic` with `boto3.client('bedrock-runtime')`
- Updated model default: `anthropic.claude-opus-5-sonnet-20241022-v2:0`
- Changed API call from `client.invoke()` to `client.converse()`
- Updated message format to AWS Bedrock API format

#### Skill Mapping Service
**File:** `backend/services/skill_mapping.py`
- Replaced `ChatAnthropic` with `boto3.client('bedrock-runtime')`
- Updated model default: `anthropic.claude-opus-5-sonnet-20241022-v2:0`
- Changed API call from `client.invoke()` to `client.converse()`
- Updated message format to AWS Bedrock API format

#### Recommendations Service
**File:** `backend/services/recommendations.py`
- Replaced `ChatAnthropic` with `boto3.client('bedrock-runtime')`
- Updated model default: `anthropic.claude-opus-5-sonnet-20241022-v2:0`
- Changed API call from `client.invoke()` to `client.converse()`
- Updated message format to AWS Bedrock API format

### 3. Configuration Updates

#### Config File
**File:** `backend/config.py`

**Added:**
```python
AWS_REGION: str = "us-east-1"
AWS_ACCESS_KEY_ID: Optional[str] = None
AWS_SECRET_ACCESS_KEY: Optional[str] = None
LLM_PROVIDER: str = "bedrock"
LLM_MODEL: str = "anthropic.claude-opus-5-sonnet-20241022-v2:0"
```

#### Environment File
**File:** `backend/.env`

**Added:**
```
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key

# LLM Configuration (AWS Bedrock)
LLM_PROVIDER=bedrock
LLM_MODEL=anthropic.claude-opus-5-sonnet-20241022-v2:0
LLM_TEMPERATURE=0.7
```

### 4. API Updates

#### Agents API
**File:** `backend/api/agents.py`

**Updated:**
- AI_PROVIDERS configuration to show AWS Bedrock as active provider
- AI statistics endpoint to report AWS Bedrock usage and pricing
- Provider name: "AWS Bedrock"
- Available models: AWS Bedrock model IDs for Claude variants

## Setup Instructions

### Prerequisites
1. AWS Account with Bedrock access
2. AWS credentials (Access Key ID and Secret Access Key)
3. Bedrock models enabled in your AWS account

### Step 1: Enable Bedrock Models in AWS Console
1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access"
3. Enable the following models:
   - Anthropic Claude Opus 5 Sonnet
   - Anthropic Claude 3.5 Sonnet (optional)
   - Anthropic Claude 3 Sonnet (optional)

### Step 2: Configure AWS Credentials
Set up your AWS credentials in the `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-actual-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-actual-aws-secret-access-key

# LLM Configuration
LLM_PROVIDER=bedrock
LLM_MODEL=anthropic.claude-opus-5-sonnet-20241022-v2:0
```

**Alternative:** Use AWS CLI configuration
```bash
aws configure
```

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Test the Connection
Run the application and verify in logs that AWS Bedrock is being used:
```bash
python -m uvicorn backend.app:app --reload
```

## AWS Bedrock Model IDs

Available Claude models via AWS Bedrock:

| Model | Model ID |
|-------|----------|
| Claude Opus 5 Sonnet | `anthropic.claude-opus-5-sonnet-20241022-v2:0` |
| Claude 3.5 Sonnet | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| Claude 3 Sonnet | `anthropic.claude-3-sonnet-20240229-v1:0` |

## Pricing

AWS Bedrock Claude pricing (approximate):
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens

*(Prices may vary by region and model. Check AWS Bedrock pricing page for current rates)*

## API Changes

### Before (Anthropic)
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

client = ChatAnthropic(model="claude-opus-5-5")
response = client.invoke([
    SystemMessage(content="..."),
    HumanMessage(content="..."),
])
```

### After (AWS Bedrock)
```python
import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.converse(
    modelId="anthropic.claude-opus-5-sonnet-20241022-v2:0",
    messages=[
        {"role": "user", "content": "..."}
    ],
    inferenceConfig={
        "maxTokens": 4096,
        "temperature": 0.7,
    }
)
text = response['output']['message']['content'][0]['text']
```

## Verification Checklist

- [ ] AWS credentials configured in `.env`
- [ ] Bedrock models enabled in AWS console
- [ ] Dependencies installed: `pip install -r backend/requirements.txt`
- [ ] Application starts without errors
- [ ] Workflow executions work with AWS Bedrock
- [ ] Agent execution tracking displays progress correctly
- [ ] AI statistics show AWS Bedrock provider
- [ ] Skill mapping and recommendations generate correctly

## Troubleshooting

### Error: "User is not authorized to perform: bedrock:InvokeModel"
**Solution:** Enable the Claude models in AWS Bedrock console under "Model access"

### Error: "Invalid AWS credentials"
**Solution:** Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in `.env` file

### Error: "Model not found: anthropic.claude-opus-5-sonnet-20241022-v2:0"
**Solution:** 
1. Check region is set correctly (AWS_REGION)
2. Verify model is enabled in Bedrock Model access console

### Slow responses
**Solution:** Increase maxTokens or check AWS region for latency

## Rollback Instructions

If you need to rollback to Anthropic:

1. Restore original requirements.txt
2. Reinstall dependencies: `pip install -r backend/requirements.txt`
3. Update service files to use `ChatAnthropic` instead of boto3
4. Restore ANTHROPIC_API_KEY in `.env`

## Support

For AWS Bedrock issues, refer to:
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Claude on AWS Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids-supported.html)
