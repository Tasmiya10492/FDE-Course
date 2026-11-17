# What an LLM Cannot Do – Customer Note

## Introduction

A Large Language Model (LLM) can understand questions and generate human-like responses. However, it does not always provide correct or reliable information. In an HR leave assistant, we must understand its limitations before allowing employees to depend on its answers.

## 1. It cannot guarantee factual accuracy

An LLM can generate incorrect information or make up details when it does not know the answer. This is sometimes called hallucination.

**Example:** An employee asks how many maternity leave days they are entitled to. If the policy does not specify the duration, the assistant must not invent a number.

## 2. It cannot automatically know the latest company policies

An LLM does not automatically know about newly updated company policies, employee entitlements or internal announcements.

**Example:** If HR changes its leave policy, the assistant needs access to the updated information before it can answer using that change.

## 3. It cannot replace human judgement

An LLM cannot independently make sensitive HR decisions that require context, approval or human responsibility.

**Example:** It can explain the leave cancellation process, but it cannot replace the reporting manager's approval.

## 4. It cannot guarantee that retrieved information is relevant

In a Retrieval-Augmented Generation (RAG) system, the assistant searches documents before generating an answer. If the wrong document or incomplete information is retrieved, the final answer may also be incorrect.

**Example:** A question about paternity leave may retrieve maternity leave information if the retrieval system selects similar but incorrect content.

## 5. It cannot guarantee privacy or security by itself

An LLM does not automatically enforce company access permissions or protect sensitive employee information. Security controls must be implemented around the system.

**Example:** An employee should not be able to access another employee's leave records simply by asking the assistant.

## 6. It cannot perform real-world actions without connected tools and permissions

An LLM can explain how to submit a leave request, but it cannot automatically submit, approve or cancel one unless the appropriate systems, tools and permissions are connected.

## Recommendation

An AI-powered HR leave assistant should be used to answer routine questions based on approved and updated HR documents. It should clearly communicate uncertainty, avoid inventing policy details, protect employee information and direct employees to HR or their manager when human support or approval is required.

**Key message:** An LLM is an assistant, not a replacement for company policy, secure systems or human decision-making.