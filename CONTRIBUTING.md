# Contributing to SynapseAI

Thank you for your interest in contributing to SynapseAI.

SynapseAI is an open-source AI chatbot project built with Python, LangChain, RAG, and agent-based tools. Contributions that improve functionality, reliability, documentation, testing, and maintainability are welcome.

## Contribution Workflow

The recommended contribution workflow is:

```text
Fork
  ↓
Clone
  ↓
Create or choose an Issue
  ↓
Create a Branch
  ↓
Implement Changes
  ↓
Test
  ↓
Commit
  ↓
Push
  ↓
Create Pull Request
```

## 1. Fork the Repository

Fork the SynapseAI repository to your GitHub account.

Then clone your fork:

```bash
git clone https://github.com/<your-username>/synapse-ai.git
cd synapse-ai
```

## 2. Set Up the Development Environment

SynapseAI requires:

* Python 3.12+
* Git
* `uv`

Install the project dependencies:

```bash
uv sync
```

Create a local `.env` file using `.env.example` as a reference.

Never commit the actual `.env` file or any API keys.

## 3. Create or Choose an Issue

Before starting significant work, create or choose a GitHub Issue describing the problem, feature, or improvement.

An Issue helps contributors discuss the proposed change before implementation begins.

For small documentation or maintenance changes, an Issue may not always be necessary.

## 4. Create a Branch

Create a new branch from the current development branch.

Use the following naming convention:

```text
feature/<issue-number>-<short-description>
```

Example:

```text
feature/28-web-search-tool
```

Other useful prefixes include:

```text
fix/<issue-number>-<short-description>
docs/<issue-number>-<short-description>
refactor/<issue-number>-<short-description>
test/<issue-number>-<short-description>
```

Keep branch names short, descriptive, and related to the Issue.

## 5. Implement the Changes

Keep changes focused on the purpose of the Issue.

Before modifying existing architecture, understand how the affected components currently work.

For changes involving RAG, agents, tools, or application flow:

* Understand the existing implementation first.
* Avoid unnecessary architectural changes.
* Keep responsibilities clear.
* Preserve existing functionality unless the change intentionally modifies it.

## 6. Test Your Changes

Test changes locally before creating a Pull Request.

At minimum:

* Run the application locally.
* Test the functionality you changed.
* Verify existing functionality still works.
* Check for obvious errors or regressions.

For SynapseAI, the application can be started with:

```bash
uv run streamlit run chatbot.py
```

If you modify document indexing or RAG functionality, also test the relevant document workflow.

If automated tests are added to the project, contributors should run them before opening a Pull Request.

## 7. Commit Your Changes

Use clear and descriptive commit messages.

SynapseAI follows a Conventional Commits-style format:

```text
<type>: <short description>
```

Common types include:

```text
feat:     New functionality
fix:      Bug fix
docs:     Documentation changes
refactor: Code restructuring without changing behavior
test:     Tests
chore:    Maintenance or configuration changes
```

Examples:

```text
feat: add web search tool
fix: handle missing weather api key
docs: update project README
refactor: simplify document indexing
test: add rag retrieval tests
chore: update dependencies
```

Keep commits focused and avoid combining unrelated changes into one commit.

## 8. Push Your Branch

Push your branch to your fork:

```bash
git push origin <branch-name>
```

Example:

```bash
git push origin feature/28-web-search-tool
```

## 9. Create a Pull Request

Create a Pull Request against the project's development branch.

The Pull Request should clearly explain:

* What was changed
* Why the change was needed
* Which Issue it addresses
* How the change was tested
* Any limitations or follow-up work

When applicable, reference the related Issue:

```text
Closes #28
```

## Pull Request Expectations

A good Pull Request should:

* Address a clear problem or improvement.
* Keep changes focused.
* Include relevant tests where appropriate.
* Avoid unnecessary changes.
* Update documentation when behavior or usage changes.
* Explain important implementation decisions.
* Preserve existing functionality unless intentionally changed.

Large architectural changes should generally be discussed through an Issue before implementation.

## Code Quality

When contributing code:

* Follow existing project conventions.
* Prefer clear and readable code.
* Keep functions focused on a clear responsibility.
* Avoid unnecessary duplication.
* Use descriptive names.
* Handle expected errors appropriately.
* Avoid hardcoding secrets or credentials.
* Keep configuration separate from application logic where appropriate.

Do not introduce architectural changes simply to solve a small local problem.

## Documentation

Documentation should be updated when a change affects:

* User-facing behavior
* Installation or setup
* Environment variables
* Application usage
* Architecture
* Developer workflow
* Supported functionality

If a new feature changes how SynapseAI is used, update the relevant documentation in the same Pull Request.

## Secrets and API Keys

Never commit:

* API keys
* Passwords
* Access tokens
* Private credentials
* `.env` files
* Other sensitive configuration

Use `.env` for local development and `.env.example` to document required environment variables.

If a secret is accidentally committed, report it immediately and rotate the affected credential.

## Before Opening a Pull Request

Use this checklist:

* [ ] The change addresses a specific problem or improvement.
* [ ] The code works locally.
* [ ] Existing functionality still works.
* [ ] Relevant tests have been run.
* [ ] Documentation has been updated if necessary.
* [ ] No API keys or secrets have been committed.
* [ ] Commit messages are clear and descriptive.
* [ ] The Pull Request clearly explains the changes.
* [ ] The related Issue is referenced when applicable.

Thank you for contributing to SynapseAI!
