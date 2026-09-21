#include "ui.h"
#include <stdarg.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>

/* ==================== centering helpers ==================== */

static int term_cols(void)
{
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0 && w.ws_col > 20)
        return w.ws_col;
    return 80;
}

static int pad_for(int width)
{
    int p = (term_cols() - width) / 2;
    return p > 0 ? p : 0;
}

static void spaces(int n)
{
    for (int i = 0; i < n; i++) putchar(' ');
}

void ui_indent(void)
{
    spaces(pad_for(UI_WIDTH + 2));
}

void ui_center(const char *fmt, ...)
{
    char b[512];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(b, sizeof(b), fmt, ap);
    va_end(ap);
    spaces(pad_for((int)strlen(b)));
    printf("%s", b);
}

/* ==================== screen control ==================== */

void ui_clear(void)       { printf("\033[2J\033[H"); }
void ui_home(void)        { printf("\033[H"); }
void ui_cursor_hide(void) { printf("\033[?25l"); }
void ui_cursor_show(void) { printf("\033[?25h"); }

/* ==================== boxes ==================== */

void ui_box_top(const char *title)
{
    ui_indent();
    printf(C_CYAN "+");
    for (int i = 0; i < UI_WIDTH; i++) putchar('-');
    printf("+" C_RESET "\n");

    if (title) {
        int len = (int)strlen(title);
        if (len > UI_WIDTH - 2) len = UI_WIDTH - 2;
        int lead = (UI_WIDTH - len) / 2;

        ui_indent();
        printf(C_CYAN "|" C_RESET);
        spaces(lead);
        printf(C_BOLD C_WHITE "%.*s" C_RESET, len, title);
        spaces(UI_WIDTH - lead - len);
        printf(C_CYAN "|" C_RESET "\n");
        ui_box_mid();
    }
}

void ui_box_mid(void)
{
    ui_indent();
    printf(C_CYAN "+");
    for (int i = 0; i < UI_WIDTH; i++) putchar('-');
    printf("+" C_RESET "\n");
}

void ui_box_bottom(void)
{
    ui_indent();
    printf(C_CYAN "+");
    for (int i = 0; i < UI_WIDTH; i++) putchar('-');
    printf("+" C_RESET "\n");
}

/* one boxed row, plain text, auto-padded and clipped */
void ui_row(const char *fmt, ...)
{
    char buf[512];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);

    int avail = UI_WIDTH - 4;              /* "| " + text + " |" */
    int len   = (int)strlen(buf);
    if (len > avail) { len = avail; buf[len] = '\0'; }

    ui_indent();
    printf(C_CYAN "|  " C_RESET "%s", buf);
    spaces(avail - len);
    printf(C_CYAN "  |" C_RESET "\n");
}

/* aligned key : value row */
void ui_kv(const char *key, const char *fmt, ...)
{
    char val[256];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(val, sizeof(val), fmt, ap);
    va_end(ap);

    char line[512];
    snprintf(line, sizeof(line), "%-20s %s", key, val);
    ui_row("%s", line);
}

/* ==================== bar widget ==================== */

static const char *bar_colour(double p)
{
    if (p < 50.0) return C_GREEN;
    if (p < 80.0) return C_YELLOW;
    return C_RED;
}

void ui_bar(const char *label, double percent)
{
    const int cells = 40;
    if (percent < 0)   percent = 0;
    if (percent > 100) percent = 100;

    int filled = (int)((percent / 100.0) * cells + 0.5);
    const char *col = bar_colour(percent);

    /* visible layout: label(6) + sp + '[' + 40 + ']' + sp + "100.00%"(7) = 56 */
    const int visible = 6 + 1 + 1 + cells + 1 + 1 + 7;
    int avail = UI_WIDTH - 4;

    ui_indent();
    printf(C_CYAN "|  " C_RESET);
    printf("%-6.6s ", label);
    printf("[%s", col);
    for (int i = 0; i < filled; i++) putchar('#');
    printf(C_DIM);
    for (int i = filled; i < cells; i++) putchar('.');
    printf(C_RESET "] ");
    printf("%s%6.2f%%" C_RESET, col, percent);
    spaces(avail - visible);
    printf(C_CYAN "  |" C_RESET "\n");
}

/* ==================== banner ==================== */

void ui_banner(void)
{
    static const char *art[] = {
        " _     ___ _   _ _   ___  __    __  __  ___  _   _ ___ _____ ___  ___ ",
        "| |   |_ _| \\ | | | | \\ \\/ /   |  \\/  |/ _ \\| \\ | |_ _|_   _/ _ \\| _ \\",
        "| |__  | || |\\| | |_| |>  <    | |\\/| | (_) | |\\| || |  | || (_) |   /",
        "|____||___|_| \\_|\\___//_/\\_\\   |_|  |_|\\___/|_| \\_|___| |_| \\___/|_|_\\"
    };
    const int art_w = 70;
    const char *sub = "System Monitor & Process Manager   |   OSSP Project";

    printf(C_BOLD C_CYAN);
    for (int i = 0; i < 4; i++) {
        spaces(pad_for(art_w));
        printf("%s\n", art[i]);
    }
    printf(C_RESET);

    spaces(pad_for((int)strlen(sub)));
    printf(C_DIM "%s" C_RESET "\n", sub);
}

/* ==================== status lines ==================== */

void ui_ok(const char *fmt, ...)
{
    char b[512]; va_list ap; va_start(ap, fmt);
    vsnprintf(b, sizeof(b), fmt, ap); va_end(ap);
    spaces(pad_for((int)strlen(b) + 5));
    printf(C_GREEN "[OK] " C_RESET "%s\n", b);
}

void ui_err(const char *fmt, ...)
{
    char b[512]; va_list ap; va_start(ap, fmt);
    vsnprintf(b, sizeof(b), fmt, ap); va_end(ap);
    spaces(pad_for((int)strlen(b) + 5));
    printf(C_RED "[!!] " C_RESET "%s\n", b);
}

void ui_info(const char *fmt, ...)
{
    char b[512]; va_list ap; va_start(ap, fmt);
    vsnprintf(b, sizeof(b), fmt, ap); va_end(ap);
    spaces(pad_for((int)strlen(b) + 5));
    printf(C_BLUE "[i]  " C_RESET "%s\n", b);
}

/* ==================== process state colours ==================== */

const char *ui_state_colour(const char *state)
{
    if (!state || !*state) return C_WHITE;
    switch (state[0]) {
        case 'R': return C_GREEN;    /* running       */
        case 'S': return C_CYAN;     /* sleeping      */
        case 'D': return C_YELLOW;   /* disk wait     */
        case 'T': return C_MAGENTA;  /* stopped       */
        case 'Z': return C_RED;      /* zombie        */
        default:  return C_WHITE;
    }
}
