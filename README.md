# 订阅解析与 VLESS 转换工具 (SubConverter)

一个基于 Python 和 Tkinter 构建的桌面端轻量级工具。专门用于解析特定加密格式的代理订阅链接，提取节点信息，并自动化重组为包含高级防封锁参数的 Clash YAML 配置以及标准 `vless://` 链接。


- **⚠️注意**：
-   ##### 解密方式

  自行获取自研客户端aes的key和iv。通过aes的key和iv可以解密配置文件。可以参考下方链接python代码

  [【教程分享】机场私有客户端转换Clash订阅链接](https://linux.do/t/topic/2456497)

- 一、需要获取订阅链接具体流程如下：

  ##### **方法一：登录抓包获取（通用流程）**

  1. 抓取登录接口
     ```
     POST /api/v1/passport/auth/login
     ```

  2. 获取用户信息
     ```
     GET /api/v1/user/info
     ```

  3. 获取订阅地址
     ```
     GET /api/v1/user/getSubscribe
     ```

  4. 得到订阅链接

     携带特定的请求头去访问上一步获取的地址，就能拿到加密后的订阅内容。

  5. 解密得到 Clash 配置
     用事先拿到的 AES 密钥和 IV 对内容解密，还原出标准订阅。

  ##### **方法二：本地数据库直接读取（推荐）**

  有些客户端的订阅链接会直接存在本地的数据库中，路径如下：

  - **Mac**：`/Users/你的用户名/Library/Application Support/[机场名称]/database.db`
  - **Windows**：`C:\Users\你的用户名\AppData\Roaming\[机场名称]\database.db`（文件名有可能是database.sqlite）

  用Letos等数据库工具打开数据库文件后，在profiles表中就能找到订阅链接，最简单省事。

## ✨ 核心特性

- **一键解密订阅**：内置 User-Agent 伪装，自动完成 `AES-128-CBC` 解密与 `Base64` 解码。
- **YAML 规范化与参数注入**：
  - 提取原始订阅中的 VLESS 节点，强制输出整洁的单行花括号风格（Flow Style）。
  - **自动补全高级防封锁参数**：智能注入 `client-fingerprint: chrome`、`xudp: true`、`tfo: true` 等参数，优化网络连通性与安全性。
- **协议无缝转换**：将 Clash YAML 格式的节点精准转换为通用 `vless://` 标准链接，方便导入 V2RayN、Shadowrocket 等客户端。
- **可视化操作 (GUI)**：基于 Tkinter 打造的直观双栏界面，左侧输出链接，右侧输出 YAML，底部提供实时运行日志，支持多线程防卡死。

## 🛠️ 环境依赖

在运行本项目之前，请确保您的电脑上已安装 Python 3.7 或更高版本。

项目依赖以下第三方库：
- `requests`：用于网络请求
- `pycryptodome`：用于 AES 加解密
- `pyyaml`：用于解析和构建 YAML 配置

## 🚀 安装与运行

**1. 克隆或下载本项目**

```bash
git clone https://github.com/KEVINJ1E/SubConverter.git
```

**2. 安装依赖**

```bash
pip install requests pycryptodome pyyaml
```

**3. 运行程序**

```bash
python main.py
```

**4. 提取订阅信息并转换**

[asailor的订阅转换](https://sub.asailor.org/) 进入该站点进行订阅转换



**更多**

自定义远程配置

```url
https://raw.githubusercontent.com/KEVINJ1E/Custom_OpenClash_Rules_OLDK/refs/heads/main/Custom_Clash.ini
```

[DNS泄露测试](https://ipleak.net/)

获取订阅信息

![image-20260724130425508](https://oss.111586.xyz/2026/07/638d59a9822c37b1957cc0b3e0d80d4965c23e156.png)

订阅转换配置截图

![image-20260724125928910](https://oss.111586.xyz/2026/07/39f7af710dacf4d42bb422279b64bf22abc64fb22.png)
