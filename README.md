# AI 生成代码检测工具

截至 2026 年 11 月 11 日，市面上已有用于判断代码是否由 AI 生成的在线工具。不过，检测结果只能作为参考，不能单独证明代码的来源。

## 工具示例

| 工具 | 用途 |
| --- | --- |
| [ZeroTell AI Code Detector](https://zerotell.com/ai-detection/ai-code-detector) | 分析代码中的 AI 生成特征，提供判断线索。 |
| [OmniDetect](https://www.omnidetect.ai/ai-code-detector) | 检测代码是否呈现 AI 生成风格；官网说明代码检测比普通文本更不确定。 |
| [TextSight](https://www.textsight.ai/tools/code-ai-detector/) | 根据注释、命名、格式和模板结构等特征进行判断。 |

以上用途依据工具官网说明整理，未对这些产品进行独立准确率测试。

## 可靠性

有检测工具不等于能准确证明代码由 AI 编写。相关研究发现，现有检测工具在代码检测上的表现和泛化能力仍有限。实验中的效果不能直接代表它在任意真实项目中的准确率。

研究参考：[An Empirical Study on Automatically Detecting AI-Generated Source Code: How Far Are We?](https://arxiv.org/abs/2411.04299)

## 使用建议

- **个人参考**：可以查看工具标出的可疑特征，但不要仅凭分数下结论。
- **作业、面试或工作审核**：结合提交历史、编写过程和作者现场解释代码的能力进行判断。
- **理解检测分数**：“AI 率 90%”不一定表示 90% 的代码由 AI 编写，具体含义取决于工具的评分定义。
