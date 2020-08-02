# ProxyPoolSystem
这是个简单的代理池管理系统，仅供学习参考！

该项目是一个Web前后端与爬虫相结合的项目。

## 技术栈

- 前端：Bootstrap
- 后端：Python -> Flask框架
- 数据库：Redis -> Set
- 数据渲染：Vue.js + jQuery

## 项目结构

- requirements.txt

    本人当前环境的所有Python库，虽然很多，但在该项目中并没有用到几个

- main.py
    
    程序入口，可直接运行启动

- settings.py

    一些配置信息

- crawler.py

    里面包含4个类，这4个类为该代理池系统的核心逻辑

- api.py

    该模块为系统的视图或接口模块

- /page/

    该文件夹下存放html页面

- /static/

    该文件夹下存放Css、Js、Images等静态文件
