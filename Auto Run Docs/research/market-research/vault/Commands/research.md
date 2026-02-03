# Research Entity

Research a specific entity and add it to the Czech Healthcare AI & Decision Support knowledge vault.

## Usage
Provide the entity type and name to research.

## Process
1. Identify the appropriate agent for the entity type:
   - Company → use company-researcher agent
   - Product → use product-researcher agent
   - Person → use person-researcher agent
   - Technology → use technology-researcher agent
   - Trend → use trend-researcher agent

2. Spawn the agent with the Task tool to research the entity

3. Verify the profile was created and INDEX.md was updated

## Example
"Research the company Acme Corp"
→ Spawns company-researcher agent
→ Creates Companies/Acme-Corp.md
→ Updates INDEX.md
