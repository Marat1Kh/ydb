PROGRAM(mvp_oidc_proxy)

OWNER(
    alexnick
    xenoxeno
    tarasov-egor
    g:kikimr
)

CFLAGS(
    -DPROFILE_MEMORY_ALLOCATIONS
)

ALLOCATOR(LF_DBG)

SRCS(
    main.cpp
)

PEERDIR(
    ydb/mvp/oidc_proxy
)

YQL_LAST_ABI_VERSION()

END()
