# due-skills

[中文](README.md)

[![skills.sh](https://skills.sh/b/dobyte/due-skills)](https://skills.sh/dobyte/due-skills)

AI agent skills for the Due framework. This repository packages Due v2 framework references, runnable examples, and development guidance as reusable skills so AI coding agents can quickly load the right framework context when working on Due projects.

## Install

Use the `skills` CLI:

```bash
npx skills add dobyte/due-skills
```

After installation, restart or reload your AI agent if it does not discover new skills automatically.

## Included Skills

### due-skills

Repository-level entrypoint for the Due framework skill collection.

### due-v2

Complete Due v2 framework development reference, including:

- Framework design: architecture, communication protocols, routing, configuration, runtime modes, error handling, concurrency models, actor model, and rolling updates.
- Core modules: networking, service registration, user locating, RPC transport, cryptography, distributed locks, cache, configuration center, event bus, and logging.
- Cluster services: gate server, node server, mesh server, web server, and client usage.
- Third-party integrations: GORM, Redis, MongoDB, JWT, and Casbin.
- Runnable examples under `skills/due-v2/examples/`.

## Usage Examples

After installing, ask your AI agent to use the `due-v2` skill for Due framework tasks, for example:

```text
Use the due-v2 skill to create a minimal Due node server.
```

```text
Use the due-v2 skill to explain how gate binding and node binding work.
```

```text
Use the due-v2 skill to choose the right runtime mode and configuration pattern for a production deployment.
```
