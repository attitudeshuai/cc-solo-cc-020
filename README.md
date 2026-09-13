# 内容推荐与兴趣分析系统

按用户的浏览、点赞、评分行为，用协同过滤挑出更合口味的内容，并给运营方一套看数据与调参数的入口。

## How to Run

### 使用 Docker Compose 一键启动

```bash
docker-compose up --build -d
```

等待所有服务启动完成（约 2-3 分钟），即可访问系统。

### 停止服务

```bash
docker-compose down
```

### 清除数据重新启动

```bash
docker-compose down -v
docker-compose up --build -d
```

## Services

| 服务 | 地址 | 说明 |
|------|------|------|
| 管理后台 | http://localhost:8091 | 数据管理、可视化分析、算法原理 |
| 用户端 | http://localhost:8092 | 个性化推荐、新闻浏览、音乐播放 |
| 后端 API | http://localhost:5001 | Flask REST API |
| MySQL | localhost:3307 | 数据库 |
| Redis | localhost:6379 | 缓存 |

## 测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 管理后台登录 |
| 普通用户 | user1 | 123456 | 用户端登录 |
| 普通用户 | user2 | 123456 | 用户端登录 |
| ... | user3~user10 | 123456 | 更多测试用户 |

## 业务背景

内容库里的新闻和音乐越攒越多，首页按时间倒序排已经没意义：用户翻两屏就走了，编辑也不知道该把什么放到前面。系统要用用户自己的行为（浏览、点赞、评分）算出兴趣相近的人群，据此生成个人的内容列表，并在列表上说明这条为什么被推出来。

运营这边需要看两件事：行为分布在往哪走、推荐出去的内容有没有被点开；另外采集脚本会定时从订阅源拉新闻和音乐，拉回来要能去重、能停能手动跑。冷启动的用户没有行为记录，不能给他推空列表。

---

## 系统功能

### 推荐引擎（协同过滤）
- User-Based Collaborative Filtering（基于用户的协同过滤）
- 余弦相似度计算用户相似度矩阵
- 加权评分预测生成推荐列表
- 冷启动降级为热度推荐

### 管理后台
- 数据概览仪表盘（用户数、内容数、行为数统计）
- 用户管理（CRUD）
- 新闻管理（CRUD + 分类筛选）
- 音乐管理（CRUD + 风格筛选）
- 行为分析可视化（饼图、折线图、柱状图）
- 推荐效果分析（评分分布、算法分布、趋势）
- 用户相似度热力图
- 协同过滤算法原理详解
- 操作日志

### 用户端
- 个性化新闻推荐
- 个性化音乐推荐
- 新闻浏览与详情
- 音乐列表与播放
- 用户行为记录（浏览、点赞、评分）
- 协同过滤算法原理展示

### 技术栈
- Backend: Python 3.11 + Flask + SQLAlchemy + NumPy + SciPy + scikit-learn
- Frontend: Vue 3 + Vite + Ant Design Vue + ECharts
- Database: MySQL 8.0 + Redis
- Deploy: Docker + Docker Compose
