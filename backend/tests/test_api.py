"""
个性化推荐系统 - 全接口测试用例
测试目标：
  1. 所有接口返回正确的 code/msg/data 结构
  2. 不会返回 500 系统错误，所有错误均有友好中文提示
  3. 权限控制正确（普通用户不能访问管理接口）
  4. CRUD 操作完整性验证

运行方式：
  # 在容器内运行（推荐）：
  docker-compose exec backend python -m pytest tests/test_api.py -v
  
  # 在宿主机运行：
  TEST_API_URL=http://localhost:5001/api pytest backend/tests/test_api.py -v
"""
import pytest
import requests
import random
import string
import os

# 容器内默认使用 localhost:5000，宿主机运行时通过环境变量指定
BASE_URL = os.environ.get("TEST_API_URL", "http://localhost:5000/api")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_str(n=8):
    return ''.join(random.choices(string.ascii_lowercase, k=n))


def assert_ok(resp, msg_prefix=""):
    """断言请求成功且不是 500"""
    assert resp.status_code != 500, f"{msg_prefix} 返回了500系统错误: {resp.text}"
    data = resp.json()
    assert 'code' in data, f"{msg_prefix} 响应缺少 code 字段"
    return data


def assert_success(resp, msg_prefix=""):
    """断言请求成功 code=200"""
    data = assert_ok(resp, msg_prefix)
    assert data['code'] == 200, f"{msg_prefix} 期望 code=200, 实际 code={data['code']}, msg={data.get('msg')}"
    return data


def assert_error(resp, expected_code, msg_prefix=""):
    """断言请求返回预期的错误码，且有友好提示"""
    data = assert_ok(resp, msg_prefix)
    assert data['code'] == expected_code, \
        f"{msg_prefix} 期望 code={expected_code}, 实际 code={data['code']}"
    assert 'msg' in data and len(data['msg']) > 0, \
        f"{msg_prefix} 错误响应缺少友好提示信息"
    return data


def auth_header(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def admin_token():
    """获取管理员 token"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    data = assert_success(resp, "管理员登录")
    return data['data']['token']


@pytest.fixture(scope="module")
def user_token():
    """获取普通用户 token"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "user1", "password": "123456"})
    data = assert_success(resp, "普通用户登录")
    return data['data']['token']


# ===========================================================================
# 1. 认证模块 (Auth)
# ===========================================================================

class TestAuth:
    """认证相关接口测试"""

    def test_login_success(self):
        """正常登录"""
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
        data = assert_success(resp, "登录")
        assert 'token' in data['data'], "登录成功应返回 token"
        assert 'user' in data['data'], "登录成功应返回 user 信息"

    def test_login_wrong_password(self):
        """密码错误"""
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "wrong"})
        data = assert_error(resp, 401, "密码错误")
        assert '密码' in data['msg'] or '错误' in data['msg'], "应提示密码错误"

    def test_login_nonexistent_user(self):
        """不存在的用户"""
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "no_such_user_xyz", "password": "123"})
        data = assert_error(resp, 401, "不存在的用户")

    def test_login_missing_fields(self):
        """缺少必填字段"""
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin"})
        data = assert_error(resp, 400, "缺少密码字段")

    def test_login_empty_body(self):
        """空请求体"""
        resp = requests.post(f"{BASE_URL}/auth/login", json={})
        data = assert_error(resp, 400, "空请求体")

    def test_register_success(self):
        """正常注册"""
        username = f"test_{rand_str()}"
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username, "password": "test123", "nickname": "测试用户"
        })
        data = assert_success(resp, "注册")
        assert data['data']['username'] == username

    def test_register_duplicate(self):
        """重复用户名"""
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "username": "admin", "password": "123456"
        })
        data = assert_error(resp, 400, "重复注册")
        assert '已存在' in data['msg'], "应提示用户名已存在"

    def test_register_missing_fields(self):
        """注册缺少必填字段"""
        resp = requests.post(f"{BASE_URL}/auth/register", json={"username": "abc"})
        data = assert_error(resp, 400, "注册缺少密码")

    def test_profile_with_token(self, user_token):
        """携带 token 获取个人信息"""
        resp = requests.get(f"{BASE_URL}/auth/profile", headers=auth_header(user_token))
        data = assert_success(resp, "获取个人信息")
        assert 'username' in data['data'], "应返回用户信息"

    def test_profile_without_token(self):
        """不携带 token 获取个人信息"""
        resp = requests.get(f"{BASE_URL}/auth/profile")
        assert resp.status_code != 500, "不应返回500"
        data = resp.json()
        # flask-jwt-extended 可能返回 msg 而非 code
        assert resp.status_code in (401, 422) or data.get('code') in (401, 422), \
            "未授权应返回 401 或 422"


