# microduck-journey · 小鸭复刻之旅

一个硬件零基础选手复刻 [Microduck](https://github.com/pollen-robotics/microduck) 机器鸭的全程日志仓——按天记进度、按条记踩坑、按单打订单。

**上游致谢**：
- 官方项目：[pollen-robotics/microduck](https://github.com/pollen-robotics/microduck)（XL330 版）· [apirrone/microduck_rl](https://github.com/apirrone/microduck_rl)（强化学习训练）
- 中文复刻主仓：[fanhao375/microduck-replica](https://github.com/fanhao375/microduck-replica)（文档/BOM/镜像/Studio）
- CAD 图纸仓：[fanhao375/microduck-replica-cad](https://github.com/fanhao375/microduck-replica-cad)（SolidWorks 图纸/装配说明书/打印工程）

## 仓里有什么

| 文件 | 是什么 |
|---|---|
| [复现计划.md](复现计划.md) | 总计划：采购清单（带作者实链）、里程碑、上游动态同步 |
| [进度日志.md](进度日志.md) | 按天倒序的进度流水 + 当前状态快照表 |
| [我们的踩坑记录.md](我们的踩坑记录.md) | 自己踩的坑：采购 / 文件流程 / 认知三类，每条含根因与正确做法 |
| [打印下单问题总结与淘宝代打防坑指南.md](打印下单问题总结与淘宝代打防坑指南.md) | 嘉立创拒单复盘 + 淘宝代打话术 + 到货验收单 |
| [舵机配ID第一天checklist.md](舵机配ID第一天checklist.md) | 飞特 HD-1910 ×15 配 ID 实操清单（URT-2 版） |
| [装配说明书-文字批注版.md](装配说明书-文字批注版.md) | 21 页装配 PDF 的文字批注版 |
| [仿真入门.md](仿真入门.md) / [仿真看鸭.py](仿真看鸭.py) | MuJoCo 里先看虚拟鸭 |
| `_破面溯源.txt` / `_mesh_audit.py` | 网格缺陷溯源审计：证据与方法（面数指纹对接法） |
| `_3mf清单.txt` | 打印工程 6 盘 43 件的零件清单（实打 PLA 35 + TPU 2） |

## 硬件方案

飞特 HD-1910-C001 舵机 ×15 + Radxa Zero 3W（无 eMMC，microSD 启动）+ 飞线派（无 HAT）。
打印：淘宝桌面 FDM 代打（作者实买店，整套 ¥131）+ 嘉立创 TPU 2 件。

## 记录约定

- 进度追加到 `进度日志.md`：一天一节，倒序，新在上
- 踩坑追加到 `我们的踩坑记录.md`：日期 · 现象 → 根因 → 正确做法
- 上游克隆仓不入本仓（.gitignore 已排除），只引用不复制

> 人人都可以拥有属于自己的 MicroDuck 🦆
