"""
推荐引擎单元测试 (test_engine.py)
覆盖：矩阵构建、相似度计算、推荐逻辑、冷启动降级、缓存机制、边界条件
"""
import sys
import os
import pytest
import numpy as np

# 确保可以导入 backend 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, MagicMock, PropertyMock
from app.engine import CollaborativeFilteringEngine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine():
    """创建干净的引擎实例"""
    return CollaborativeFilteringEngine()


def _make_behavior(user_id, item_type, item_id, action_type, rating=0.0):
    """构造模拟的 UserBehavior 对象"""
    b = MagicMock()
    b.user_id = user_id
    b.item_type = item_type
    b.item_id = item_id
    b.action_type = action_type
    b.rating = rating
    return b


def _make_item(item_id, item_type='news', view_count=0, play_count=0):
    """构造模拟的 News/Music 对象"""
    item = MagicMock()
    item.id = item_id
    item.to_dict.return_value = {
        'id': item_id,
        'title': f'Item {item_id}',
        'view_count': view_count,
        'play_count': play_count,
    }
    return item


# ===========================================================================
# 1. 行为评分权重
# ===========================================================================

class TestActionToScore:
    def test_view_score(self, engine):
        assert engine._action_to_score('view') == 1.0

    def test_like_score(self, engine):
        assert engine._action_to_score('like') == 3.0

    def test_rate_score(self, engine):
        assert engine._action_to_score('rate') == 5.0

    def test_collect_score(self, engine):
        assert engine._action_to_score('collect') == 4.0

    def test_unknown_action_defaults_to_1(self, engine):
        assert engine._action_to_score('share') == 1.0
        assert engine._action_to_score('') == 1.0

    def test_custom_scores(self):
        """验证从配置读取自定义权重"""
        with patch('app.engine.Config') as mock_cfg:
            mock_cfg.ACTION_SCORES = {'view': 2.0, 'like': 4.0, 'rate': 5.0, 'collect': 3.0}
            mock_cfg.CACHE_REFRESH_INTERVAL = 300
            eng = CollaborativeFilteringEngine()
            assert eng._action_to_score('view') == 2.0
            assert eng._action_to_score('like') == 4.0


# ===========================================================================
# 2. 相似度计算
# ===========================================================================

class TestComputeSimilarity:
    def test_identical_users(self, engine):
        """相同评分向量的用户相似度应为 1"""
        matrix = np.array([[5, 3, 1], [5, 3, 1]])
        sim = engine._compute_similarity(matrix)
        assert sim.shape == (2, 2)
        assert abs(sim[0, 1] - 1.0) < 1e-6

    def test_orthogonal_users(self, engine):
        """正交评分向量的用户相似度应为 0"""
        matrix = np.array([[1, 0], [0, 1]])
        sim = engine._compute_similarity(matrix)
        assert abs(sim[0, 1]) < 1e-6

    def test_all_zero_matrix(self, engine):
        """全零矩阵应返回全零相似度"""
        matrix = np.zeros((3, 4))
        sim = engine._compute_similarity(matrix)
        assert np.all(sim == 0)

    def test_single_user(self, engine):
        """单用户矩阵"""
        matrix = np.array([[3, 4, 5]])
        sim = engine._compute_similarity(matrix)
        assert sim.shape == (1, 1)
        assert abs(sim[0, 0] - 1.0) < 1e-6

    def test_diagonal_is_one(self, engine):
        """对角线应为 1（自身相似度）"""
        matrix = np.array([[5, 3, 0], [0, 4, 2], [1, 0, 5]])
        sim = engine._compute_similarity(matrix)
        for i in range(3):
            assert abs(sim[i, i] - 1.0) < 1e-6


# ===========================================================================
# 3. 矩阵构建
# ===========================================================================

