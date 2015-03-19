//
// Created by chenlong on 15-3-19.
//

#include "Python.h"
#include <arpa/inet.h>

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
    uint64_t offset, length;
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
                // correct byte order
                offset = htonl(offset);
                length = htonl(length);

                fclose(fp);
                return Py_BuildValue("sLL", name, offset, length);
            }

            // re-initialize
            bzero(name, sizeof(name));
            name_ix = 0;
        }
    }
    fclose(fp);
    return Py_BuildValue("sLL", word, 0, 0);
}

static PyMethodDef pycFuncs[] = {
        {"getIndex", (PyCFunction)getIndex, METH_VARARGS, "get the index of stardict"},
        {NULL}
};

void initCPyStarDictIndex(void) {
    Py_InitModule("CPyStarDictIndex", pycFuncs);
}
