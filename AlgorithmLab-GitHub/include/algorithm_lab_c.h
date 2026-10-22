/* Original C adapter for Algorithm Lab's subset of the AV JSON protocol.
 * Call lab_step(__LINE__) after each state you want to replay.
 * This is a single-translation-unit teaching adapter, not a debugger.
 */
#ifndef ALGORITHM_LAB_C_H
#define ALGORITHM_LAB_C_H
#include <stdio.h>
#include <stdlib.h>

static FILE *lab_file = NULL;
static int lab_first = 1;

static void lab_close(void) {
    if (lab_file) { fputs("]", lab_file); fclose(lab_file); lab_file = NULL; }
}
static void lab_init(void) {
    if (!lab_file) {
        const char *path = getenv("ALGORITHM_LAB_TRACE");
        lab_file = fopen(path ? path : "visualization.json", "wb");
        if (!lab_file) { perror("Algorithm Lab trace"); exit(1); }
        fputs("[", lab_file); atexit(lab_close);
    }
}
static void lab_string(const char *s) {
    const unsigned char *p = (const unsigned char *)s;
    fputc('"', lab_file);
    for (; *p; ++p) {
        if (*p == '"' || *p == '\\') { fputc('\\', lab_file); fputc(*p, lab_file); }
        else if (*p < 32) fprintf(lab_file, "\\u%04x", *p);
        else fputc(*p, lab_file);
    }
    fputc('"', lab_file);
}
static void lab_begin(const char *key, const char *method) {
    lab_init();
    if (!lab_first) fputc(',', lab_file);
    lab_first = 0; fputs("{\"key\":", lab_file);
    if (key) lab_string(key); else fputs("null", lab_file);
    fputs(",\"method\":", lab_file);lab_string(method);fputs(",\"args\":[", lab_file);
}
static void lab_end(void) { fputs("]}", lab_file); }
static void lab_create(const char *key, const char *kind, const char *title) {
    lab_begin(key, kind); lab_string(title); lab_end();
}
static void lab_array1d(const char *key, const int *a, int count) {
    int i; lab_begin(key,"set");fputc('[',lab_file);
    for(i=0;i<count;i++){if(i)fputc(',',lab_file);fprintf(lab_file,"%d",a[i]);}
    fputc(']',lab_file);lab_end();
}
static void lab_array2d(const char *key, const int *a, int rows, int cols) {
    int r,c;lab_begin(key,"set");fputc('[',lab_file);
    for(r=0;r<rows;r++){if(r)fputc(',',lab_file);fputc('[',lab_file);
        for(c=0;c<cols;c++){if(c)fputc(',',lab_file);fprintf(lab_file,"%d",a[r*cols+c]);}
        fputc(']',lab_file);}
    fputc(']',lab_file);lab_end();
}
static void lab_row(const char *key,int row,int start,int end,int selected) {
    lab_begin(key,selected?"selectRow":"deselectRow");fprintf(lab_file,"%d,%d,%d",row,start,end);lab_end();
}
static void lab_log(const char *key,const char *text) {lab_begin(key,"println");lab_string(text);lab_end();}
static void lab_step(int line) {lab_begin(NULL,"delay");fprintf(lab_file,"%d",line);lab_end();fflush(lab_file);}
#endif
