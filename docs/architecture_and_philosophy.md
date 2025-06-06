# Architecture & Philosophy

This document outlines the architectural decisions, technology stack, and development philosophy behind the `vpnbot` project.

---

## 📌 Project Purpose

`vpnbot` is a Telegram bot designed to provide users with easy and reliable access to VPN services hosted on private servers. The main goal is to ensure stable and censorship-resistant internet access, even during major service disruptions.

The bot automates the purchase and provisioning of VPN access in a secure and user-friendly manner.

---

## 🏗️ Project Structure

All core logic resides in the `app/` directory and is organized by responsibility:

```
app/
├── commons/         # Shared reusable logic
│   ├── services/    # Business-layer services (e.g. Telegram, payments)
│   └── utils/       # Low-level helpers and pure utility functions
├── enums/           # Enumerations for consistent value usage
├── localization/    # Language and message localization
├── models/          # SQLAlchemy ORM models
├── routes/          # aiogram routers and handlers
├── schemas/         # Pydantic models for input/output validation
```

Supporting directories include:
- `config/` – Application configuration and environment setup.
- `database/` – Alembic migrations and initialization logic.
- `logs/` – Log storage directory.
- `docs/` – Developer documentation (this file).

---

## 🧰 Technology Stack

The stack is chosen for its robustness, community support, and developer experience:

- **Python 3.12** – Modern syntax, performance improvements.
- **[Aiogram 3.x](https://docs.aiogram.dev/)** – A clean, type-friendly, and async-native framework for Telegram bots. Chosen for its solid architecture and community-driven development.
- **SQLAlchemy 2.0 (ORM)** – Declarative database models, clean relationship handling.
- **Alembic** – Automated schema migrations.
- **Pydantic v2** – For data validation, configuration (via `pydantic-settings`), and type safety.
- **Uvicorn** – A lightweight and high-performance ASGI server used to run asynchronous Python applications.

---

## 🧠 Development Philosophy

This project follows clear architectural and stylistic principles:

- **Separation of Concerns**: Logic is split across services, routers, models, and schemas. Each file and module has a single responsibility.
- **No Logic in Routes**: Routes only orchestrate; business logic lives in the `commons.services` layer.
- **Typed Everything**: Full type annotations are used across the project to improve readability, tooling support, and reduce runtime errors.
- **Commented Where It Matters**: All non-obvious logic is documented inline.
- **Consistent Code Style**:
  - Snake_case for functions and route names.
  - CamelCase for Pydantic models and ORM classes.
  - Single quotes for strings.
- **Scalability in Mind**: Though currently an MVP, the structure is built for future extension and feature growth.

---

## 🧑‍💻 Philosophy in Practice

While `vpnbot` serves a practical business need, it is also treated as a portfolio-quality project:

- Clean, minimal, and extensible.
- Easy for new contributors to understand and onboard.
- Clear documentation and consistent internal logic.

This approach ensures the project remains maintainable and professional — both as a business tool and as a technical showcase.

---

## 📂 Future Improvements

- Integration of payment gateways.
- Admin dashboard (possibly with FastAPI + frontend).
- Rate limiting, abuse protection, and logging improvements.
- Integration tests and deployment scripts.

---

*Maintained with ❤️ by the project author.*



