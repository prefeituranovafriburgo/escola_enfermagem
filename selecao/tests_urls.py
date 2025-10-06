from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.urls import URLResolver, URLPattern

def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    for x in lis:
        if isinstance(x, URLPattern):
            acc.append(x.pattern._route)
        elif isinstance(x, URLResolver):
            list_urls(x.url_patterns, acc)
    return acc

class TestAllUrls(TestCase):
    def test_all_urls_status_code(self):
        from django.urls import get_resolver
        urls = list_urls(get_resolver().url_patterns)
        failed_urls = []
        for url in urls:
            try:
                response = self.client.get(f'/{url}')
                if response.status_code >= 400:
                    failed_urls.append((url, response.status_code))
            except Exception as e:
                failed_urls.append((url, str(e)))
        if failed_urls:
            print("URLs com problema:", failed_urls)
        self.assertFalse(failed_urls, f"Algumas URLs falharam: {failed_urls}")
