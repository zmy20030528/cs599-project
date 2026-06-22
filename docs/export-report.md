# 报告导出说明

1. 在 `CS599_大作业报告.md` 中检查个人信息、课程总结与真实 Trae CN 截图。
2. 安装 Matplotlib 与 Pillow，执行仓库内的无 GUI 构建脚本：

```bash
python scripts/generate_report_assets.py
python scripts/build_report_pdf.py
```

3. 构建脚本自动生成 A4 PDF、页码、目录和一级章节书签。用 PDF 阅读器打开导航窗格逐章点击核验。
4. 最终文件为 `docs/CS599_大作业报告.pdf`。