# ===========================================================================
# 2. 新闻模块 (News)
# ===========================================================================

class TestNews:
    """新闻相关接口测试"""

    def test_list_news(self, user_token):
        """获取新闻列表"""
        resp = requests.get(f"{BASE_URL}/news", headers=auth_header(user_token))
        data = assert_success(resp, "新闻列表")
        assert 'items' in data['data'] or 'list' in data['data'] or isinstance(data['data'], dict), \
            "应返回分页数据"

    def test_list_news_with_pagination(self, user_token):
        """分页获取新闻"""
        resp = requests.get(f"{BASE_URL}/news?page=1&per_page=5", headers=auth_header(user_token))
        data = assert_success(resp, "新闻分页")

    def test_list_news_with_category(self, user_token):
        """按分类筛选新闻"""
        resp = requests.get(f"{BASE_URL}/news?category=科技", headers=auth_header(user_token))
        data = assert_success(resp, "新闻分类筛选")

    def test_list_news_with_keyword(self, user_token):
        """按关键词搜索新闻"""
        resp = requests.get(f"{BASE_URL}/news?keyword=中国", headers=auth_header(user_token))
        data = assert_success(resp, "新闻关键词搜索")

    def test_get_news_detail(self, user_token):
        """获取新闻详情"""
        resp = requests.get(f"{BASE_URL}/news/1", headers=auth_header(user_token))
        data = assert_success(resp, "新闻详情")
        assert 'title' in data['data'], "新闻详情应包含 title"

    def test_get_news_not_found(self, user_token):
        """获取不存在的新闻"""
        resp = requests.get(f"{BASE_URL}/news/99999", headers=auth_header(user_token))
        data = assert_error(resp, 404, "新闻不存在")
        assert '不存在' in data['msg'], "应提示新闻不存在"

    def test_list_news_without_token(self):
        """未登录获取新闻列表"""
        resp = requests.get(f"{BASE_URL}/news")
        assert resp.status_code != 500, "不应返回500"


# ===========================================================================
# 3. 音乐模块 (Music)
# ===========================================================================

class TestMusic:
    """音乐相关接口测试"""

    def test_list_music(self, user_token):
        """获取音乐列表"""
        resp = requests.get(f"{BASE_URL}/music", headers=auth_header(user_token))
        data = assert_success(resp, "音乐列表")

    def test_list_music_with_pagination(self, user_token):
        """分页获取音乐"""
        resp = requests.get(f"{BASE_URL}/music?page=1&per_page=5", headers=auth_header(user_token))
        data = assert_success(resp, "音乐分页")

    def test_list_music_with_genre(self, user_token):
        """按流派筛选音乐"""
        resp = requests.get(f"{BASE_URL}/music?genre=流行", headers=auth_header(user_token))
        data = assert_success(resp, "音乐流派筛选")

    def test_list_music_with_keyword(self, user_token):
        """按关键词搜索音乐"""
        resp = requests.get(f"{BASE_URL}/music?keyword=夜", headers=auth_header(user_token))
        data = assert_success(resp, "音乐关键词搜索")

    def test_get_music_detail(self, user_token):
        """获取音乐详情"""
        resp = requests.get(f"{BASE_URL}/music/1", headers=auth_header(user_token))
        data = assert_success(resp, "音乐详情")
        assert 'title' in data['data'], "音乐详情应包含 title"

    def test_get_music_not_found(self, user_token):
        """获取不存在的音乐"""
        resp = requests.get(f"{BASE_URL}/music/99999", headers=auth_header(user_token))
        data = assert_error(resp, 404, "音乐不存在")
        assert '不存在' in data['msg'], "应提示音乐不存在"

    def test_list_music_without_token(self):
        """未登录获取音乐列表"""
        resp = requests.get(f"{BASE_URL}/music")
        assert resp.status_code != 500, "不应返回500"


# ===========================================================================
# 4. 推荐模块 (Recommend)
# ===========================================================================

