# AI Building Blocks Map

## Introduction

Modern AI applications are built using different components and techniques. Understanding these building blocks helps us choose the right approach for a business problem.

## 1. Multimodal Input

**What it is:** Multimodal AI can understand more than one type of input, such as text, images, audio and video. It can combine information from different formats to understand a request.

**When to use:** When users need to upload documents, images, audio recordings or other media for AI to analyse.

**Costs and risks:**
- Processing images, audio and video can increase costs.
- Poor-quality input may produce incorrect results.
- Sensitive information in uploaded files needs protection.

## 2. Fine-tuning

**What it is:** Fine-tuning means taking an existing trained model and training it further on a specialised dataset. It helps the model learn a particular task, style or domain-specific pattern.

**When to use:** When a general model repeatedly fails to follow a required format, classification approach or specialised behaviour.

**Costs and risks:**
- Requires suitable training data and technical expertise.
- Training and maintaining the model can be expensive.
- Poor-quality or biased training data can affect results.
- Fine-tuning does not automatically provide the latest company policies.

## 3. Multi-agent Systems

**What it is:** A multi-agent system uses multiple AI agents that work together to complete a task. Each agent can have a separate responsibility, such as searching information, analysing results or preparing a response.

**When to use:** When a business process has several distinct tasks that can be divided between specialised agents.

**Costs and risks:**
- More agents can increase processing time and cost.
- Agents may produce conflicting results.
- Coordination, permissions and monitoring become more complex.

## 4. Memory

**What it is:** Memory allows an AI application to retain selected information from previous interactions. It can use that information to provide more relevant responses in future interactions.

**When to use:** When an assistant needs to remember useful user preferences, previous tasks or ongoing conversation details.

**Costs and risks:**
- Incorrect or outdated information may be remembered.
- Sensitive information must be handled carefully.
- Memory needs clear retention, access and deletion controls.

## 5. Context Management

**What it is:** Context management controls which information is provided to an LLM when it generates a response. It includes selecting relevant documents, conversation history and instructions within the model's context window.

**When to use:** When an application handles long conversations, large documents or multiple sources of information.

**Costs and risks:**
- Large contexts can increase token usage and cost.
- Important information may be omitted if context is selected poorly.
- Irrelevant information can reduce answer quality.

## 6. AI Gateways

**What it is:** An AI gateway acts as a central layer between applications and AI models. It can manage model selection, authentication, rate limits, logging, monitoring and usage policies.

**When to use:** When an organisation uses multiple AI models or needs centralised control over AI access and usage.

**Costs and risks:**
- Adds another system that needs configuration and maintenance.
- Gateway failures can affect connected applications.
- Logging and monitoring must be designed to protect sensitive data.

## 7. Skills

**What it is:** Skills are reusable instructions, knowledge and workflows that help an AI agent perform specific tasks. They can guide an agent through a consistent process using defined procedures and tools.

**When to use:** When an agent needs to perform repeatable tasks, follow business procedures or use specialised domain knowledge.

**Costs and risks:**
- Skills need regular updates as processes change.
- Incorrect instructions can lead to incorrect actions.
- Tool access and permissions must be controlled carefully.

## Conclusion

These building blocks solve different problems and can be combined in one AI application. The right choice depends on business requirements, data availability, security, complexity and cost.

For an HR leave assistant, RAG and context management can help provide policy-based answers, while memory, AI gateways and skills may support additional capabilities when required.