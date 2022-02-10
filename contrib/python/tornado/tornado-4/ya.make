OWNER(g:python-contrib dldmitry orivej) 
 
PY23_LIBRARY() 
 
LICENSE(Apache-2.0) 
 
VERSION(4.5.3) 
 
PROVIDES(tornado)

PEERDIR( 
    # because of ca bundle 
    contrib/python/certifi 
) 
 
IF (PYTHON2) 
    PEERDIR( 
        contrib/python/backports_abc 
        contrib/python/singledispatch 
    ) 
ENDIF() 
 
NO_CHECK_IMPORTS( 
    tornado.platform.* 
    tornado.curl_httpclient 
) 
 
NO_LINT() 
 
PY_SRCS( 
    TOP_LEVEL 
    tornado/__init__.py 
    tornado/_locale_data.py 
    tornado/auth.py 
    tornado/autoreload.py 
    tornado/concurrent.py 
    tornado/curl_httpclient.py 
    tornado/escape.py 
    tornado/gen.py 
    tornado/http1connection.py 
    tornado/httpclient.py 
    tornado/httpserver.py 
    tornado/httputil.py 
    tornado/ioloop.py 
    tornado/iostream.py 
    tornado/locale.py 
    tornado/locks.py 
    tornado/log.py 
    tornado/netutil.py 
    tornado/options.py 
    tornado/platform/__init__.py 
    tornado/platform/asyncio.py 
    tornado/platform/auto.py 
    tornado/platform/caresresolver.py 
    tornado/platform/common.py 
    tornado/platform/epoll.py 
    tornado/platform/interface.py 
    tornado/platform/kqueue.py 
    tornado/platform/posix.py 
    tornado/platform/select.py 
    tornado/platform/twisted.py 
    tornado/platform/windows.py 
    tornado/process.py 
    tornado/queues.py 
    tornado/routing.py 
    tornado/simple_httpclient.py 
    tornado/stack_context.py 
    tornado/tcpclient.py 
    tornado/tcpserver.py 
    tornado/template.py 
    tornado/testing.py 
    tornado/util.py 
    tornado/web.py 
    tornado/websocket.py 
    tornado/wsgi.py 
) 
 
RESOURCE_FILES( 
    PREFIX contrib/python/tornado/tornado-4/ 
    .dist-info/METADATA 
    .dist-info/top_level.txt 
) 
 
END() 