class TestRecommend:
    """推荐相关接口测试"""

    def test_recommend_news(self, user_token):
        """获取新闻推荐"""
        resp = requests.get(f"{BASE_URL}/recommend/news", headers=auth_header(user_token))
        data = assert_success(resp, "新闻推荐")
        assert isinstance(data['data'], list), "推荐结果应为列表"

    def test_recommend_news_with_topn(self, user_token):
        """指定推荐数量"""
        resp = requests.get(f"{BASE_URL}/recommend/news?top_n=5", headers=auth_header(user_token))
        data = assert_success(resp, "新闻推荐top_n")

    def test_recommend_music(self, user_token):
        """获取音乐推荐"""
        resp = requests.get(f"{BASE_URL}/recommend/music", headers=auth_header(user_token))
        data = assert_success(resp, "音乐推荐")
        assert isinstance(data['data'], list), "推荐结果应为列表"

    def test_recommend_music_with_topn(self, user_token):
        """指定音乐推荐数量"""
        resp = requests.get(f"{BASE_URL}/recommend/music?top_n=3", headers=auth_header(user_token))
        data = assert_success(resp, "音乐推荐top_n")

    def test_algorithm_info(self, user_token):
        """获取算法说明"""
        resp = requests.get(f"{BASE_URL}/recommend/algorithm", headers=auth_header(user_token))
        data = assert_success(resp, "算法说明")
        assert isinstance(data['data'], dict), "算法说明应为字典"

    def test_record_behavior_view(self, user_token):
        """记录浏览行为"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "news", "item_id": 1, "action_type": "view"
        })
        data = assert_success(resp, "记录浏览行为")

    def test_record_behavior_like(self, user_token):
        """记录点赞行为"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "music", "item_id": 1, "action_type": "like"
        })
        data = assert_success(resp, "记录点赞行为")

    def test_record_behavior_rate(self, user_token):
        """记录评分行为"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "news", "item_id": 2, "action_type": "rate", "rating": 4.5
        })
        data = assert_success(resp, "记录评分行为")

    def test_record_behavior_collect(self, user_token):
        """记录收藏行为"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "music", "item_id": 2, "action_type": "collect"
        })
        data = assert_success(resp, "记录收藏行为")

    def test_record_behavior_invalid_item_type(self, user_token):
        """无效的 item_type"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "video", "item_id": 1, "action_type": "view"
        })
        data = assert_error(resp, 400, "无效item_type")
        assert 'item_type' in data['msg'], "应提示 item_type 无效"

    def test_record_behavior_invalid_action(self, user_token):
        """无效的 action_type"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "news", "item_id": 1, "action_type": "share"
        })
        data = assert_error(resp, 400, "无效action_type")
        assert 'action_type' in data['msg'], "应提示 action_type 无效"

    def test_record_behavior_missing_fields(self, user_token):
        """缺少必填字段"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "news"
        })
        data = assert_error(resp, 400, "缺少字段")

    def test_recommend_without_token(self):
        """未登录获取推荐"""
        resp = requests.get(f"{BASE_URL}/recommend/news")
        assert resp.status_code != 500, "不应返回500"

    # ---- 用户行为查询 ----
    def test_get_behaviors(self, user_token):
        """获取用户行为记录"""
        resp = requests.get(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token))
        data = assert_success(resp, "获取行为记录")
        assert 'likes' in data['data'], "应返回 likes 字段"
        assert 'ratings' in data['data'], "应返回 ratings 字段"

    def test_get_behaviors_with_item_type(self, user_token):
        """按类型获取用户行为记录"""
        resp = requests.get(f"{BASE_URL}/recommend/behavior?item_type=news", headers=auth_header(user_token))
        data = assert_success(resp, "获取新闻行为记录")

    def test_delete_behavior(self, user_token):
        """删除行为记录（取消点赞）"""
        # 先记录一个点赞
        requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={
            "item_type": "news", "item_id": 3, "action_type": "like"
        })
        # 删除点赞
        resp = requests.delete(
            f"{BASE_URL}/recommend/behavior?item_type=news&item_id=3&action_type=like",
            headers=auth_header(user_token)
        )
        data = assert_success(resp, "删除行为记录")
        assert '取消' in data.get('msg', ''), "应提示已取消"

    def test_delete_behavior_missing_params(self, user_token):
        """删除行为记录缺少参数"""
        resp = requests.delete(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token))
        data = assert_error(resp, 400, "删除行为缺少参数")

    # ---- 用户兴趣统计 ----
    def test_get_my_stats(self, user_token):
        """获取用户兴趣统计"""
        resp = requests.get(f"{BASE_URL}/recommend/my-stats", headers=auth_header(user_token))
        data = assert_success(resp, "获取兴趣统计")
        assert 'behavior_summary' in data['data'], "应返回 behavior_summary"
        assert 'news_interests' in data['data'], "应返回 news_interests"
        assert 'music_interests' in data['data'], "应返回 music_interests"

    def test_get_my_behaviors(self, user_token):
        """获取用户行为列表"""
        resp = requests.get(f"{BASE_URL}/recommend/my-behaviors", headers=auth_header(user_token))
        data = assert_success(resp, "获取行为列表")
        assert 'likes' in data['data'], "应返回 likes"
        assert 'ratings' in data['data'], "应返回 ratings"

    def test_get_my_profile(self, user_token):
        """获取用户兴趣画像"""
        resp = requests.get(f"{BASE_URL}/recommend/my-profile", headers=auth_header(user_token))
        data = assert_success(resp, "获取兴趣画像")
        assert 'news_radar' in data['data'], "应返回 news_radar"
        assert 'music_radar' in data['data'], "应返回 music_radar"
        assert 'stats' in data['data'], "应返回 stats"


# ===========================================================================
# 5. 管理模块 (Admin)
# ===========================================================================

class TestAdmin:
    """管理后台接口测试"""

    # ---- 用户管理 ----
    def test_list_users(self, admin_token):
        """管理员获取用户列表"""
        resp = requests.get(f"{BASE_URL}/admin/users", headers=auth_header(admin_token))
        data = assert_success(resp, "用户列表")

    def test_list_users_pagination(self, admin_token):
        """用户列表分页"""
        resp = requests.get(f"{BASE_URL}/admin/users?page=1&per_page=5", headers=auth_header(admin_token))
        data = assert_success(resp, "用户列表分页")

    def test_update_user(self, admin_token):
        """更新用户信息"""
        # 先获取一个用户
        resp = requests.get(f"{BASE_URL}/admin/users", headers=auth_header(admin_token))
        data = assert_success(resp, "获取用户列表")
        users = data['data'].get('items', data['data'].get('list', []))
        # 找一个非 admin 用户
        target = None
        for u in users:
            if u.get('role') != 'admin':
                target = u
                break
        if target:
            resp = requests.put(
                f"{BASE_URL}/admin/users/{target['id']}",
                headers=auth_header(admin_token),
                json={"nickname": f"测试昵称_{rand_str(4)}"}
            )
            data = assert_success(resp, "更新用户")
            assert '成功' in data.get('msg', ''), "应提示更新成功"

    def test_update_nonexistent_user(self, admin_token):
        """更新不存在的用户"""
        resp = requests.put(
            f"{BASE_URL}/admin/users/99999",
            headers=auth_header(admin_token),
            json={"nickname": "test"}
        )
        data = assert_error(resp, 404, "更新不存在用户")

    # ---- 新闻管理 ----
    def test_create_news(self, admin_token):
        """创建新闻"""
        resp = requests.post(f"{BASE_URL}/admin/news", headers=auth_header(admin_token), json={
            "title": f"测试新闻_{rand_str(4)}",
            "content": "这是一条测试新闻内容，用于接口测试。",
            "category": "科技",
            "source": "测试来源"
        })
        data = assert_success(resp, "创建新闻")
        assert 'id' in data['data'], "创建成功应返回新闻 ID"

    def test_create_news_missing_fields(self, admin_token):
        """创建新闻缺少必填字段"""
        resp = requests.post(f"{BASE_URL}/admin/news", headers=auth_header(admin_token), json={
            "title": "只有标题"
        })
        data = assert_error(resp, 400, "创建新闻缺少字段")

    def test_update_news(self, admin_token):
        """更新新闻"""
        # 先创建一条
        create_resp = requests.post(f"{BASE_URL}/admin/news", headers=auth_header(admin_token), json={
            "title": f"待更新新闻_{rand_str(4)}", "content": "原始内容", "category": "科技"
        })
        create_data = assert_success(create_resp, "创建待更新新闻")
        nid = create_data['data']['id']

        resp = requests.put(f"{BASE_URL}/admin/news/{nid}", headers=auth_header(admin_token), json={
            "title": "更新后的标题", "content": "更新后的内容"
        })
        data = assert_success(resp, "更新新闻")
        assert '成功' in data.get('msg', '')

    def test_update_nonexistent_news(self, admin_token):
        """更新不存在的新闻"""
        resp = requests.put(f"{BASE_URL}/admin/news/99999", headers=auth_header(admin_token), json={
            "title": "不存在"
        })
        data = assert_error(resp, 404, "更新不存在新闻")

    def test_delete_news(self, admin_token):
        """删除新闻"""
        # 先创建一条
        create_resp = requests.post(f"{BASE_URL}/admin/news", headers=auth_header(admin_token), json={
            "title": f"待删除新闻_{rand_str(4)}", "content": "将被删除", "category": "科技"
        })
        create_data = assert_success(create_resp, "创建待删除新闻")
        nid = create_data['data']['id']

        resp = requests.delete(f"{BASE_URL}/admin/news/{nid}", headers=auth_header(admin_token))
        data = assert_success(resp, "删除新闻")
        assert '成功' in data.get('msg', '')

    def test_delete_nonexistent_news(self, admin_token):
        """删除不存在的新闻"""
        resp = requests.delete(f"{BASE_URL}/admin/news/99999", headers=auth_header(admin_token))
        data = assert_error(resp, 404, "删除不存在新闻")

    # ---- 音乐管理 ----
    def test_create_music(self, admin_token):
        """创建音乐"""
        resp = requests.post(f"{BASE_URL}/admin/music", headers=auth_header(admin_token), json={
            "title": f"测试歌曲_{rand_str(4)}",
            "artist": "测试歌手",
            "genre": "流行",
            "album": "测试专辑",
            "duration": 240
        })
        data = assert_success(resp, "创建音乐")
        assert 'id' in data['data'], "创建成功应返回音乐 ID"

    def test_create_music_missing_fields(self, admin_token):
        """创建音乐缺少必填字段"""
        resp = requests.post(f"{BASE_URL}/admin/music", headers=auth_header(admin_token), json={
            "title": "只有标题"
        })
        data = assert_error(resp, 400, "创建音乐缺少字段")

    def test_update_music(self, admin_token):
        """更新音乐"""
        create_resp = requests.post(f"{BASE_URL}/admin/music", headers=auth_header(admin_token), json={
            "title": f"待更新歌曲_{rand_str(4)}", "artist": "原歌手", "genre": "流行"
        })
        create_data = assert_success(create_resp, "创建待更新音乐")
        mid = create_data['data']['id']

        resp = requests.put(f"{BASE_URL}/admin/music/{mid}", headers=auth_header(admin_token), json={
            "title": "更新后的歌曲", "artist": "新歌手"
        })
        data = assert_success(resp, "更新音乐")
        assert '成功' in data.get('msg', '')

    def test_update_nonexistent_music(self, admin_token):
        """更新不存在的音乐"""
        resp = requests.put(f"{BASE_URL}/admin/music/99999", headers=auth_header(admin_token), json={
            "title": "不存在"
        })
        data = assert_error(resp, 404, "更新不存在音乐")

    def test_delete_music(self, admin_token):
        """删除音乐"""
        create_resp = requests.post(f"{BASE_URL}/admin/music", headers=auth_header(admin_token), json={
            "title": f"待删除歌曲_{rand_str(4)}", "artist": "歌手", "genre": "流行"
        })
        create_data = assert_success(create_resp, "创建待删除音乐")
        mid = create_data['data']['id']

        resp = requests.delete(f"{BASE_URL}/admin/music/{mid}", headers=auth_header(admin_token))
        data = assert_success(resp, "删除音乐")
        assert '成功' in data.get('msg', '')

    def test_delete_nonexistent_music(self, admin_token):
        """删除不存在的音乐"""
        resp = requests.delete(f"{BASE_URL}/admin/music/99999", headers=auth_header(admin_token))
        data = assert_error(resp, 404, "删除不存在音乐")

    # ---- 操作日志 ----
    def test_list_logs(self, admin_token):
        """获取操作日志"""
        resp = requests.get(f"{BASE_URL}/admin/logs", headers=auth_header(admin_token))
        data = assert_success(resp, "操作日志")

    def test_list_logs_pagination(self, admin_token):
        """操作日志分页"""
        resp = requests.get(f"{BASE_URL}/admin/logs?page=1&per_page=5", headers=auth_header(admin_token))
        data = assert_success(resp, "操作日志分页")


# ===========================================================================
# 6. 权限控制测试
# ===========================================================================

class TestPermission:
    """权限控制测试 - 普通用户不能访问管理接口"""

    def test_user_cannot_list_users(self, user_token):
        """普通用户不能获取用户列表"""
        resp = requests.get(f"{BASE_URL}/admin/users", headers=auth_header(user_token))
        data = assert_ok(resp, "普通用户访问用户列表")
        assert data['code'] == 403, f"普通用户应被拒绝, 实际 code={data['code']}"

    def test_user_cannot_create_news(self, user_token):
        """普通用户不能创建新闻"""
        resp = requests.post(f"{BASE_URL}/admin/news", headers=auth_header(user_token), json={
            "title": "非法创建", "content": "内容", "category": "科技"
        })
        data = assert_ok(resp, "普通用户创建新闻")
        assert data['code'] == 403, f"普通用户应被拒绝, 实际 code={data['code']}"

    def test_user_cannot_delete_music(self, user_token):
        """普通用户不能删除音乐"""
        resp = requests.delete(f"{BASE_URL}/admin/music/1", headers=auth_header(user_token))
        data = assert_ok(resp, "普通用户删除音乐")
        assert data['code'] == 403, f"普通用户应被拒绝, 实际 code={data['code']}"

    def test_user_cannot_view_logs(self, user_token):
        """普通用户不能查看操作日志"""
        resp = requests.get(f"{BASE_URL}/admin/logs", headers=auth_header(user_token))
        data = assert_ok(resp, "普通用户查看日志")
        assert data['code'] == 403, f"普通用户应被拒绝, 实际 code={data['code']}"

    def test_user_cannot_view_analytics(self, user_token):
        """普通用户不能查看数据分析"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/overview", headers=auth_header(user_token))
        data = assert_ok(resp, "普通用户查看分析")
        assert data['code'] == 403, f"普通用户应被拒绝, 实际 code={data['code']}"


