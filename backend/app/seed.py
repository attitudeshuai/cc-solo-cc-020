"""种子数据：初始化管理员账号和示例数据"""
import random
from app import db, logger
from app.models import User, News, Music, UserBehavior

NEWS_CATEGORIES = ['科技', '财经', '体育', '娱乐', '教育', '健康']
MUSIC_GENRES = ['pop', 'rock', 'jazz', 'classical', 'electronic', 'hiphop']

SAMPLE_NEWS = [
    ('人工智能在医疗领域的突破性应用', '科技', '近年来，AI技术在医疗影像诊断、药物研发等领域取得了显著进展，多家医院已开始部署AI辅助诊断系统。'),
    ('全球股市迎来新一轮上涨行情', '财经', '受多重利好因素影响，全球主要股指连续上涨，投资者信心明显回升。'),
    ('世界杯预选赛精彩回顾', '体育', '在刚刚结束的世界杯预选赛中，多支传统强队展现出了强大的竞技实力。'),
    ('年度最佳电影榜单揭晓', '娱乐', '由权威影评机构评选的年度最佳电影榜单正式公布，多部口碑佳作入选。'),
    ('在线教育平台用户突破亿级', '教育', '随着数字化教育的普及，国内主要在线教育平台的注册用户总数已突破一亿。'),
    ('新型疫苗研发取得重大进展', '健康', '科研团队宣布新型mRNA疫苗在三期临床试验中表现出优异的保护效果。'),
    ('量子计算机实现新里程碑', '科技', '研究团队成功实现了1000量子比特的稳定运算，标志着量子计算进入新阶段。'),
    ('数字货币监管政策持续完善', '财经', '多国央行相继出台数字货币监管框架，推动加密资产市场规范化发展。'),
    ('马拉松赛事参与人数创新高', '体育', '今年全国各地举办的马拉松赛事参与总人数突破500万，全民健身热情高涨。'),
    ('流媒体平台原创内容大爆发', '娱乐', '各大流媒体平台加大原创内容投入，优质剧集和电影数量显著增长。'),
    ('STEM教育改革方案正式发布', '教育', '教育部发布新一轮STEM教育改革方案，强调培养学生的创新思维和实践能力。'),
    ('心理健康关注度持续上升', '健康', '社会各界对心理健康问题的关注度不断提高，心理咨询服务需求大幅增长。'),
    ('5G网络覆盖率突破90%', '科技', '工信部数据显示，全国5G网络覆盖率已突破90%，用户体验持续改善。'),
    ('绿色金融产品创新加速', '财经', '银行业推出多款绿色金融产品，支持可持续发展项目的融资需求。'),
    ('电竞产业规模持续扩大', '体育', '全球电竞产业市场规模预计将在明年突破200亿美元，职业化程度不断提高。'),
]

SAMPLE_MUSIC = [
    ('星辰大海', '黄霄雲', '星辰大海', 'pop', 245),
    ('孤勇者', '陈奕迅', '孤勇者', 'pop', 263),
    ('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 'rock', 354),
    ('Hotel California', 'Eagles', 'Hotel California', 'rock', 391),
    ('Take Five', 'Dave Brubeck', 'Time Out', 'jazz', 324),
    ('Fly Me to the Moon', 'Frank Sinatra', 'It Might as Well Be Swing', 'jazz', 148),
    ('Canon in D', 'Pachelbel', 'Classical Collection', 'classical', 330),
    ('四季·春', 'Vivaldi', 'The Four Seasons', 'classical', 210),
    ('Strobe', 'Deadmau5', 'For Lack of a Better Name', 'electronic', 637),
    ('Levels', 'Avicii', 'True', 'electronic', 203),
    ('Lose Yourself', 'Eminem', '8 Mile', 'hiphop', 326),
    ('HUMBLE.', 'Kendrick Lamar', 'DAMN.', 'hiphop', 177),
    ('稻香', '周杰伦', '魔杰座', 'pop', 223),
    ('晴天', '周杰伦', '叶惠美', 'pop', 269),
    ('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV', 'rock', 482),
]


def seed_data():
    """初始化种子数据"""
    try:
        if User.query.first():
            return
    except Exception:
        return

    logger.info("Seeding initial data...")

    # 创建管理员和测试用户
    admin = User(username='admin', nickname='系统管理员', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    test_users = []
    for i in range(1, 11):
        u = User(username=f'user{i}', nickname=f'测试用户{i}', role='user')
        u.set_password('123456')
        db.session.add(u)
        test_users.append(u)

    db.session.flush()

    # 创建新闻
    news_list = []
    for title, cat, content in SAMPLE_NEWS:
        n = News(title=title, category=cat, content=content,
                 source='推荐系统数据源', view_count=random.randint(10, 500))
        db.session.add(n)
        news_list.append(n)

    # 创建音乐
    music_list = []
    for title, artist, album, genre, dur in SAMPLE_MUSIC:
        m = Music(title=title, artist=artist, album=album, genre=genre,
                  duration=dur, play_count=random.randint(10, 1000))
        db.session.add(m)
        music_list.append(m)

    db.session.flush()

    # 生成用户行为数据
    actions = ['view', 'like', 'rate']
    for user in test_users:
        # 每个用户随机与部分新闻和音乐交互
        sampled_news = random.sample(news_list, k=random.randint(5, len(news_list)))
        for news in sampled_news:
            action = random.choice(actions)
            rating = round(random.uniform(1, 5), 1) if action == 'rate' else 0
            b = UserBehavior(user_id=user.id, item_type='news', item_id=news.id,
                             action_type=action, rating=rating)
            db.session.add(b)

        sampled_music = random.sample(music_list, k=random.randint(5, len(music_list)))
        for music in sampled_music:
            action = random.choice(actions)
            rating = round(random.uniform(1, 5), 1) if action == 'rate' else 0
            b = UserBehavior(user_id=user.id, item_type='music', item_id=music.id,
                             action_type=action, rating=rating)
            db.session.add(b)

    db.session.commit()
    logger.info("Seed data created successfully")
