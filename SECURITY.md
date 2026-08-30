# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in SynapseAI, please report it privately rather than opening a public GitHub Issue.

Use GitHub's private vulnerability reporting feature when available.

Please include:

* A description of the vulnerability
* Steps to reproduce the issue
* Potential impact
* Relevant logs or screenshots, if applicable
* A possible mitigation, if known

Please do not publicly disclose the vulnerability until it has been reviewed and addressed.

## Secrets and API Keys

Never commit secrets or credentials to the repository.

This includes:

* API keys
* Access tokens
* Passwords
* Private credentials
* `.env` files
* Other sensitive configuration

Use a local `.env` file for development and `.env.example` to document the required environment variables.

If a secret is accidentally committed:

1. Revoke or rotate the exposed credential immediately.
2. Remove the secret from the repository history where appropriate.
3. Check for any other exposed credentials.
4. Report the incident privately.

## Supported Versions

SynapseAI is currently under active development.

Security fixes will generally target the latest version available on the project's development branch.

Older versions may not receive security updates.

## Responsible Disclosure

Please give the project maintainers a reasonable opportunity to investigate and address a reported vulnerability before publicly disclosing it.

Thank you for helping keep SynapseAI and its contributors safe.
