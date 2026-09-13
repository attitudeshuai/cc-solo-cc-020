"""
数据采集模块 (Data Collector)
- 新闻采集：通过 RSS 订阅源抓取新闻数据
- 音乐采集：通过公开 API 获取音乐数据（支持动态热门列表 + 配置关键词）
- 支持定时采集和手动触发
- 所有配置项从 config.py 读取，支持环境变量覆盖
"""
import re
import time
import threading
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
from app import db, logger
from app.models import News, Music
from config import Config


def _strip_html(text):
    """去除 HTML 标签"""
    if not text:
        return ''
    return re.sub(r'<[^>]+>', '', text).strip()


def _safe_request(url, timeout=None):
    """安全的 HTTP 请求，带超时和异常处理"""
    if timeout is None:
        timeout = Config.COLLECT_REQUEST_TIMEOUT
    try:
        req = Request(url, headers={'User-Agent': 'RecommendSystem/1.0'})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (URLError, OSError, Exception) as e:
        logger.warning(f"[Collector] 请求失败 {url}: {e}")
        return None


def collect_news_from_rss(app):
    """从 RSS 源采集新闻数据（源列表从配置读取）"""
    collected = 0
    failed_sources = 0
    rss_sources = Config.RSS_SOURCES

    for source in rss_sources:
        try:
            raw = _safe_request(source['url'])
            if raw is None:
                failed_sources += 1
                continue

            root = ET.fromstring(raw)
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')

            with app.app_context():
                for item in items[:20]:
                    # 注意：ET.Element 无子节点时 bool() 为 False，必须用 is None 判断
                    title_el = item.find('title')
                    if title_el is None:
                        title_el = item.find('{http://www.w3.org/2005/Atom}title')
                    desc_el = item.find('description')
                    if desc_el is None:
                        desc_el = item.find('{http://www.w3.org/2005/Atom}summary')
                    link_el = item.find('link')
                    if link_el is None:
                        link_el = item.find('{http://www.w3.org/2005/Atom}link')

                    title = title_el.text.strip() if title_el is not None and title_el.text else None
                    if not title:
                        continue

                    if News.query.filter_by(title=title).first():
                        continue

                    content = _strip_html(desc_el.text) if desc_el is not None and desc_el.text else ''
                    link = ''
                    if link_el is not None:
                        link = link_el.get('href', '') or (link_el.text or '')

                    news = News(
                        title=title,
                        content=content if content else f'来源: {source["name"]}',
                        category=source['category'],
                        source=source['name'],
                        image_url=link,
                        view_count=0
                    )
                    db.session.add(news)
                    collected += 1

                db.session.commit()

        except ET.ParseError as e:
            logger.warning(f"[Collector] RSS 解析失败 {source['name']}: {e}")
            failed_sources += 1
        except Exception as e:
            logger.error(f"[Collector] 采集异常 {source['name']}: {e}")
            db.session.rollback()
            failed_sources += 1

    logger.info(f"[Collector] 新闻采集完成: 新增 {collected} 条, 失败源 {failed_sources}/{len(rss_sources)}")
    return {'collected': collected, 'failed_sources': failed_sources, 'total_sources': len(rss_sources)}


def _fetch_trending_artists():
    """
    从 MusicBrainz 动态获取近期活跃/热门艺术家列表
    通过搜索近期发行的录音来发现新艺术家，增强数据多样性
    """
    genres = ['pop', 'rock', 'jazz', 'electronic', 'classical', 'hiphop', 'r&b', 'folk']
    dynamic_queries = []

    for genre in genres:
        try:
            url = f'https://musicbrainz.org/ws/2/recording/?query=tag:{genre}&fmt=xml&limit=5'
            raw = _safe_request(url, timeout=15)
            if raw is None:
                continue

            root = ET.fromstring(raw)
            ns = {'mb': 'http://musicbrainz.org/ns/mmd-2.0#'}
            recordings = root.findall('.//mb:recording', ns)

            seen_artists = set()
            for rec in recordings:
                artist_el = rec.find('.//mb:artist/mb:name', ns)
                if artist_el is not None and artist_el.text:
                    artist_name = artist_el.text.strip()
                    if artist_name not in seen_artists:
                        seen_artists.add(artist_name)
                        dynamic_queries.append((genre, artist_name))

            time.sleep(1.2)  # MusicBrainz 速率限制
        except Exception as e:
            logger.warning(f"[Collector] 动态获取 {genre} 热门艺术家失败: {e}")

    logger.info(f"[Collector] 动态发现 {len(dynamic_queries)} 个艺术家")
    return dynamic_queries