class TestBuildMatrix:
    @patch('app.engine.UserBehavior')
    def test_empty_behaviors(self, mock_ub, engine):
        """无行为数据时返回 None"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        matrix, users, items = engine._build_matrix('news')
        assert matrix is None
        assert users == []
        assert items == []

    @patch('app.engine.UserBehavior')
    def test_single_behavior(self, mock_ub, engine):
        """单条行为记录"""
        mock_ub.query.filter_by.return_value.all.return_value = [
            _make_behavior(1, 'news', 10, 'view')
        ]
        matrix, users, items = engine._build_matrix('news')
        assert matrix is not None
        assert matrix.shape == (1, 1)
        assert users == [1]
        assert items == [10]
        assert matrix[0, 0] == 1.0  # view -> 1.0

    @patch('app.engine.UserBehavior')
    def test_multiple_users_items(self, mock_ub, engine):
        """多用户多物品矩阵"""
        behaviors = [
            _make_behavior(1, 'news', 10, 'view'),
            _make_behavior(1, 'news', 20, 'like'),
            _make_behavior(2, 'news', 10, 'rate', rating=4.5),
            _make_behavior(2, 'news', 30, 'collect'),
        ]
        mock_ub.query.filter_by.return_value.all.return_value = behaviors
        matrix, users, items = engine._build_matrix('news')
        assert matrix.shape == (2, 3)  # 2 users, 3 items
        assert users == [1, 2]
        assert items == [10, 20, 30]
        # user1-item10: view=1.0, user1-item20: like=3.0
        assert matrix[0, 0] == 1.0
        assert matrix[0, 1] == 3.0
        # user2-item10: rating=4.5, user2-item30: collect=4.0
        assert matrix[1, 0] == 4.5
        assert matrix[1, 2] == 4.0

    @patch('app.engine.UserBehavior')
    def test_rating_overrides_action(self, mock_ub, engine):
        """有评分时使用评分而非行为权重"""
        mock_ub.query.filter_by.return_value.all.return_value = [
            _make_behavior(1, 'news', 10, 'rate', rating=3.5)
        ]
        matrix, _, _ = engine._build_matrix('news')
        assert matrix[0, 0] == 3.5

    @patch('app.engine.UserBehavior')
    def test_db_query_exception(self, mock_ub, engine):
        """数据库查询异常时安全返回"""
        mock_ub.query.filter_by.return_value.all.side_effect = Exception("DB error")
        matrix, users, items = engine._build_matrix('news')
        assert matrix is None


# ===========================================================================
# 4. 缓存机制
# ===========================================================================

class TestCacheManagement:
    def test_initial_cache_invalid(self, engine):
        """初始缓存应无效"""
        assert not engine._is_cache_valid('news')
        assert not engine._is_cache_valid('music')

    def test_cache_valid_after_refresh(self, engine):
        """刷新后缓存应有效"""
        with patch('app.engine.UserBehavior') as mock_ub:
            mock_ub.query.filter_by.return_value.all.return_value = [
                _make_behavior(1, 'news', 10, 'view')
            ]
            engine.refresh_cache('news')
            assert engine._is_cache_valid('news')

    def test_cache_invalid_for_unknown_type(self, engine):
        """未知类型缓存应无效"""
        assert not engine._is_cache_valid('video')

    @patch('app.engine.UserBehavior')
    def test_refresh_empty_data(self, mock_ub, engine):
        """无数据时缓存标记为空但有时间戳"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        engine.refresh_cache('news')
        cache = engine._cache['news']
        assert cache['matrix'] is None
        assert cache['updated_at'] > 0

    @patch('app.engine.UserBehavior')
    def test_refresh_all_caches(self, mock_ub, engine):
        """refresh_all_caches 刷新两种类型"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        engine.refresh_all_caches()
        assert engine._cache['news']['updated_at'] > 0
        assert engine._cache['music']['updated_at'] > 0


# ===========================================================================
# 5. 推荐核心逻辑
# ===========================================================================

class TestRecommendForUser:
    @patch('app.engine.News')
    @patch('app.engine.UserBehavior')
    def test_global_cold_start(self, mock_ub, mock_news, engine):
        """无行为数据时降级为热度推荐"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        mock_news.query.order_by.return_value.limit.return_value.all.return_value = [
            _make_item(1, view_count=100)
        ]
        results = engine.recommend_for_user(999, 'news', top_n=5)
        assert len(results) > 0
        assert results[0]['rec_reason'] == '暂无足够数据，为您推荐热门内容'

    @patch('app.engine.News')
    @patch('app.engine.UserBehavior')
    def test_new_user_cold_start(self, mock_ub, mock_news, engine):
        """新用户（无行为记录）降级为热度推荐"""
        mock_ub.query.filter_by.return_value.all.return_value = [
            _make_behavior(1, 'news', 10, 'view'),
            _make_behavior(1, 'news', 20, 'like'),
        ]
        mock_news.query.order_by.return_value.limit.return_value.all.return_value = [
            _make_item(10, view_count=50)
        ]
        results = engine.recommend_for_user(999, 'news', top_n=5)
        assert len(results) > 0
        assert '新用户' in results[0]['rec_reason']

    @patch('app.engine.db')
    @patch('app.engine.RecommendationLog')
    @patch('app.engine.News')
    @patch('app.engine.UserBehavior')
    def test_collaborative_filtering_recommendation(self, mock_ub, mock_news, mock_log, mock_db, engine):
        """正常协同过滤推荐流程"""
        # 用户1和用户2有相似偏好，用户2还看了物品30
        behaviors = [
            _make_behavior(1, 'news', 10, 'rate', rating=5.0),
            _make_behavior(1, 'news', 20, 'rate', rating=4.0),
            _make_behavior(2, 'news', 10, 'rate', rating=5.0),
            _make_behavior(2, 'news', 20, 'rate', rating=4.0),
            _make_behavior(2, 'news', 30, 'rate', rating=5.0),
        ]
        mock_ub.query.filter_by.return_value.all.return_value = behaviors

        item30 = _make_item(30)
        mock_news.query.filter.return_value.all.return_value = [item30]

        results = engine.recommend_for_user(1, 'news', top_n=5)
        assert len(results) > 0
        assert results[0]['id'] == 30
        assert results[0]['rec_reason'] == '协同过滤推荐'
        assert 0 <= results[0]['rec_score'] <= 5

    @patch('app.engine.News')
    @patch('app.engine.UserBehavior')
    def test_all_items_rated(self, mock_ub, mock_news, engine):
        """用户已评分所有物品时降级"""
        behaviors = [
            _make_behavior(1, 'news', 10, 'rate', rating=5.0),
        ]
        mock_ub.query.filter_by.return_value.all.return_value = behaviors
        mock_news.query.order_by.return_value.limit.return_value.all.return_value = [
            _make_item(10, view_count=100)
        ]
        results = engine.recommend_for_user(1, 'news', top_n=5)
        assert len(results) > 0
        assert '已浏览所有' in results[0]['rec_reason']

    @patch('app.engine.News')
    @patch('app.engine.UserBehavior')
    def test_exception_fallback(self, mock_ub, mock_news, engine):
        """推荐过程异常时安全降级"""
        # 让 filter_by 本身抛异常（在 _build_matrix 外层触发）
        mock_ub.query.filter_by.side_effect = Exception("Unexpected")
        mock_news.query.order_by.return_value.limit.return_value.all.return_value = [
            _make_item(1)
        ]
        results = engine.recommend_for_user(1, 'news', top_n=5)
        assert len(results) > 0
        # 异常在 _build_matrix 内被捕获返回 None，走全局冷启动
        assert '热门' in results[0]['rec_reason']

    @patch('app.engine.Music')
    @patch('app.engine.UserBehavior')
    def test_music_recommendation(self, mock_ub, mock_music, engine):
        """音乐推荐走 Music 模型"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        mock_music.query.order_by.return_value.limit.return_value.all.return_value = [
            _make_item(1, item_type='music', play_count=200)
        ]
        results = engine.recommend_for_user(1, 'music', top_n=5)
        assert len(results) > 0


# ===========================================================================
# 6. 降级推荐
# ===========================================================================

class TestFallbackRecommend:
    @patch('app.engine.News')
    def test_fallback_news_empty(self, mock_news, engine):
        """无新闻内容时返回空列表"""
        mock_news.query.order_by.return_value.limit.return_value.all.return_value = []
        results = engine._fallback_recommend('news', 5, reason='测试')
        assert results == []

    @patch('app.engine.Music')
    def test_fallback_music(self, mock_music, engine):
        """音乐降级推荐"""
        mock_music.query.order_by.return_value.limit.return_value.all.return_value = [
            _make_item(1, item_type='music', play_count=100),
            _make_item(2, item_type='music', play_count=50),
        ]
        results = engine._fallback_recommend('music', 5, reason='冷启动')
        assert len(results) == 2
        assert results[0]['rec_score'] == 0.0
        assert results[0]['rec_reason'] == '冷启动'

    @patch('app.engine.News')
    def test_fallback_db_exception(self, mock_news, engine):
        """降级查询异常时返回空列表"""
        mock_news.query.order_by.side_effect = Exception("DB down")
        results = engine._fallback_recommend('news', 5)
        assert results == []


# ===========================================================================
# 7. 推荐日志
# ===========================================================================

class TestSaveRecommendationLog:
    @patch('app.engine.db')
    @patch('app.engine.RecommendationLog')
    def test_save_log_success(self, mock_log, mock_db, engine):
        """正常保存推荐日志"""
        engine._save_recommendation_log(1, 'news', [(10, 4.5), (20, 3.2)])
        assert mock_db.session.add.call_count == 2
        mock_db.session.commit.assert_called_once()

    @patch('app.engine.db')
    @patch('app.engine.RecommendationLog')
    def test_save_log_exception(self, mock_log, mock_db, engine):
        """日志保存失败不抛异常"""
        mock_db.session.commit.side_effect = Exception("DB error")
        # 不应抛出异常
        engine._save_recommendation_log(1, 'news', [(10, 4.5)])
        mock_db.session.rollback.assert_called_once()


# ===========================================================================
# 8. 可视化数据接口
# ===========================================================================

class TestVisualizationData:
    @patch('app.engine.UserBehavior')
    def test_similarity_matrix_empty(self, mock_ub, engine):
        """无数据时返回空矩阵"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        data = engine.get_similarity_matrix_data('news')
        assert data['size'] == 0
        assert data['matrix'] == []

    @patch('app.engine.UserBehavior')
    def test_similarity_matrix_with_data(self, mock_ub, engine):
        """有数据时返回正确维度"""
        behaviors = [
            _make_behavior(1, 'news', 10, 'view'),
            _make_behavior(2, 'news', 10, 'like'),
            _make_behavior(3, 'news', 20, 'rate', rating=4.0),
        ]
        mock_ub.query.filter_by.return_value.all.return_value = behaviors
        data = engine.get_similarity_matrix_data('news', max_users=2)
        assert data['size'] == 2
        assert len(data['matrix']) == 2
        assert len(data['matrix'][0]) == 2

    @patch('app.engine.UserBehavior')
    def test_rating_distribution_empty(self, mock_ub, engine):
        """无数据时返回空字典"""
        mock_ub.query.filter_by.return_value.all.return_value = []
        dist = engine.get_rating_distribution('news')
        assert dist == {}

    @patch('app.engine.UserBehavior')
    def test_rating_distribution(self, mock_ub, engine):
        """评分分布统计"""
        behaviors = [
            _make_behavior(1, 'news', 10, 'view'),   # 1.0
            _make_behavior(2, 'news', 20, 'view'),   # 1.0
            _make_behavior(3, 'news', 30, 'like'),   # 3.0
        ]
        mock_ub.query.filter_by.return_value.all.return_value = behaviors
        dist = engine.get_rating_distribution('news')
        assert dist.get('1') == 2
        assert dist.get('3') == 1

    def test_algorithm_explanation(self, engine):
        """算法说明返回完整结构"""
        info = engine.get_algorithm_explanation()
        assert 'name' in info
        assert 'principle' in info
        assert 'steps' in info
        assert 'formula' in info
        assert len(info['steps']) >= 5
        assert len(info['pros']) >= 2
        assert len(info['cons']) >= 2


# ===========================================================================
# 9. 预测分数边界
# ===========================================================================

class TestPredictionBounds:
    @patch('app.engine.db')
    @patch('app.engine.RecommendationLog')
    @patch('app.engine.News')
    @patch('app.engine.UserBehavior')
    def test_prediction_clipped_to_0_5(self, mock_ub, mock_news, mock_log, mock_db, engine):
        """预测分数应被限制在 [0, 5] 范围内"""
        behaviors = [
            _make_behavior(1, 'news', 10, 'rate', rating=5.0),
            _make_behavior(2, 'news', 10, 'rate', rating=5.0),
            _make_behavior(2, 'news', 20, 'rate', rating=5.0),
        ]
        mock_ub.query.filter_by.return_value.all.return_value = behaviors
        item20 = _make_item(20)
        mock_news.query.filter.return_value.all.return_value = [item20]

        results = engine.recommend_for_user(1, 'news', top_n=5)
        for r in results:
            assert 0 <= r['rec_score'] <= 5
