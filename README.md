<!-- Yata-Datacom · GitHub Profile · nord palette · English page (中文页：README.zh-CN.md) -->

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/banner-light.svg">
  <img src="./assets/banner.svg" alt="Yata-Datacom — Networks, Automation, Embedded, Cloud Native" width="100%" />
</picture>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=88C0D0&center=true&vCenter=true&width=640&lines=Networks+%C2%B7+Automation+%C2%B7+Embedded;Cloud+Native+%C2%B7+and+what%27s+next;Turning+ideas+into+tools">
  <source media="(prefers-color-scheme: light)" srcset="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=5E81AC&center=true&vCenter=true&width=640&lines=Networks+%C2%B7+Automation+%C2%B7+Embedded;Cloud+Native+%C2%B7+and+what%27s+next;Turning+ideas+into+tools">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=88C0D0&center=true&vCenter=true&width=640&lines=Networks+%C2%B7+Automation+%C2%B7+Embedded;Cloud+Native+%C2%B7+and+what%27s+next;Turning+ideas+into+tools" alt="typing" />
</picture>

### Hi, I'm Yata 👋

**I build tools for networks and systems — and whatever piece of hardware is on the bench.**

<sub>[**English**](README.md) · [**简体中文**](README.zh-CN.md)</sub>

<br/>

<a href="https://github.com/Yata-Datacom?tab=repositories"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Fusers%2FYata-Datacom&query=%24.public_repos&label=Repositories&style=for-the-badge&color=5E81AC&logo=github&logoColor=white" alt="repositories" /></a>
<img src="https://img.shields.io/badge/Networks-81A1C1?style=for-the-badge&logoColor=white" alt="networks" />
<img src="https://img.shields.io/badge/Automation-81A1C1?style=for-the-badge&logo=githubactions&logoColor=white" alt="automation" />
<img src="https://img.shields.io/badge/Embedded-8FBCBB?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="embedded" />
<img src="https://img.shields.io/badge/Cloud%20Native-88C0D0?style=for-the-badge&logo=kubernetes&logoColor=white" alt="cloud native" />

<br/>

<img src="./assets/chibi-whale.svg" width="132" alt="a little blue whale" />

</div>

<img src="./assets/divider.svg" width="100%" alt="" />

## 🧰 Toolbox

| Project | What it does | Stack |
| :-- | :-- | :-- |
| **[Network Inspection Tool · GUI Edition](https://github.com/Yata-Datacom/Network-Device-Server-Inspection-Tool-GUI-Edition)** | SSH-based automated inspection for network devices & Linux servers — anomaly flagging, config backup, report export, connection profiles. | `Python` `SSH` `GUI` |
| **[NADT — Network Automation Deployment Tool](https://github.com/Yata-Datacom/NADT-Network-Automation-Deployment-Tool)** | 🚧 Preview — vendor-agnostic zero-touch provisioning for switches (DHCP option 66/67 + TFTP), driven by a macro workbook. | `Python` `asyncio` `TFTP` `SQLite` |
| **[Traffic Load Tester — Gateway Stress Tool](https://github.com/Yata-Datacom/Traffic-Load-Tester---Gateway-Stress-Tool)** | High-concurrency gateway / server traffic testing over TCP + UDP, with live PPS and bandwidth monitoring. | `Python` `Sockets` `GUI` |
| **[DSH Portable · DeepSeek Harness launcher](https://github.com/Yata-Datacom/DeepSeekHarness-Portable)** | Green portable launcher for DeepSeek Harness — unzip, double-click, run; OS preflight, never overwrites by default, clean uninstall, ships zero API keys. | `PowerShell` `WinForms` `Node.js` |

> The three inspection / automation tools ship with `pytest` suites + GitHub Actions (multi-OS tests, lint, Windows build artifacts); the portable launcher ships its own environment-isolation verifier.

<img src="./assets/divider.svg" width="100%" alt="" />

## 🏅 Certifications

<div align="center">
<img src="./assets/badges/huawei-hcie.png" height="110" alt="Huawei Certified ICT Expert (HCIE)" title="Huawei Certified ICT Expert (HCIE)" />
<img src="./assets/badges/huawei-hcip.png" height="110" alt="Huawei Certified ICT Professional (HCIP)" title="Huawei Certified ICT Professional (HCIP)" />
<!-- credly-badges:start -->
<img src="./assets/badges/credly-1.png" height="110" alt="Advanced System Administrator in Ansible" title="Red Hat Certified Advanced System Administrator in Ansible · Red Hat" />
<img src="./assets/badges/credly-2.png" height="110" alt="Engineer in Ansible" title="Red Hat Certified Engineer in Ansible · Red Hat" />
<img src="./assets/badges/credly-3.png" height="110" alt="System Administrator (RHCSA)" title="Red Hat Certified System Administrator (RHCSA) · Red Hat" />
<!-- credly-badges:end -->
</div>

<img src="./assets/divider.svg" width="100%" alt="" />

## 🎯 Interests & what's next

| Area | What I work with |
| :-- | :-- |
| **Networks & protocols** | SSH · DHCP / ZTP · TFTP · SNMP · routing & switching · **SDN** |
| **Automation & tooling** | Python · Rust · PowerShell · pytest · GitHub Actions |
| **Embedded & hardware** | Linux on small boards & mini PCs · microcontrollers · **SDR** |
| **Cloud native & low level** | Docker / Podman · Kubernetes · **eBPF** & observability |
| **Exploring next** | the list keeps growing — if it runs code, it is probably interesting |

<img src="./assets/divider.svg" width="100%" alt="" />

## 💡 How I work

- 🔧 **Turn repetition into tools** — if I've typed it by hand a third time, it deserves a UI and a one-click export.
- 🧪 **Tests as a safety net** — lock the current behaviour with cases before refactoring; every fixed bug becomes a regression assertion.
- 🔌 **Standards over lock-in** — prefer open protocols and plain formats over anything that traps you in one vendor.
- 📦 **Deliverables must be self-contained** — one exe, one README, one checklist; whoever gets it can run it.

<img src="./assets/divider.svg" width="100%" alt="" />

<div align="center">

<img src="https://komarev.com/ghpvc/?username=Yata-Datacom&style=for-the-badge&color=5E81AC&label=PROFILE+VIEWS" alt="views" />

<sub>⭐ If one of these tools saved you some time, a star goes a long way.</sub>

</div>
