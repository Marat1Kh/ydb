PY3_LIBRARY()

OWNER(g:yql)

PY_SRCS(__init__.py)

PEERDIR(
    contrib/python/Jinja2
    library/python/resource
)

END()

RECURSE_FOR_TESTS(ut)
