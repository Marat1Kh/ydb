#pragma once

#include <ydb/library/yql/udfs/common/clickhouse/client/src/IO/ReadBuffer.h>
#include <zlib.h>

namespace NYql {

namespace NGz {

class TReadBuffer : public NDB::ReadBuffer {
public:
    TReadBuffer(NDB::ReadBuffer& source);
    ~TReadBuffer();
private:
    bool nextImpl() final;

    NDB::ReadBuffer& Source_;
    std::vector<char> InBuffer, OutBuffer;

    z_stream Z_;
};

}

}

