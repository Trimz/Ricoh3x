# Other interfaces: camctl, Wi-Fi HTTP API, Linux side, USB/MTP

The GR IIIx has two processors: the main RTOS (camera, menus, settings; where
everything in this repo runs) and an embedded **Linux** side that handles Wi-Fi,
Bluetooth and USB. They talk over IPCU mailboxes (`ipcu_*` shell commands).

## camctl: camera control commands

`camctl_*` shell commands are the RTOS end of the remote-control path used by the
Wi-Fi app (Linux `camctld` → IPCU → RTOS). They can be called from a script with
`sendln` like any shell command. **None have been tested.** They act on the
*live* camera state (shooting, power, radio), so treat them like button presses.
Settings changes are cleaner through `UserData Set` (settings.md).

**Why camctl is not tested:** every `camctl_*` request goes through a sender object
(`FUN_533b27c8()+4` → `FUN_533b3e30`) whose pointer is initialised to 0 and is never written
anywhere in the RTOS image. It is most likely only valid while a Wi-Fi app session is up. Called
from a script it would dereference NULL like `camprop_*_wo_linux`, and a crash in
`startup.ttl` blocks boot. Use `UserData Set` instead.

Notables: `camctl_capture start|stop` / `camctl_af` (shoot / autofocus),
`camctl_power off`, `camctl_set_still_image_ctrl <custom no> <effect>` (selects
only the effect of a slot, no parameters).

Usage text extracted by `tools/shell_usage.py` ([data/shell_usage.tsv](../data/shell_usage.tsv)):

