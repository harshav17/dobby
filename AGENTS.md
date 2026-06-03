# Agent Instructions

This repository is expected to be driven only by agents. Keep changes small, explicit, and easy for a human reviewer to inspect.

## Skills

Only use skills whose `SKILL.md` lives under `./.agents/skills/`.

Do not use skills from `$CODEX_HOME/skills`, `$CODEX_HOME/skills/.system`, plugins, remote repositories, or installed/global skills for work in this repository.

If a requested skill is not present under `./.agents/skills`, say it is unavailable locally. When using a skill, read `./.agents/skills/<skill-name>/SKILL.md` first.