def collect_music_from_api(app):
    """
    从公开音乐数据源采集音乐数据
    使用 MusicBrainz 公开 API（无需 API Key）
    采集策略：配置关键词 + 动态热门列表，增强数据多样性
    """
    collected = 0

    # 合并配置中的固定关键词 + 动态发现的热门艺术家
    config_queries = [tuple(q) for q in Config.MUSIC_SEARCH_QUERIES]
    dynamic_queries = _fetch_trending_artists()

    # 去重合并，配置优先
    seen = set(config_queries)
    all_queries = list(config_queries)
    for q in dynamic_queries:
        if q not in seen:
            seen.add(q)
            all_queries.append(q)

    logger.info(f"[Collector] 音乐采集: 配置 {len(config_queries)} 组 + 动态 {len(dynamic_queries)} 组 = 总计 {len(all_queries)} 组")

    for genre, artist in all_queries:
        try:
            url = f'https://musicbrainz.org/ws/2/recording/?query=artist:{artist}&fmt=xml&limit=5'
            raw = _safe_request(url, timeout=15)
            if raw is None:
                continue

            root = ET.fromstring(raw)
            ns = {'mb': 'http://musicbrainz.org/ns/mmd-2.0#'}
            recordings = root.findall('.//mb:recording', ns)

            with app.app_context():
                for rec in recordings:
                    title_el = rec.find('mb:title', ns)
                    length_el = rec.find('mb:length', ns)
                    artist_el = rec.find('.//mb:artist/mb:name', ns)

                    title = title_el.text.strip() if title_el is not None and title_el.text else None
                    if not title:
                        continue

                    real_artist = artist_el.text if artist_el is not None and artist_el.text else artist

                    if Music.query.filter_by(title=title, artist=real_artist).first():
                        continue

                    duration = 0
                    if length_el is not None and length_el.text:
                        try:
                            duration = int(length_el.text) // 1000
                        except (ValueError, TypeError):
                            duration = 0

                    music = Music(
                        title=title,
                        artist=real_artist,
                        album='',
                        genre=genre,
                        duration=duration,
                        play_count=0
                    )
                    db.session.add(music)
                    collected += 1

                db.session.commit()

            time.sleep(1.2)

        except ET.ParseError as e:
            logger.warning(f"[Collector] 音乐数据解析失败 {artist}: {e}")
        except Exception as e:
            logger.error(f"[Collector] 音乐采集异常 {artist}: {e}")
            try:
                with app.app_context():
                    db.session.rollback()
            except Exception:
                pass

    logger.info(f"[Collector] 音乐采集完成: 新增 {collected} 条")
    return {'collected': collected}


def run_collection(app):
    """执行一次完整的数据采集"""
    logger.info("[Collector] 开始数据采集...")
    news_result = collect_news_from_rss(app)
    music_result = collect_music_from_api(app)
    return {
        'news': news_result,
        'music': music_result,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def start_scheduled_collector(app):
    """启动后台定时采集线程"""
    interval = Config.COLLECT_INTERVAL

    def _loop():
        time.sleep(30)
        while True:
            try:
                run_collection(app)
            except Exception as e:
                logger.error(f"[Collector] 定时采集异常: {e}")
            time.sleep(interval)

    t = threading.Thread(target=_loop, daemon=True, name='DataCollector')
    t.start()
    logger.info(f"[Collector] 定时采集线程已启动, 间隔 {interval}s")
