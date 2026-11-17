# Consulting Practice: Make Our Support Team Faster

## 1. Understand and define the problem

**Business brief:** “Make our support team faster.”

This is an ambiguous problem because “faster” could mean:
- Customers receive their first response sooner.
- Support requests are resolved in less time.
- Agents spend less time handling each request.
- Fewer requests need to be reopened or escalated.

### Core problem statement

**How can we reduce the time taken to resolve customer support requests while maintaining customer satisfaction and resolution quality?**

This gives us a focused question to investigate.

### Define success

We should measure:

| Metric | What it tells us |
|---|---|
| First response time | How quickly customers receive an initial response |
| Average resolution time | How long it takes to resolve a request |
| Median and 90th-percentile resolution time | Typical experience and experience of slower cases |
| Agent handling time | How much active time agents spend on requests |
| Reopen rate | Whether requests are actually resolved correctly |
| Customer satisfaction (CSAT) | Whether customers are happy with the support |

**Important constraint:** Improving speed must not reduce answer accuracy, customer satisfaction or the quality of resolution.

---

## 2. MECE issue tree

To investigate the problem, I will divide the total time spent on a support request into four distinct stages.

**Core question: What is causing customer support requests to take longer than expected?**

1. Time before an agent starts working on the request.
2. Time the agent actively spends handling the request.
3. Time the request waits for information or assistance.
4. Time between resolving the issue and closing the request.

These four branches are based on the request's workflow status. Each period of elapsed time belongs to one stage at a time, so we avoid double-counting.

### Branch 1: Waiting before an agent starts working

**Question:** Why do support requests wait too long before an agent starts handling them?

Possible sub-branches:
- High incoming request volume.
- Insufficient agent availability.
- Poor request categorisation.
- Incorrect assignment or routing.
- Lack of prioritisation for urgent requests.
- Uneven distribution of requests between agents.

**Hypothesis:** Requests take longer to receive an initial response because incoming requests are not being categorised and assigned efficiently.

**How to investigate:**
- Check the time between request creation and first agent activity.
- Compare waiting times across support channels.
- Identify queues with the highest waiting times.
- Review whether requests are assigned to the correct teams.

**Proposed stage: POC (Proof of Concept)**

Start with a small test of automated categorisation or improved routing using historical or sample support requests.

**What must be true to move to Pilot?**
- The categorisation and routing approach correctly handles a representative sample of requests.
- It reduces assignment delays in testing.
- Incorrect assignments and urgent-request handling are checked.

**What must be true to move from Pilot to MVP?**
- A limited live queue demonstrates improved response times.
- Agents can correct incorrect routing.
- The process works reliably for the selected request categories.

**What must be true to move from MVP to Production?**
- Routing works consistently across the support operation.
- Monitoring, ownership, access controls and fallback procedures are in place.
- Improvements are sustained without negatively affecting service quality.

### Branch 2: Time spent actively handling requests

**Question:** Why do agents need too much time to understand and resolve requests?

Possible sub-branches:
- Agents cannot quickly find the correct information.
- Knowledge base articles are incomplete or outdated.
- Agents lack the necessary training or experience.
- Support tools are slow or difficult to use.
- Resolution procedures involve unnecessary steps.
- Complex requests require repeated investigation.

**Hypothesis:** Agents spend too much time searching for information and understanding resolution procedures.

**How to investigate:**
- Review agent handling time by request category.
- Observe how agents search for answers.
- Identify frequently repeated questions.
- Interview agents about common difficulties.
- Check whether useful knowledge articles already exist.

**Proposed stage: POC (Proof of Concept)**

Create a small searchable knowledge resource for one frequently occurring support category and test whether agents can find accurate answers more quickly.

**What must be true to move to Pilot?**
- The knowledge resource provides relevant and accurate information.
- Agents can find answers faster than with the existing process.
- Incorrect or unsupported answers are identified.

**What must be true to move from Pilot to MVP?**
- A limited group of agents uses the resource during real support work.
- It covers the most common questions in the selected category.
- Agents can report missing or outdated information.

**What must be true to move from MVP to Production?**
- The knowledge resource is maintained and regularly updated.
- It integrates into the normal support workflow.
- Accuracy, usage and time savings are monitored.

### Branch 3: Time waiting for information or assistance

**Question:** Why do support requests remain unresolved while waiting for someone else?

Possible sub-branches:
- The customer has not provided required information.
- The request needs assistance from another internal team.
- Manager approval is required.
- Technical issues need engineering investigation.
- External vendors or service providers are delaying resolution.

**Hypothesis:** Requests are delayed because dependencies and escalations are not being followed up efficiently.

**How to investigate:**
- Identify requests with long waiting periods.
- Record why each request is waiting.
- Compare waiting times for customer responses and internal escalations.
- Identify teams or approval stages causing repeated delays.
- Review how escalations are tracked.

