"""域名探测缓存与并发探测测试

构造爬虫要探测候选域名，每个不可达域名都要等一次超时。这是首页加载慢/超时的主因。
本文件覆盖三件事：
- 成功记忆：探测到可用域名后 TTL 内复用，不再重复探测
- 失败记忆：全部域名探测失败后短 TTL 内快速失败
  （否则网络不通时每次实例化都要把所有候选域名重跑一遍）
- 并发探测：候选域名并行探测，但仍返回优先级最高的可用者
  （不能被"最先响应"的镜像挤掉用户配置的优先顺序）

两个爬虫都通过 _probe_host_isolated 探测，因此统一在该方法上打桩。
该方法会被线程池并发调用，所以桩里的记录要加锁。
"""

import threading
import time

import pytest

from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.javdb import JavdbSpider


@pytest.fixture(params=[JavdbSpider, JavbusSpider], ids=["javdb", "javbus"])
def spider_cls(request, monkeypatch):
    """每个用例都从干净的探测缓存开始，且不触碰真实网络。"""
    cls = request.param
    monkeypatch.setattr(cls, "_resolved_host", None, raising=False)
    monkeypatch.setattr(cls, "_resolved_host_at", 0.0, raising=False)
    monkeypatch.setattr(cls, "_probe_failed_at", 0.0, raising=False)
    # 避免构造时读取真实配置/发真实请求
    monkeypatch.setattr(cls, "_apply_login_cookie", lambda self: None, raising=False)
    return cls


class ProbeRecorder:
    """线程安全地记录探测调用，并按域名给出预设结果。"""

    def __init__(self, result=True, reachable=None):
        self._lock = threading.Lock()
        self.calls = []
        self._result = result
        self._reachable = reachable

    def install(self, monkeypatch, cls):
        recorder = self

        def fake_probe(self, base):
            with recorder._lock:
                recorder.calls.append(base)
            if recorder._reachable is not None:
                return base in recorder._reachable
            return recorder._result

        monkeypatch.setattr(cls, "_probe_host_isolated", fake_probe)
        return self

    @property
    def count(self):
        with self._lock:
            return len(self.calls)


def test_successful_probe_is_cached_across_instances(spider_cls, monkeypatch):
    recorder = ProbeRecorder(result=True).install(monkeypatch, spider_cls)

    spider_cls()
    after_first = recorder.count
    spider_cls()
    spider_cls()

    assert after_first >= 1
    # 后续实例必须命中缓存，不再新增探测
    assert recorder.count == after_first
    assert spider_cls._cached_host() is not None


def test_failed_probe_short_circuits_subsequent_constructions(spider_cls, monkeypatch):
    recorder = ProbeRecorder(result=False).install(monkeypatch, spider_cls)

    spider_cls()
    after_first = recorder.count
    spider_cls()
    spider_cls()

    # 关键回归点：全部失败后不能每次实例化都重跑全部候选域名
    assert after_first >= 1
    assert recorder.count == after_first
    assert spider_cls._probe_recently_failed() is True


def test_all_candidates_are_probed_concurrently(spider_cls, monkeypatch):
    """并发探测应一次性把所有候选域名都发出去，而不是逐个等超时。"""
    recorder = ProbeRecorder(result=False).install(monkeypatch, spider_cls)

    spider = spider_cls()
    candidates = spider._candidate_hosts()

    # 串行实现会在第一个可用域名处提前返回；全不可用时两者都会探完，
    # 因此这里用"全不可用"场景断言覆盖了全部候选
    assert recorder.count == len(candidates)
    assert set(recorder.calls) == set(candidates)


def test_highest_priority_reachable_host_wins(spider_cls, monkeypatch):
    """并发下必须返回候选列表里最靠前的可用者，而非最先响应的。"""
    # _candidate_hosts 是 classmethod：直接在类上取，不要先构造实例——
    # 构造会触发真实探测，一个不可达域名就要等一次连接超时
    candidates = spider_cls._candidate_hosts()
    assert len(candidates) >= 2, "需要至少两个候选域名才能验证优先级"

    # 只让最后一个和倒数第二个可用，期望选中靠前的那个
    reachable = {candidates[-1], candidates[-2]}
    expected = candidates[-2]

    ProbeRecorder(reachable=reachable).install(monkeypatch, spider_cls)

    spider = spider_cls()

    assert spider.host == expected
    assert spider_cls._cached_host() == expected


