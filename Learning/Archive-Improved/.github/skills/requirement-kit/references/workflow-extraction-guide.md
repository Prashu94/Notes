# Workflow Extraction Guide

## What is a Workflow?

A workflow is a sequence of steps performed by one or more actors to achieve a business outcome. It has a trigger, steps, decision points, and a post-condition.

## Types of Workflows

| Type | Description | Example |
|------|-------------|---------|
| **User Workflow** | Human actor drives the process | User places an order |
| **System Workflow** | Automated, no human interaction | Nightly batch process |
| **Collaborative Workflow** | Multiple actors/systems | Order approval chain |
| **Exception Workflow** | Error and edge-case handling | Payment failure retry |

## Identification Signals

Look for these patterns in requirements:

- Step-by-step processes described in numbered lists
- Conditional flows: "If X then Y, otherwise Z"
- Role-specific actions: "The supervisor then approves..."
- Trigger-outcome pairs: "When an order is placed, the warehouse receives a pick list"
- State transitions: "The order moves from PENDING to CONFIRMED when..."
- User journeys described in prose

## Workflow Documentation Pattern

```
WF-NNN: <Name>
Trigger: <What event or user action starts this>
Actor(s): <Who participates — user roles, system names>
Pre-conditions: <What must already be true>
Main Flow:
  1. <Actor> <action>
  2. System <response>
  3. <Actor> <decision>
     3a. If <condition>: <sub-flow>
     3b. If <condition>: <sub-flow>
Post-conditions: <What is guaranteed to be true when flow completes>
Alternate Flows:
  Alt-1: <name> — <trigger> → <steps>
Exception Flows:
  Exc-1: <name> — <trigger> → <recovery steps>
Business Rules: BR-001, BR-002
Related Workflows: WF-NNN
```

## BPMN Notation for Descriptions

When describing workflows in markdown, use these notation conventions:
- `[ ]` = Task/Activity
- `< >` = Gateway/Decision
- `(( ))` = Start/End Event
- `{ }` = Sub-process
- `-->` = Sequence flow

## Tips for Complex Workflows

1. Break long workflows (>10 steps) into sub-workflows and reference them
2. Identify reusable sub-flows (authentication, notification) — mark them as `SHARED`
3. Note system integrations at each step ("System calls Payment Gateway API")
4. Flag asynchronous steps with `[ASYNC]`
5. Note SLAs or timeouts where mentioned: "must complete within 5 minutes"
