//
// Created by chenlong on 15-3-19.
//

#ifdef _MSC_VER

typedef __int32 int32_t;
typedef unsigned __int32 uint32_t;
typedef __int64 int64_t;
typedef unsigned __int64 uint64_t;

#else
#include <stdint.h>
#endif

#include "Python.h"

static PyObject *getIndex(PyObject *self, PyObject *args) {
    char *idx;
    char *word;
    int index_offset_bytes_size;
    if(!PyArg_ParseTuple(args, "sis", &word, &index_offset_bytes_size, &idx)) {
        return NULL;
    }

    FILE *fp = fopen(idx, "rb");

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
            if(strcmp(name, word) == 0) {

                fclose(fp);
                return Py_BuildValue("sLL", name, offset, length);
            }

            // re-initialize
            memset(name, 0, sizeof(name));
            name_ix = 0;
        }
    }
    fclose(fp);
    return Py_BuildValue("sss", word, NULL, NULL);
}

static PyMethodDef pycFuncs[] = {
        {"getIndex", (PyCFunction)getIndex, METH_VARARGS, "get the index of stardict"},
        {NULL}
};

extern "C" void initCPyStarDictIndex(void) {
    Py_InitModule("CPyStarDictIndex", pycFuncs);
}
