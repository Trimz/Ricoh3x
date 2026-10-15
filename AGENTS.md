# Instructions for AI agents working in this repo

You are working on a real camera owned by a real person, through undocumented
developer features. Before proposing any on-camera step:

1. Read `docs/SAFETY.md` in full. Its hard rules override convenience.
2. Confirm the camera runs firmware **1.60** (user checks MENU → Setup →
   Firmware Info/Options). Do not reuse addresses/keys on other versions.
3. You cannot see the camera. Ask the user what the screen shows and which
   files appeared; never report success the user hasn't confirmed.
4. Change one thing per power cycle, with marker lines written to the card.
5. Never use the commands listed as dangerous in SAFETY.md. Never modify or flash
   firmware. Never run factory/calibration (`ADJ_DAT_*`), format or erase commands.
6. Tell the user before anything that writes camera settings, and say which
   slot/setting will change so they can note the old value.
7. After a script has run once, remove it from the card.
7a. **Never bulk-write settings** (more than a handful) and never "restore" a whole export
   by script: it damaged the test camera (docs/incident-2026-10-15.md).
8. This repo is a knowledge base: record every finding in `docs/` and every
   on-camera run in `docs/test-log.md` (what was run, exact command, outcome).

The working interface for settings is `UserData Set <Item> <Value>` via
`sendln` in `script/startup.ttl`: see `docs/settings.md` and `data/userdata_set_values.tsv`.