# ===========================================================================
# 7. 数据分析模块 (Analytics)
# ===========================================================================

class TestAnalytics:
    """数据分析接口测试"""

    def test_overview(self, admin_token):
        """数据概览"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/overview", headers=auth_header(admin_token))
        data = assert_success(resp, "数据概览")
        for key in ['user_count', 'news_count', 'music_count', 'behavior_count']:
            assert key in data['data'], f"概览数据应包含 {key}"
            assert isinstance(data['data'][key], int), f"{key} 应为整数"

    def test_behavior_analysis_news(self, admin_token):
        """新闻行为分析"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/behavior?item_type=news", headers=auth_header(admin_token))
        data = assert_success(resp, "新闻行为分析")
        for key in ['action_distribution', 'daily_trend', 'category_heat', 'rating_distribution']:
            assert key in data['data'], f"行为分析应包含 {key}"

    def test_behavior_analysis_music(self, admin_token):
        """音乐行为分析"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/behavior?item_type=music", headers=auth_header(admin_token))
        data = assert_success(resp, "音乐行为分析")

    def test_recommendation_analysis(self, admin_token):
        """推荐分析"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/recommendation", headers=auth_header(admin_token))
        data = assert_success(resp, "推荐分析")
        for key in ['algorithm_distribution', 'score_distribution', 'daily_recommendations']:
            assert key in data['data'], f"推荐分析应包含 {key}"

    def test_similarity_matrix_news(self, admin_token):
        """新闻相似度矩阵"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/similarity?item_type=news", headers=auth_header(admin_token))
        data = assert_success(resp, "新闻相似度矩阵")

    def test_similarity_matrix_music(self, admin_token):
        """音乐相似度矩阵"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/similarity?item_type=music", headers=auth_header(admin_token))
        data = assert_success(resp, "音乐相似度矩阵")

    def test_algorithm_explanation(self, admin_token):
        """算法说明"""
        resp = requests.get(f"{BASE_URL}/admin/analytics/algorithm", headers=auth_header(admin_token))
        data = assert_success(resp, "算法说明")
        assert isinstance(data['data'], dict), "算法说明应为字典"


