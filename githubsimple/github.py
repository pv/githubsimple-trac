from trac.core import *
from trac.config import Option, IntOption, ListOption, BoolOption
from trac.web.api import IRequestFilter, IRequestHandler, Href
from trac.util.translation import _

def is_svn_rev(rev):
    try:
        revno = int(rev)
    except (TypeError, ValueError):
        return False
    if revno > 100000:
        return False
    return True

class GithubSimplePlugin(Component):
    implements(IRequestHandler, IRequestFilter)
    
    browser = Option('githubsimple', 'browser', '', doc="""Place your GitHub Source Browser URL here to have the /browser entry point redirect to GitHub.""")

    def __init__(self):
        self.env.log.debug("Browser: %s" % self.browser)
    
    # This has to be done via the pre_process_request handler
    # Seems that the /browser request doesn't get routed to match_request :(
    def pre_process_request(self, req, handler):
        if self.browser:
            serve = req.path_info.startswith('/browser') \
			and not is_svn_rev(req.args.get('rev'))
            self.env.log.debug("Handle Pre-Request /browser: %s" % serve)
            if serve:
                self.processBrowserURL(req)

            serve2 = req.path_info.startswith('/changeset') \
			and not is_svn_rev(req.path_info.replace('/changeset/', ''))
            self.env.log.debug("Handle Pre-Request /changeset: %s" % serve2)
            if serve2:
                self.processChangesetURL(req)

        return handler


    def post_process_request(self, req, template, data, content_type):
        return (template, data, content_type)


    def processChangesetURL(self, req):
        self.env.log.debug("processChangesetURL")
        browser = self.browser.replace('/tree/master', '/commit/')
        
        url = req.path_info.replace('/changeset/', '')
        if not url:
            browser = self.browser
            url = ''

        redirect = '%s%s' % (browser, url)
        self.env.log.debug("Redirect URL: %s" % redirect)
        out = 'Going to GitHub: %s' % redirect

        req.redirect(redirect)


    def processBrowserURL(self, req):
        self.env.log.debug("processBrowserURL")
        browser = self.browser.replace('/master', '/')
        rev = req.args.get('rev')
        
        url = req.path_info.replace('/browser', '')
        if not rev:
            rev = ''

        redirect = '%s%s%s' % (browser, rev, url)
        self.env.log.debug("Redirect URL: %s" % redirect)
        out = 'Going to GitHub: %s' % redirect

        req.redirect(redirect)
