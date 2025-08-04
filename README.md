# 自动签到项目

一个基于 GitHub Actions 的自动签到工具，支持多个网站的定时自动签到功能。

## 🚀 功能特性

- **自动化签到**: 利用 GitHub Actions 定时调度，无需本地运行
- **多平台支持**: 目前支持 iKuuu 和 GLaDOS 等网站
- **安全可靠**: 使用 GitHub Secrets 安全存储敏感信息
- **易于扩展**: 模块化设计，方便添加新的签到网站
- **免费使用**: 基于 GitHub Actions，完全免费

## 📋 支持的网站

- [iKuuu](https://ikuuu.ch) - 机场服务
- [GLaDOS](https://glados.rocks) - 机场服务

## 🛠️ 安装配置

### 1. Fork 项目

点击右上角的 `Fork` 按钮，将此项目复制到你的 GitHub 账户。

### 2. 配置 Secrets

在你的 Fork 项目中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下环境变量：

#### SSPANEL_CONFIG_JSON
```json
{
  "url": "https://your-sspanel-site.com",
  "accounts": [
    {
      "email": "user1@example.com",
      "password": "password1"
    },
    {
      "email": "user2@example.com",
      "password": "password2"
    }
  ]
}
```

#### GLADOS_CONFIG_JSON
```json
{
  "cookies": [
    "cookie1=value1; cookie2=value2; cookie3=value3",
    "cookie4=value4; cookie5=value5; cookie6=value6"
  ]
}
```

#### NOTIFY_CONFIG_JSON
```json
{
  "server_chan": {
    "sckey": "your_server_chan_key"
  },
  "pushplus": {
    "token": "your_pushplus_token"
  }
}
```

> 💡 **提示**: 所有配置都使用JSON格式，确保JSON语法正确，不要包含注释。

### 3. 启用 Actions

确保 GitHub Actions 已启用：
- 进入 `Actions` 标签页
- 点击 `I understand my workflows, go ahead and enable them`

## ⚙️ 使用方法

### 自动运行

项目配置了 GitHub Actions 工作流，会在以下时间自动执行签到：

- **每日签到**: 每天早上 8:00 (UTC+8)
- **每周签到**: 每周一早上 9:00 (UTC+8)

### 手动运行

你也可以手动触发签到：

1. 进入 `Actions` 标签页
2. 选择 `Auto Checkin` 工作流
3. 点击 `Run workflow` 按钮
4. **指定签到器**（可选）：
   - 在 `要执行的签到器` 输入框中填写签到器名称
   - 支持多个签到器，用逗号分隔，例如：`SSPanel,GLaDOS`
   - 留空则执行所有可用的签到器
   - 当前支持的签到器：`SSPanel`、`GLaDOS`

### 查看运行结果

- 在 `Actions` 标签页查看运行历史
- 点击具体的运行记录查看详细日志
- 成功签到会显示相应的成功信息

## 🔧 自定义配置

### 修改签到时间

编辑 `.github/workflows/runner.yml` 文件中的 `cron` 表达式：

```yaml
# 每天上午 8:00 执行 (UTC+8)
- cron: '0 0 * * *'

# 每周一上午 9:00 执行 (UTC+8)
- cron: '0 1 * * 1'
```

### 添加新的签到网站

1. 在 `checkin.py` 中添加新的签到函数
2. 在 GitHub Secrets 中添加相应的配置
3. 更新工作流配置

## 🐛 故障排除

### 常见问题

1. **签到失败**
   - 检查邮箱和密码是否正确
   - 确认网站服务是否正常
   - 查看 Actions 日志获取详细错误信息

2. **Actions 未运行**
   - 确认已启用 GitHub Actions
   - 检查工作流文件语法是否正确
   - 确认 Secrets 配置完整

3. **权限问题**
   - 确保 Fork 的项目有 Actions 权限
   - 检查 GitHub 账户设置

### 获取帮助

如果遇到问题，可以：

1. 查看 Actions 运行日志
2. 检查 GitHub Secrets 配置
3. 提交 Issue 描述问题

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持 iKuuu 自动签到
- 支持 GLaDOS 自动签到
- 基于 GitHub Actions 的定时调度

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

- 本项目仅供学习和个人使用
- 请遵守相关网站的服务条款
- 使用本工具产生的任何后果由用户自行承担
- 建议合理使用，避免对目标网站造成压力

## 🌟 致谢

感谢以下开源项目和服务：

- [lichang_checkin](https://github.com/bighammer-link/jichang_checkin)
- [GlaDOS_checkin_auto](https://github.com/domeniczz/GLaDOS_checkin_auto)

---

如果这个项目对你有帮助，请给个 ⭐️ 支持一下！