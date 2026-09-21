#ifndef UI_H
#define UI_H

#include <stdio.h>

/* ---------------- ANSI colours ---------------- */
#define C_RESET   "\033[0m"
#define C_BOLD    "\033[1m"
#define C_DIM     "\033[2m"
#define C_RED     "\033[31m"
#define C_GREEN   "\033[32m"
#define C_YELLOW  "\033[33m"
#define C_BLUE    "\033[34m"
#define C_MAGENTA "\033[35m"
#define C_CYAN    "\033[36m"
#define C_WHITE   "\033[37m"
#define C_BGBLUE  "\033[44m"

/* inner width of every box */
#define UI_WIDTH 68

/* screen control */
void ui_clear(void);
void ui_home(void);
void ui_cursor_hide(void);
void ui_cursor_show(void);

/* centering */
void ui_indent(void);
void ui_center(const char *fmt, ...);

/* boxes */
void ui_box_top(const char *title);
void ui_box_mid(void);
void ui_box_bottom(void);
void ui_row(const char *fmt, ...);
void ui_kv(const char *key, const char *fmt, ...);

/* widgets */
void ui_bar(const char *label, double percent);
void ui_banner(void);

/* status lines */
void ui_ok(const char *fmt, ...);
void ui_err(const char *fmt, ...);
void ui_info(const char *fmt, ...);

const char *ui_state_colour(const char *state);

#endif /* UI_H */