# ===========================================================================
# 8. 错误处理与健壮性测试
# ===========================================================================

class TestErrorHandling:
    """错误处理测试 - 确保不返回500，所有错误有友好提示"""

    def test_invalid_endpoint(self):
        """访问不存在的接口"""
        resp = requests.get(f"{BASE_URL}/nonexistent")
        assert resp.status_code != 500, "不存在的接口不应返回500"

    def test_invalid_method(self):
        """使用错误的 HTTP 方法"""
        resp = requests.delete(f"{BASE_URL}/auth/login")
        data = resp.json()
        # 应返回 405 而非 500
        assert resp.status_code != 500, \
            f"错误的HTTP方法不应返回500, 实际: {resp.status_code}, msg={data.get('msg')}"

    def test_malformed_json(self, user_token):
        """发送格式错误的 JSON"""
        resp = requests.post(
            f"{BASE_URL}/recommend/behavior",
            headers={**auth_header(user_token), "Content-Type": "application/json"},
            data="not a json"
        )
        assert resp.status_code != 500, "格式错误的JSON不应返回500"

    def test_empty_json(self, user_token):
        """发送空 JSON"""
        resp = requests.post(f"{BASE_URL}/recommend/behavior", headers=auth_header(user_token), json={})
        data = resp.json()
        assert resp.status_code != 500, "空JSON不应返回500"
        assert data.get('code') == 400 or 'msg' in data, "空JSON应返回400或有错误提示"

    def test_invalid_token(self):
        """使用无效 token"""
        resp = requests.get(f"{BASE_URL}/auth/profile", headers=auth_header("invalid.token.here"))
        assert resp.status_code != 500, "无效token不应返回500"

    def test_expired_like_token(self):
        """使用格式错误的 token"""
        resp = requests.get(f"{BASE_URL}/news", headers={"Authorization": "Bearer abc123"})
        assert resp.status_code != 500, "格式错误token不应返回500"

    def test_news_id_string(self, user_token):
        """新闻ID传入字符串"""
        resp = requests.get(f"{BASE_URL}/news/abc", headers=auth_header(user_token))
        assert resp.status_code != 500, "字符串ID不应返回500"

    def test_music_id_negative(self, user_token):
        """音乐ID传入负数"""
        resp = requests.get(f"{BASE_URL}/music/-1", headers=auth_header(user_token))
        assert resp.status_code != 500, "负数ID不应返回500"

    def test_large_page_number(self, user_token):
        """超大页码"""
        resp = requests.get(f"{BASE_URL}/news?page=999999", headers=auth_header(user_token))
        data = assert_success(resp, "超大页码")

    def test_zero_per_page(self, user_token):
        """per_page 为 0"""
        resp = requests.get(f"{BASE_URL}/news?per_page=0", headers=auth_header(user_token))
        assert resp.status_code != 500, "per_page=0 不应返回500"

    def test_negative_top_n(self, user_token):
        """top_n 为负数"""
        resp = requests.get(f"{BASE_URL}/recommend/news?top_n=-1", headers=auth_header(user_token))
        assert resp.status_code != 500, "负数top_n不应返回500"


