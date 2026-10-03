# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this project, please report it responsibly by emailing [aayash317@gmail.com](mailto:aayash317@gmail.com).

**Please do not open a public GitHub issue for security vulnerabilities.**

## Important Notes for Deployment

- The `backend/.env` file contains credentials and is **never committed** (it is gitignored).
- Refer to `backend/.env.example` for the list of required environment variables.
- Never use `password123` or weak passwords in any real deployment.
- The demo credentials in the README are for local development only.
- JWT secrets must be strong random strings in production.
- MongoDB URI should point to a properly secured instance in production.