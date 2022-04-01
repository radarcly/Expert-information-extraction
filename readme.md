# 人才信息抽取
## 项目简介
人才信息抽取主要内容为从一段人才简介中，抽取包含姓名，机构，出生日期，国籍，研究方向，学科领域，职称，职务，部门，个人主页等二十余项人才基本信息以及工作经历，教育经历，荣誉经历三种复杂信息。

人才信息抽取模型支持中英文输入，利用自然语言处理中序列标注技术，采取预训练模型加微调的思路进行训练。同时针对复杂信息中的多值问题进行了工程化处理

## 目录结构
模型代码文件夹 bert_ner

解码代码文件夹 info

训练集生成代码 tagging.py

模型训练代码   run_ner.py

模型预测代码   predict.py

结果文件生成   generate.py

输入参数规范   input_specification.docx

输出参数规范   output_specification.docx

输入示例       input_sample.json

输出示例       output_sample.json      



