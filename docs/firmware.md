# Firmware notes (GR IIIx v1.60, `fwdc243b.bin`)

Official download `gr3x_v160.zip` (SHA-256
`19b5895fb3f48238852cdb74799ac28a6ba6ed5fbfccf442c19811f6612866d0`) contains
`fwdc243b.bin` (30,391,788 bytes, build "2025/09/25 11:30:50 JST",
git rev `438ff331`).

## Format

- Unencrypted. Header (0x80 bytes): `RICOH`, `GR IIIx`, `RICOH IMAGING COMPANY, LTD.`,
  model code `0x261` (= 609, the "KB609" used in file names such as `KB609.DOM`),
  build date `2025/09/25 11:30:50 JST`.
- From offset `0x80`: a Pentax/Ricoh-style LZ stream.
  `tools/pdec.py fwdc243b.bin out/s00.bin` decompresses it (59.7 MB; the block format
  is in the script's docstring).
- The decompressed image is a list of sections, each with a 16-byte header
  `char name[8]; u16 4; u16 index; u32 size;` followed by `size` bytes:

| Offset in s00 | Section | idx | Size | Content |
|---|---|---|---|---|
| `0x0` | (loader) | | `0x10860` | boot loader (`out/loader.bin`); contains the `BOOT` section below |
| `0xb318` | `BOOT` | 0 | `0x5538` | starts with ARM vectors |
| `0x10860` | `RTOS` | 1 | `0x10b55c0` | main RTOS, ARMv7, base `0x53000000` (`out/rtos.bin`) |
| `0x10c5e30` | `LINUX` | 5 | `0x2ebc00` | Linux kernel for the Wi-Fi/USB side (`lx/kernel.bin`) |
| `0x13b1a40` | `INITFS` | 6 | `0xd41800` | romfs ("-rom1fs-") for the Linux side; the userland in `rootfs/` was extracted from the Linux part (method not recorded, re-derive) |
| `0x20f3250` | `SRIC` | 2 | `0xc000` | sub-processor firmware |
| `0x20ff260` | `CPU` | | | sub-CPU data (different header type) |
| `0x211f270` | `SHELLCMD` | 3 | `0x9240` | shell command name table |
| `0x21284c0` | `ICONBIN` | 4 | `0x1181314` | UI icons |
| `0x32a97e4` | `FDRVPARA` | | | drive parameters, then the `A:`/`B:` resource drives (fonts, sounds, JPEGs) |

Drives seen in paths: `A:` / `B:` firmware resources, `C:` SD card,
`F:` internal flash file system (persistent settings `F:\KB609.DOM`).

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
- `tools/constref.py rtos.bin <const>`: same for 32-bit constants.
- `tools/userdata_values.py rtos.bin`: regenerates `data/userdata_set_values.tsv`.
- `tools/shell_usage.py rtos.bin data/shell_commands.tsv`: regenerates `data/shell_usage.tsv`.

Example:

```
analyzeHeadless gproj gr3x -process -noanalysis -readOnly \
  -scriptPath tools/ghs -postScript DecompRefs.java $PWD/out/q.c a:0x53008038
```

## Key addresses

Full list with names: [`data/symbols.tsv`](../data/symbols.tsv).

| What | Address |
|---|---|
| Shell command table | 584 `{name, handler}` entries (`SHELLCMD` section + handlers in RTOS) |
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

## Other interfaces

See [interfaces.md](interfaces.md): camctl commands, Wi-Fi HTTP API, Linux side, USB/MTP.