**Proposed stage: POC (Proof of Concept)**

Test a simple escalation tracker with clear ownership, waiting reasons and follow-up reminders for one support category.

**What must be true to move to Pilot?**
- The tracker correctly identifies the person or team responsible for each dependency.
- Follow-up reminders are useful and do not create unnecessary noise.
- Delays can be measured before and after the test.

**What must be true to move from Pilot to MVP?**
- A limited support team uses the tracker in live cases.
- Escalations have clear ownership and follow-up expectations.
- Waiting time is reduced without unnecessary escalations.

**What must be true to move from MVP to Production?**
- The process is adopted by all relevant teams.
- Ownership and escalation rules are documented.
- The process is monitored and maintained consistently.

### Branch 4: Time taken to close a resolved request

**Question:** Why do requests remain open after the actual issue has been resolved?

Possible sub-branches:
- Agents must complete lengthy manual documentation.
- Closure requires unnecessary administrative steps.
- Customer confirmation is delayed.
- Resolution notes are incomplete.
- The ticketing system does not automatically update request status.

**Hypothesis:** Manual closure and documentation processes create avoidable delays after an issue has already been resolved.

**How to investigate:**
- Compare the time of actual resolution with the final ticket closure time.
- Review the number of manual steps required.
- Identify repeated documentation tasks.
- Check which closure steps are genuinely necessary.

**Proposed stage: POC (Proof of Concept)**

Test a standard resolution-note template and a simplified closure checklist for one type of support request.

**What must be true to move to Pilot?**
- The template captures all required information.
- Agents can complete closure tasks more quickly.
- Required documentation and customer confirmation are not skipped.

**What must be true to move from Pilot to MVP?**
- A limited group of agents successfully uses the simplified process.
- Closure time decreases.
- Reopened requests and incomplete documentation do not increase.

**What must be true to move from MVP to Production?**
- The closure process is approved and documented.
- It works reliably with the ticketing system.
- Quality checks and monitoring are in place.

---

## 3. Summary of the issue tree

| Main branch | Main area to investigate | Proposed stage |
|---|---|---|
| 1. Before agent handling | Queue, categorisation and assignment | POC |
| 2. Active handling | Knowledge, training and tools | POC |
| 3. Waiting for dependencies | Customer information, escalations and approvals | POC |
| 4. After resolution | Documentation and ticket closure | POC |

**Why are all four branches initially at POC?**

The brief does not provide actual support data, measurements or evidence that any solution has already been tested. Therefore, it would be premature to label a branch as Pilot, MVP or Production.

POC is the most appropriate starting point. Each branch can advance independently when its evidence and success criteria are met.

---

## 4. Prioritisation of the branches

I would prioritise the branches based on their likely impact on total resolution time, how frequently the problem occurs, and how easy it is to investigate.

| Priority | Branch | Reason |
|---|---|---|
| 1 | Before agent handling | Queue and assignment delays can affect a large number of requests. |
| 2 | Active handling | Improving knowledge access can save time across many requests. |
| 3 | Waiting for dependencies | Long escalations and missing information can significantly delay resolution. |
| 4 | After resolution | Simplifying closure can reduce administrative delays. |

This is an initial prioritisation based on the problem structure, not a conclusion supported by actual company data.

Before committing resources, I would compare the four branches using ticket data and interviews with support agents.

---

## 5. Proposed investigation and action plan

1. Collect support ticket data covering a representative period.
2. Measure first response time and total resolution time.
3. Break total elapsed time into the four workflow stages.
4. Identify which stage contributes most to delays.
5. Analyse the most common request categories.
6. Interview support agents to understand their difficulties.
7. Review customer feedback and reopened requests.
8. Select the highest-impact problem to investigate first.
9. Create a small proof of concept for the selected problem.
10. Compare the results with the existing process.
11. If successful, test the solution with a limited group through a pilot.
12. Expand to a minimum viable product once the pilot demonstrates reliable results.
13. Move to production only when the solution is reliable, maintainable and supported by clear ownership and monitoring.

---

## 6. Conclusion

The brief “make our support team faster” is too broad to solve directly. Using the MECE approach, I divided the support workflow into four areas: waiting before an agent starts, active handling, waiting for dependencies, and time taken to close a resolved request.

For each branch, I identified possible causes, formed a hypothesis, proposed ways to investigate it, and assigned an initial POC stage.

My recommendation is to first measure where the largest amount of time is being lost. Then we should test the highest-impact hypothesis through a small proof of concept, evaluate the results, and move through Pilot, MVP and Production only when the required evidence is available.

**The overall objective is not simply to close tickets faster, but to resolve customer issues faster while maintaining accuracy and customer satisfaction.**