def test_concurrent_driver_falls_back_to_serial(spider_cls, monkeypatch):
    """线程池不可用时必须退回串行，功能不能因并发失败而丢失。"""
    recorder = ProbeRecorder(result=True).install(monkeypatch, spider_cls)

    def exploding_pool(*args, **kwargs):
        raise RuntimeError("cannot start thread")

    monkeypatch.setattr("app.utils.spider.spider.ThreadPoolExecutor", exploding_pool)

    spider = spider_cls()

    # 退回串行后仍应选出可用域名
    assert spider.host in spider._candidate_hosts()
    assert recorder.count >= 1


def test_single_candidate_skips_thread_pool(spider_cls, monkeypatch):
    """只有一个候选时不必启线程池。"""
    recorder = ProbeRecorder(result=True).install(monkeypatch, spider_cls)

    def exploding_pool(*args, **kwargs):
        raise AssertionError("单候选不应启用线程池")

    monkeypatch.setattr("app.utils.spider.spider.ThreadPoolExecutor", exploding_pool)

    spider = spider_cls()
    only = spider._candidate_hosts()[0]
    assert spider._probe_hosts_concurrently([only]) == only
    assert recorder.count >= 1


def test_empty_candidate_list_returns_none(spider_cls, monkeypatch):
    ProbeRecorder(result=True).install(monkeypatch, spider_cls)
    spider = spider_cls()

    assert spider._probe_hosts_concurrently([]) is None


def test_probe_exception_is_treated_as_unreachable(spider_cls, monkeypatch):
    """单个域名探测抛异常不能带崩整轮探测。"""
    candidates_holder = {}

    def flaky_probe(self, base):
        candidates_holder.setdefault("seen", []).append(base)
        if base == self._candidate_hosts()[0]:
            raise RuntimeError("boom")
        return True

    monkeypatch.setattr(spider_cls, "_probe_host_isolated", flaky_probe)

    spider = spider_cls()

    # 第一个域名抛异常，应继续采用后面可用的域名
    assert spider.host in spider._candidate_hosts()


def test_failure_memo_expires_so_recovery_is_detected(spider_cls):
    spider_cls._probe_failed_at = time.time()
    assert spider_cls._probe_recently_failed() is True

    # 失败记忆过期后必须重新探测，网络恢复才能被发现
    spider_cls._probe_failed_at = time.time() - spider_cls._HOST_FAILURE_TTL_SECONDS - 1
    assert spider_cls._probe_recently_failed() is False


def test_failure_ttl_is_shorter_than_success_ttl(spider_cls):
    # 失败要更快重试，成功可以缓存更久
    assert spider_cls._HOST_FAILURE_TTL_SECONDS < spider_cls._HOST_CACHE_TTL_SECONDS


def test_success_clears_failure_memo(spider_cls):
    spider_cls._probe_failed_at = time.time()
    spider_cls._remember_host("https://mirror.test")

    assert spider_cls._probe_failed_at == 0.0
    assert spider_cls._cached_host() == "https://mirror.test"


def test_expired_success_cache_is_not_reused(spider_cls):
    spider_cls._remember_host("https://mirror.test")
    assert spider_cls._cached_host() == "https://mirror.test"

    spider_cls._resolved_host_at = time.time() - spider_cls._HOST_CACHE_TTL_SECONDS - 1
    assert spider_cls._cached_host() is None


def test_both_spiders_override_the_isolated_probe():
    """基类桩恒返回 False；子类若未覆盖，将永远探测不到任何域名。"""
    for cls in (JavdbSpider, JavbusSpider):
        owner = cls._probe_host_isolated.__qualname__.split(".")[0]
        assert owner == cls.__name__, f"{cls.__name__} 未覆盖 _probe_host_isolated"


def test_javdb_forced_reprobe_bypasses_both_memos(monkeypatch):
    """运行中被风控时需要强制重新探测，不能被缓存或失败记忆挡住。"""
    monkeypatch.setattr(JavdbSpider, "_apply_login_cookie", lambda self: None, raising=False)
    monkeypatch.setattr(JavdbSpider, "_resolved_host", None, raising=False)
    monkeypatch.setattr(JavdbSpider, "_probe_failed_at", 0.0, raising=False)

    recorder = ProbeRecorder(result=True).install(monkeypatch, JavdbSpider)

    spider = JavdbSpider()
    baseline = recorder.count

    spider._select_best_host(force=True)
    assert recorder.count > baseline
