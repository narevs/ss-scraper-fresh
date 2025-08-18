from app.extract import extract_emails_from_html


def test_email_priority_and_dedup():
    html = """
    <html><body>
    <a href='mailto:first@example.com'>first</a>
    first@example.com
    <a href='mailto:second@example.com'>second</a>
    second@example.com
    </body></html>
    """
    emails = extract_emails_from_html(html)
    assert emails == ["first@example.com", "second@example.com"]
