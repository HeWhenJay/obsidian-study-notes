安装环境  python=3.11
# pip 安装
pip install graphrag
实战文本：《圣诞颂歌》
https://www.gutenberg.org/cache/epub/24022/pg24022.txt
input/book.txt
初始化，创建.env环境配置文件 和 settings.yaml项目配置文件
graphrag init --root D:\graghrag
配置环境变量，源码默认使用openai的模型，这里我们改成国产模型qwen-coder-plus，用qwen-max会报错TypeError: Object of type ModelMetaclass is not JSON serializable，可能需要改下提示词
在.env文件中填写qwen的API key，然后在settings.yaml中修改图片红色框的内容
![img.png](img.png)

构建索引(10分钟左右)
graphrag index --root D:\graghrag

运行
1.本地搜索：Local
graphrag query --root D:\graghrag  --method local --query "这个故事的主题是什么?"
2.Global
graphrag query --root D:\graghrag  --method global --query "这个故事主题是什么?"
3.DRIFT
graphrag query --root D:\graghrag  --method drift --query "这个故事主题是什么?"

