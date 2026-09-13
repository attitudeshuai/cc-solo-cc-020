"""
协同过滤推荐引擎
- User-Based Collaborative Filtering (基于用户的协同过滤)
- 带缓存机制：矩阵和相似度定时重算，推荐接口直接查缓存
- 完善的异常处理和冷启动降级策略
"""
import time
import threading
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from app import db, logger
from app.models import UserBehavior, News, Music, RecommendationLog
from config import Config


class CollaborativeFilteringEngine:
    """协同过滤推荐引擎（带缓存）"""

    def __init__(self):
        # 缓存数据结构
        self._cache = {
            'news': {'matrix': None, 'user_sim': None, 'user_ids': [], 'item_ids': [], 'updated_at': 0},
            'music': {'matrix': None, 'user_sim': None, 'user_ids': [], 'item_ids': [], 'updated_at': 0},
        }
        self._lock = threading.Lock()
        # 从配置读取参数
        self._action_scores = Config.ACTION_SCORES
        self._cache_refresh_interval = Config.CACHE_REFRESH_INTERVAL

    # ------------------------------------------------------------------
    # 缓存管理
    # ------------------------------------------------------------------

    def _is_cache_valid(self, item_type):
        """检查缓存是否有效"""
        cache = self._cache.get(item_type)
        if cache is None or cache['matrix'] is None:
            return False
        return (time.time() - cache['updated_at']) < self._cache_refresh_interval

    def refresh_cache(self, item_type):
        """刷新指定类型的缓存（线程安全）"""
        with self._lock:
            try:
                matrix, user_ids, item_ids = self._build_matrix(item_type)
                if matrix is None:
                    logger.info(f"[Engine] {item_type} 无行为数据，缓存为空")
                    self._cache[item_type] = {
                        'matrix': None, 'user_sim': None,
                        'user_ids': [], 'item_ids': [], 'updated_at': time.time()
                    }
                    return

                user_sim = self._compute_similarity(matrix)
                self._cache[item_type] = {
                    'matrix': matrix,
                    'user_sim': user_sim,
                    'user_ids': user_ids,
                    'item_ids': item_ids,
                    'updated_at': time.time()
                }
                logger.info(
                    f"[Engine] 缓存刷新完成 {item_type}: "
                    f"{len(user_ids)} 用户, {len(item_ids)} 物品, "
                    f"矩阵稀疏度 {1 - np.count_nonzero(matrix) / max(matrix.size, 1):.2%}"
                )
            except Exception as e:
                logger.error(f"[Engine] 缓存刷新失败 {item_type}: {e}", exc_info=True)

    def refresh_all_caches(self):
        """刷新所有类型的缓存"""
        for item_type in ('news', 'music'):
            self.refresh_cache(item_type)

    def _get_cache(self, item_type):
        """获取缓存，如果过期则自动刷新"""
        if not self._is_cache_valid(item_type):
            self.refresh_cache(item_type)
        return self._cache.get(item_type, {})

    # ------------------------------------------------------------------
    # 矩阵构建与相似度计算
    # ------------------------------------------------------------------

    def _build_matrix(self, item_type):
        """构建用户-物品评分矩阵，返回 (matrix, user_ids, item_ids) 或 (None, [], [])"""
        try:
            behaviors = UserBehavior.query.filter_by(item_type=item_type).all()
        except Exception as e:
            logger.error(f"[Engine] 查询行为数据失败: {e}")
            return None, [], []

        if not behaviors:
            return None, [], []

        user_set = sorted(set(b.user_id for b in behaviors))
        item_set = sorted(set(b.item_id for b in behaviors))

        if len(user_set) == 0 or len(item_set) == 0:
            return None, [], []

        user_idx = {uid: i for i, uid in enumerate(user_set)}
        item_idx = {iid: i for i, iid in enumerate(item_set)}

        rows, cols, data = [], [], []
        for b in behaviors:
            score = b.rating if b.rating and b.rating > 0 else self._action_to_score(b.action_type)
            rows.append(user_idx[b.user_id])
            cols.append(item_idx[b.item_id])
            data.append(float(score))

        try:
            matrix = csr_matrix(
                (data, (rows, cols)),
                shape=(len(user_set), len(item_set))
            ).toarray()
        except (ValueError, MemoryError) as e:
            logger.error(f"[Engine] 矩阵构建失败: {e}")
            return None, [], []

        return matrix, user_set, item_set

    def _action_to_score(self, action_type):
        return self._action_scores.get(action_type, 1.0)

    @staticmethod
    def _compute_similarity(matrix):
        """计算用户相似度矩阵（余弦相似度），带异常保护"""
        try:
            # 检查矩阵是否全零
            if np.all(matrix == 0):
                return np.zeros((matrix.shape[0], matrix.shape[0]))
            return cosine_similarity(matrix)
        except Exception as e:
            logger.error(f"[Engine] 相似度计算失败: {e}")
            return np.zeros((matrix.shape[0], matrix.shape[0]))

    # ------------------------------------------------------------------
    # 推荐核心逻辑
    # ------------------------------------------------------------------

    def recommend_for_user(self, user_id, item_type, top_n=10):
        """
        基于用户的协同过滤推荐
        - 使用缓存的相似度矩阵，不再每次重算
        - 冷启动用户自动降级为热度推荐
        - 完善的异常处理
        """
        try:
            cache = self._get_cache(item_type)
            matrix = cache.get('matrix')
            user_sim = cache.get('user_sim')
            user_ids = cache.get('user_ids', [])
            item_ids = cache.get('item_ids', [])

            # 情况1：无行为数据，全局冷启动
            if matrix is None or user_sim is None:
                logger.info(f"[Engine] 全局冷启动: {item_type} 无行为数据")
                return self._fallback_recommend(item_type, top_n, reason='暂无足够数据，为您推荐热门内容')

            # 情况2：当前用户无行为记录（新用户冷启动）
            if user_id not in user_ids:
                logger.info(f"[Engine] 新用户冷启动: user_id={user_id}")
                return self._fallback_recommend(item_type, top_n, reason='新用户推荐，为您推荐热门内容')

            user_idx = user_ids.index(user_id)
            sim_scores = user_sim[user_idx]
            user_ratings = matrix[user_idx]

            # 找出用户未评分的物品
            unrated_items = np.where(user_ratings == 0)[0]

            # 情况3：用户已评分所有物品
            if len(unrated_items) == 0:
                logger.info(f"[Engine] 用户 {user_id} 已评分所有 {item_type} 物品")
                return self._fallback_recommend(item_type, top_n, reason='您已浏览所有内容，为您推荐热门内容')

            # 加权预测评分
            predictions = []
            for item_idx in unrated_items:
                rated_users = np.where(matrix[:, item_idx] > 0)[0]
                if len(rated_users) == 0:
                    continue

                # 排除自身
                rated_users = rated_users[rated_users != user_idx]
                if len(rated_users) == 0:
                    continue

                sim_sum = np.sum(np.abs(sim_scores[rated_users]))
                if sim_sum < 1e-10:  # 避免除零，使用极小值阈值
                    continue

                pred = np.dot(sim_scores[rated_users], matrix[rated_users, item_idx]) / sim_sum
                # 限制预测分数范围
                pred = float(np.clip(pred, 0, 5))
                predictions.append((item_ids[item_idx], pred))

            # 情况4：无法生成有效预测（相似用户太少）
            if not predictions:
                logger.info(f"[Engine] 用户 {user_id} 无有效预测，降级为热度推荐")
                return self._fallback_recommend(item_type, top_n, reason='相似用户较少，为您推荐热门内容')

            predictions.sort(key=lambda x: x[1], reverse=True)
            results = predictions[:top_n]

            # 记录推荐日志
            self._save_recommendation_log(user_id, item_type, results)

            return self._fetch_items(item_type, [r[0] for r in results], {r[0]: r[1] for r in results})

        except Exception as e:
            logger.error(f"[Engine] 推荐异常 user={user_id} type={item_type}: {e}", exc_info=True)
            return self._fallback_recommend(item_type, top_n, reason='推荐服务暂时不可用，为您推荐热门内容')

    def _save_recommendation_log(self, user_id, item_type, results):
        """保存推荐日志，异常不影响推荐结果"""
        try:
            for item_id, score in results:
                log = RecommendationLog(
                    user_id=user_id, item_type=item_type,
                    item_id=item_id, score=score, algorithm='user_cf'
                )
                db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"[Engine] 保存推荐日志失败: {e}")

    def _fallback_recommend(self, item_type, top_n, reason='热门推荐'):
        """冷启动降级：按热度推荐，带明确的降级原因"""
        try:
            if item_type == 'news':
                items = News.query.order_by(News.view_count.desc()).limit(top_n).all()
            else:
                items = Music.query.order_by(Music.play_count.desc()).limit(top_n).all()

            if not items:
                logger.warning(f"[Engine] {item_type} 无任何内容可推荐")
                return []

            result = []
            for item in items:
                d = item.to_dict()
                d['rec_score'] = 0.0
                d['rec_reason'] = reason
                result.append(d)
            return result
        except Exception as e:
            logger.error(f"[Engine] 热度推荐查询失败: {e}")
            return []

    @staticmethod
    def _fetch_items(item_type, item_ids, score_map):
        """获取物品详情并附加推荐分数"""
        try:
            Model = News if item_type == 'news' else Music
            items = Model.query.filter(Model.id.in_(item_ids)).all()
            result = []
            for item in items:
                d = item.to_dict()
                d['rec_score'] = round(score_map.get(item.id, 0), 4)
                d['rec_reason'] = '协同过滤推荐'
                result.append(d)
            result.sort(key=lambda x: x['rec_score'], reverse=True)
            return result
        except Exception as e:
            logger.error(f"[Engine] 获取物品详情失败: {e}")
            return []

    # ------------------------------------------------------------------
    # 可视化数据接口
    # ------------------------------------------------------------------

    def get_similarity_matrix_data(self, item_type, max_users=20):
        """获取用户相似度矩阵数据（用于热力图可视化）"""
        try:
            cache = self._get_cache(item_type)
            user_sim = cache.get('user_sim')
            user_ids = cache.get('user_ids', [])

            if user_sim is None or len(user_ids) == 0:
                return {'user_ids': [], 'matrix': [], 'size': 0}

            n = min(len(user_ids), max_users)
            return {
                'user_ids': user_ids[:n],
                'matrix': user_sim[:n, :n].tolist(),
                'size': n
            }
        except Exception as e:
            logger.error(f"[Engine] 获取相似度矩阵失败: {e}")
            return {'user_ids': [], 'matrix': [], 'size': 0}

    def get_rating_distribution(self, item_type):
        """获取评分分布数据"""
        try:
            behaviors = UserBehavior.query.filter_by(item_type=item_type).all()
            if not behaviors:
                return {}
            dist = {}
            for b in behaviors:
                score = b.rating if b.rating and b.rating > 0 else self._action_to_score(b.action_type)
                key = str(round(score))
                dist[key] = dist.get(key, 0) + 1
            return dist
        except Exception as e:
            logger.error(f"[Engine] 获取评分分布失败: {e}")
            return {}

    def get_algorithm_explanation(self):
        """返回协同过滤算法原理说明"""
        return {
            'name': '协同过滤算法 (Collaborative Filtering)',
            'principle': '基于"相似用户有相似偏好"的假设，通过分析用户历史行为数据，找到与目标用户兴趣相似的邻居用户，将邻居用户喜欢但目标用户未接触过的物品推荐给目标用户。',
            'steps': [
                '1. 数据采集：通过 RSS 订阅和公开 API 采集新闻与音乐数据，同时记录用户浏览、点赞、评分等行为',
                '2. 构建矩阵：将用户行为转化为用户-物品评分矩阵（稀疏矩阵存储）',
                '3. 计算相似度：使用余弦相似度计算用户间的相似程度（定时离线计算并缓存）',
                '4. 邻居选择：选取与目标用户最相似的K个用户作为邻居',
                '5. 评分预测：基于邻居用户的评分加权预测目标用户对未评分物品的偏好',
                '6. 生成推荐：按预测评分排序，取Top-N作为推荐结果；冷启动用户降级为热度推荐'
            ],
            'formula': 'pred(u,i) = Σ(sim(u,v) × r(v,i)) / Σ|sim(u,v)|',
            'formula_desc': '其中 sim(u,v) 为用户u和v的余弦相似度，r(v,i) 为用户v对物品i的评分',
            'similarity_formula': 'cos(u,v) = (u·v) / (||u|| × ||v||)',
            'pros': ['无需物品特征信息', '能发现用户潜在兴趣', '推荐结果多样性好'],
            'cons': ['冷启动问题（已通过热度降级缓解）', '数据稀疏性', '计算复杂度随用户增长（已通过缓存优化）']
        }

    # ------------------------------------------------------------------
    # 后台定时刷新
    # ------------------------------------------------------------------

    def start_cache_refresh_thread(self, app):
        """启动后台缓存刷新线程"""
        def _loop():
            # 启动后延迟15秒，等待数据库就绪
            time.sleep(15)
            while True:
                try:
                    with app.app_context():
                        self.refresh_all_caches()
                except Exception as e:
                    logger.error(f"[Engine] 定时缓存刷新异常: {e}")
                time.sleep(self._cache_refresh_interval)

        t = threading.Thread(target=_loop, daemon=True, name='CacheRefresh')
        t.start()
        logger.info(f"[Engine] 缓存刷新线程已启动, 间隔 {self._cache_refresh_interval}s")


engine = CollaborativeFilteringEngine()