| Command | Description | Arguments |
|---|---|---|
| `camctl_get_rlv_stat` | get remoe liveview state. |  |
| `camctl_get_rlv_size` | get remote liveview size. |  |
| `camctl_get_wlan_ssid` | get wlan ssid |  |
| `camctl_get_wlan_psk` | get wlan passkey. |  |
| `camctl_get_wlan_ch` | get wlan channel. |  |
| `camctl_get_ble_devname` | get ble device name. |  |
| `camctl_set_rlv_size` | set remote liveview size. | <width : 720/1080> <height : 480/720> |
| `camctl_set_wlan_ssid` | set wlan ssid. | <ssid> |
| `camctl_set_wlan_psk` | set wlan passkey. | <passkey> |
| `camctl_set_wlan_ch` | set wlan channel. | <ch : 1- 11> |
| `camctl_set_ble_devname` | set ble device name. | <device name> |
| `camctl_wakeup` | wake up from sleep. |  |
| `camctl_cancel_selftimer` | cancel self timer. |  |
| `camctl_set_time` | set camera date time. | <year> <month> <day> <hour> <minute> <second> |
| `camctl_set_aperture` | set aperture. | <aperture : apex> |
| `camctl_set_shutter` | set shuter speed. | <shutter speed : apex> |
| `camctl_set_iso` | set iso sensitivity. | <iso sensitivity: apex> |
| `camctl_set_exp_comp` | set exposure compensation. | <exposure compensation : apx> |
| `camctl_set_bulb_timer` | set exposure time for bulb timer mode. | <exposure time in seconds> |
| `camctl_set_auto_resize` | set auto resize. | <value : on/off> |
| `camctl_get_time` | get system time. |  |
| `camctl_get_battery` | get battery level. |  |
| `camctl_get_geotag` | get geotag setting. |  |
| `camctl_get_ble_mode` | get ble mode. |  |
| `camctl_get_wlan_mode` | get wlan mode. |  |
| `camctl_get_transfer_power_off` | get file-transfer setting at power off. |  |
| `camctl_get_drive_mode` | get drive mode. |  |
| `camctl_get_self_time` | get self-timer time in second. |  |
| `camctl_get_self_state` | get self-timer state. |  |
| `camctl_get_expmode` | get exposure mode. |  |
| `camctl_get_usermode` | get user mode. |  |
| `camctl_get_still_movie` | check still or movie. |  |
| `camctl_get_movie_state` | get movie state. |  |
| `camctl_get_still_file_format` | get still file format. |  |
| `camctl_get_still_resolution` | get still resolution. |  |
| `camctl_get_still_aspectratio` | get still aspect ratio. |  |
| `camctl_get_aperture` | get aperture. |  |
| `camctl_get_shutter` | get shutter. |  |
| `camctl_get_iso` | get iso sensitivity. |  |
| `camctl_get_exp_comp` | get exposure compensation. |  |
| `camctl_get_still_focus_mode` | get still focus mode. |  |
| `camctl_get_movie_framerate` | get movie framerate. |  |
| `camctl_get_movie_focus_mode` | get movie focus mode. |  |
| `camctl_get_focus_state` | get focus state. |  |
| `camctl_get_iso_auto` | get iso auto. |  |
| `camctl_get_bulb_mode` | get bulb mode. |  |
| `camctl_get_bulb_timer` | get exposure time for bulb timesetir mode. |  |
| `camctl_get_still_image_ctrl` | get sitll image control. |  |
| `camctl_get_movie_image_ctrl` | get movie image control. |  |
| `camctl_get_camera_mode` | get camera mode. |  |
| `camctl_get_auto_resize` | get auto resize. |  |
| `camctl_get_shutter_button_setting` | get shutter button setting. |  |
| `camctl_av_list` | display av list. |  |
| `camctl_tv_list` | display tv list. |  |
| `camctl_sv_list` | display sv list. |  |
| `camctl_xv_list` | display xv list. |  |
| `camctl_set_av_cp` | set aperture direct (for debug). |  |
| `camctl_set_tv_cp` | set tv direct (for debug). |  |
| `camctl_set_sv_cp` | set sv direct (for debug). |  |
| `camctl_set_xv_cp` | set xv direct (for debug). |  |
| `camctl_ctl_rlv` | control remote liveview. | <on/off> |
| `camctl_capture` | start/stop capture. |  |
| `camctl_af` | execute auto focus. |  |
| `camctl_power` | execute power control. | <control : off> |
| `camctl_stop_interval` | stop interval. | <option : wait_exp/cancel_exp> |
| `camctl_multiexp` | control multi exposure. | <control : next/retry/finish> |
| `camctl_set_geotag` | set geo tagging setting. | <setting : on/off> |
| `camctl_set_ble_mode` | set ble mode. | <setting : always/on/off> |
| `camctl_set_wlan_mode` | set wlan mode. | <setting : on/off> |
| `camctl_set_transfer_power_off` | set image transfer setting at power off. | <setting : wait/stop> |
| `camctl_set_drive_mode` | set drive mode. | <mode : single/cont/bracket/mexp/interval/intervalexp> |
| `camctl_set_self_time` | set self-timer time in second. | <time : 0/2/10> |
| `camctl_set_expmode` | set exposure mode. | <mode : p/tv/av/m> |
| `camctl_set_still_movie` | change still or movie. | <mode : still/movie> |
| `camctl_set_still_file_format` | set still file format. | <format : jpeg/raw/raw_p> |
| `camctl_set_still_resolution` | set still resolution. | <resolution : large/middle/small/xsmall> |
| `camctl_set_still_aspectratio` | set still aspect ratio. | <aspect ratio : 1:1/3:2> |
| `camctl_set_still_metering_mode` | set still metering mode. | <metering mode : multi/center/spot/highlight> |
| `camctl_set_still_wb` | set still wb. | <wb : auto/multi/sun/shade/cloud/flu_d/flu_n/flu_w/flu_l/ lamp/cte/man/coltmp/c1/c2/c3> |
| `camctl_set_still_focus_mode` | set still focus mode. | <focus mode : autoarea/zone/select/pin/follow/cont/mf/snap/inf> |
| `camctl_set_movie_framerate` | set movie frame rate. | <movie frame rate : 60/30/24> |
| `camctl_set_movie_metering_mode` | set movie metering mode. | <metering mode : multi/center/spot/highlight> |
| `camctl_set_movie_wb` | set movie wb mode. | <wb : auto/sun/shade/cloud/flu_d/flu_n/flu_w/flu_l/ lamp/cte/man/coltmp/c1/c2/c3> |
| `camctl_set_movie_focus_mode` | set movie focus mode. | <focus mode : af/mf/snap/inf> |
| `camctl_set_iso_auto` | set iso auto. | <iso auto : on/off> |
| `camctl_set_bulb_mode` | set bulb mode. | <bulb mode : off/bulb/bulbtimer/time> |
| `camctl_set_still_image_ctrl` | set still image control. | <custom no : 0/1/2> <image control : std/vivid/mono/smono/hmono/hicon/posi/bleach/retro/hdr> |
| `camctl_set_movie_image_ctrl` | set movie image control. | <custom no : 0/1/2> <image control : std/vivid/mono/hmono/hicon/posi/bleach/retro> |
| `camctl_set_camera_mode` | set camera mode. | <mode : shooting/playback> |
| `camctl_get_still_metering_mode` | get still metering mode. | <type : config/effective> |
| `camctl_get_still_wb` | get still wb | <type : config/effective> |
| `camctl_get_movie_metering_mode` | get movie metering mode. | <type : config/effective> |
| `camctl_get_movie_wb` | get movie wb. | <type : config/effective> |

