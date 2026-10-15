# Firmware notes (GR IIIx v1.60, `fwdc243b.bin`)

Official download `gr3x_v160.zip` (SHA-256
`19b5895fb3f48238852cdb74799ac28a6ba6ed5fbfccf442c19811f6612866d0`) contains
`fwdc243b.bin` (30,391,788 bytes, build "2025/09/25 11:30:50 JST",
git rev `438ff331`).

## Format

- Unencrypted. Pentax/Ricoh-style LZ stream starting at file offset `0x80`.
  `tools/pdec.py fwdc243b.bin out/s00.bin` decompresses it (block format is
  documented in the script's docstring).
- RTOS image: offset `0x10870` in the decompressed stream, length `0x10b55c0`,
  ARMv7 LE, base `0x53000000` (`out/rtos.bin`).
- Also inside: a Linux kernel + cpio rootfs for the Wi-Fi/BLE side (`lx/`,
  `rootfs/`; `mtpd` lives there), and a boot loader (`out/loader.bin`).

## Tooling

- Ghidra 12.1.4 headless, Raw Binary, `ARM:LE:32:v7:default`, base 0x53000000,
  `tools/ghs/Prep.java` as pre-script (aggressive instruction finder).
- `tools/ghs/DecompRefs.java <out> s:<string> | a:<addr> | n:<name> | c:<callee>`
  — decompile functions by string ref / address / name / callers.
- `tools/ghs/Dis.java <out> start:end` — disassembly ranges (use when the
  decompiler gives up, e.g. `FUN_5334688c`).
- `tools/ghs/Refs.java <out> addr[:n]` — references to addresses.
- `tools/ghs/CallUp.java` — walk callers upward with referenced strings.
- `tools/movref.py rtos.bin <string>` — find movw/movt + literal-pool references
  to a string (most string refs in this firmware are movw/movt pairs).
- `tools/constref.py rtos.bin <const>` — same for 32-bit constants.

Example:

```
analyzeHeadless gproj gr3x -process -noanalysis -readOnly \
  -scriptPath tools/ghs -postScript DecompRefs.java $PWD/out/q.c a:0x53008038
```

## Key addresses

| What | Address |
|---|---|
| Shell command table | 585 `{name, handler}` entries in the RTOS image |
| `UserData` shell | `0x53008038` → Get `FUN_53386230`, Set `FUN_5334688c` |
| UserData model accessor | `FUN_5320ad88` / `FUN_5320b31c` |
| Custom1 Standard saturation setter | `FUN_5325de5c(model, 0..8)` (via `0x532f2ccc`) |
| Custom2 base-effect Set branch | `0x532e8cf4` |
| `SYS_copylog` | `0x53042b34` → `FUN_536b98d0` (debug log), `FUN_536c1958` (exceptions) |
| `camprop_*_wo_linux` (crash) | `0x53013500`, `0x530135fc`, `0x53013730` |
| `camprop_get_setting/current` | `0x53013c34`, `0x53013dc4`; manager `FUN_533c43e8`, lookup `FUN_533c8498` |
| ModeSet parser | `FUN_536be850` (AnalyzeModeSetFile), `FUN_5383728c` |
| ModeSet tables | strings `0x538f2d94`, map `0x53b5b6a0` |
| Dev-item dispatch | `FUN_53290c58`; script flag `FUN_53290798`; debug-log flag `FUN_53290aa8` |
| TTL interpreter | keywords `FUN_538c343c`, dispatch `FUN_538c1258`, sendln `FUN_538c06ac`, errors `FUN_538c3148`, run loop `FUN_538bc080` |
| Debug log printf | `FUN_536b8150`, `FUN_536b82d4` |

## Other channels examined

- Wi-Fi HTTP API: can only select an effect (incl. Custom 1/2), not edit params.
- USB/MTP (`mtpd`): setters for saturation etc. exist but are dead code.
