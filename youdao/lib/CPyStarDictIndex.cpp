/*
<%
setup_pybind11(cfg)
%>
*/
#include "pybind11/pybind11.h"
#include <tuple>
#include <string>
#include <cstdint>

using std::string;
using std::tuple;

tuple<string, uint64_t, uint64_t> getIndex(
    const string &word, 
    const int &index_offset_bytes_size, 
    const string &idx) {

    FILE *fp = fopen(idx.c_str(), "rb");

    char name[512];
    int name_ix = 0;
    uint64_t offset;
    uint32_t length;
    int c;
    while ((c = fgetc(fp)) != EOF) {
        if (c != 0) {
            name[name_ix++] = (char) c;
        } else {
            // null-end name
            name[name_ix] = 0;

            fread(&offset, index_offset_bytes_size, 1, fp);
            fread(&length, 4, 1, fp);

            // matched
            if(strcmp(name, word.c_str()) == 0) {
                fclose(fp);
                return std::make_tuple(string(name), offset, length);
            }

            // re-initialize
            memset(name, 0, sizeof(name));
            name_ix = 0;
        }
    }
    fclose(fp);
    return std::make_tuple(word, 0, 0);
}


PYBIND11_MODULE(CPyStarDictIndex, m) {
    m.def("getIndex", &getIndex);
}