## Wi-Fi HTTP API (`webapid`, Linux side)

Served by `/usr/bin/webapid` (a C++ "webapi-server"). Endpoints found in the binary's strings (`?` = method not present next to the path):

| Method | Path |
|---|---|
| GET | `/v1/ping` |
| GET | `/v1/props` (camera state) |
| GET | `/v1/photos`, `/v1/photos/infos`, `/v1/photos/{dir}/{file}`, `/v1/photos/{dir}/{file}/info` |
| PUT | `/v1/photos/{dir}/{file}/transfer` |
| GET | `/v1/transfers` |
| GET | `/v1/liveview` |
| PUT | `/v1/params/camera`, `/v1/params/device`, `/v1/params/lens` |
| ? | `/v1/camera/shoot`, `/v1/camera/shoot/cancel`, `/v1/camera/shoot/compose` |
| ? | `/v1/lens/focus` |
| ? | `/v1/device/finish`, `/v1/device/wlan/finish` |
| WS | `/v1/changes` (event websocket) |

Camera parameters seen in the binary: `aspectRatio`, `captureMode`, `effect`,
`exposureMode`, `focusMode`, `meteringMode`, `operationMode`, `shootMode`,
`stillFormat`, `stillSize`, `WBMode`, plus state `battery`, `focused`,
`focusSetting`, `storages`. `effect` can select an Image Control (including
Custom 1/2) but there is **no way to edit Image Control parameters** over Wi-Fi.
These map onto the `camctl_*` commands above.

## Linux side

Root filesystem (from the `INITFS` section, see firmware.md): systemd/busybox
userland. Camera-specific daemons in `/usr/bin`: `webapid` (HTTP API), `camctld`
(camera control bridge to the RTOS), `mtpd` (USB MTP), `usbd`, `netmgrd`,
`sysmgrd`, `bled` (Bluetooth LE), `hostapd`/`udhcpd` (access point), plus
`start_wlan.sh` / `stop_wlan.sh` / `usb30dev_mtp_func*.sh`. Shell commands
`llog_export` (copies Linux logs to `C:\linux%02d.log`), `wait_linux_boot`,
`is_linux_boot` and the `ipcu_*` family talk to it.

## USB / MTP (`mtpd`)

`mtpd` contains handlers for vendor properties (saturation and similar), but the
setters are unreachable (dead code) in this build. USB offers no settings access.
