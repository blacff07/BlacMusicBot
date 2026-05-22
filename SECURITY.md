# Security Policy

We take the security of **BlacMusicBot** seriously and appreciate responsible disclosure of vulnerabilities.

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, contact the maintainer directly via Telegram with:
- A description of the vulnerability
- Steps to reproduce it
- Potential impact

We aim to respond within 48 hours.

## Keeping Up To Date

We strongly recommend always running the latest stable release of **BlacMusicBot** to ensure you have the latest security patches.

## Self-Hosting Security

As **BlacMusicBot** is a self-hosted Telegram bot, users are responsible for:

- **Never committing `.env`** to version control — it contains credentials
- **Rotating session strings** immediately if you suspect a session is compromised
- **Keeping MongoDB access restricted** — use IP allowlists on Atlas
- **Running on a private VPS** rather than shared hosting when possible
- **Keeping dependencies updated** — run `pip install -r requirements.txt --upgrade` regularly