# ===========================================================================
# 9. 用户删除测试（放最后，避免影响其他测试）
# ===========================================================================

class TestAdminDeleteUser:
    """管理员删除用户测试（独立测试，避免影响其他用例）"""

    def test_delete_user(self, admin_token):
        """删除用户"""
        # 先注册一个临时用户
        username = f"del_test_{rand_str(6)}"
        reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username, "password": "123456"
        })
        reg_data = assert_success(reg_resp, "注册待删除用户")
        uid = reg_data['data']['id']

        # 删除
        resp = requests.delete(f"{BASE_URL}/admin/users/{uid}", headers=auth_header(admin_token))
        data = assert_success(resp, "删除用户")
        assert '成功' in data.get('msg', '')

    def test_delete_nonexistent_user(self, admin_token):
        """删除不存在的用户"""
        resp = requests.delete(f"{BASE_URL}/admin/users/99999", headers=auth_header(admin_token))
        data = assert_error(resp, 404, "删除不存在用户")

    def test_cannot_delete_admin(self, admin_token):
        """不能删除管理员账户"""
        # admin 用户 ID 通常是 1
        resp = requests.delete(f"{BASE_URL}/admin/users/1", headers=auth_header(admin_token))
        data = assert_error(resp, 403, "删除管理员")
        assert '管理员' in data.get('msg', ''), "应提示不能删除管理员"
