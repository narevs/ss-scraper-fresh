from app.link_collect import normalize_url, same_host


def test_normalize_and_same_host():
    url = "HTTPS://www.Example.com/path/../page?utm_source=test&fbclid=1#section"
    normalized = normalize_url(url)
    assert normalized == "https://example.com/page"
    assert same_host(normalized, ["example.com"])
    assert not same_host("https://evil.com", ["example.com"])
