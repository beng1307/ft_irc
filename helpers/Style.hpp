#ifndef STYLE_HPP
#define STYLE_HPP

#include "Wire.hpp"
#include "print.hpp"
#include <sstream>

class $ : public Wire {
private:
    int padl_val;
    int padr_val;
    int padt_val;
    int padb_val;
    enum ColorMode { NONE, RED_COLOR, GREEN_COLOR } color_mode;
    string text_color_seq;
    string bg_color_seq;

    static string intToStr(int v) {
        std::ostringstream ss;
        ss << v;
        return ss.str();
    }

public:
    // Standard constructors matching Wire
    $() : Wire(), padl_val(0), padr_val(0), padt_val(0), padb_val(0), color_mode(NONE), text_color_seq(""), bg_color_seq("") {}
    $(const $& str) : Wire(str), padl_val(str.padl_val), padr_val(str.padr_val), padt_val(str.padt_val), padb_val(str.padb_val), color_mode(str.color_mode), text_color_seq(str.text_color_seq), bg_color_seq(str.bg_color_seq) {}
    $& operator=(const $& other) {
        if (this != &other) {
            Wire::operator=(other);
            padl_val = other.padl_val;
            padr_val = other.padr_val;
            padt_val = other.padt_val;
            padb_val = other.padb_val;
            color_mode = other.color_mode;
            text_color_seq = other.text_color_seq;
            bg_color_seq = other.bg_color_seq;
        }
        return *this;
    }
    ~$() {}

    $(const string& str) : Wire(str), padl_val(0), padr_val(0), padt_val(0), padb_val(0), color_mode(NONE), text_color_seq(""), bg_color_seq("") {}
    $(const char* str) : Wire(str), padl_val(0), padr_val(0), padt_val(0), padb_val(0), color_mode(NONE), text_color_seq(""), bg_color_seq("") {}
    $(char c) : Wire(c), padl_val(0), padr_val(0), padt_val(0), padb_val(0), color_mode(NONE), text_color_seq(""), bg_color_seq("") {}
    $(const Wire& w) : Wire(w), padl_val(0), padr_val(0), padt_val(0), padb_val(0), color_mode(NONE), text_color_seq(""), bg_color_seq("") {}

#define MAKE_STYLE_TYPENAME(N) typename T##N
#define MAKE_STYLE_ARGUMENT(N) T##N const &t##N

#define MAKE_STYLE_CONSTRUCTOR(N) \
    template <FE(MAKE_STYLE_TYPENAME, MAKE_##N(INCREMENT, 0))> \
    $(FE(MAKE_STYLE_ARGUMENT, MAKE_##N(INCREMENT, 0))) \
        : Wire(FE(PRINT_VAR, MAKE_##N(INCREMENT, 0))), padl_val(0), padr_val(0), padt_val(0), padb_val(0), color_mode(NONE), text_color_seq(""), bg_color_seq("") {}

    FEX(MAKE_STYLE_CONSTRUCTOR, MAKE_30(INCREMENT, 0))

#undef MAKE_STYLE_TYPENAME
#undef MAKE_STYLE_ARGUMENT
#undef MAKE_STYLE_CONSTRUCTOR

    $& padl(int x) {
        if (x <= 0) return *this;
        padl_val += x;
        if (!this->empty()) {
            string spaces(x, ' ');
            size_t start_pos = getInnerStartPos();
            this->insert(start_pos, spaces);
        }
        return *this;
    }

    $& padr(int x) {
        if (x <= 0) return *this;
        padr_val += x;
        if (!this->empty()) {
            string spaces(x, ' ');
            size_t end_pos = getInnerEndPos();
            this->insert(end_pos, spaces);
        }
        return *this;
    }

    $& padx(int x) {
        if (x <= 0) return *this;
        padl(x);
        padr(x);
        return *this;
    }

    $& padt(int y) {
        if (y <= 0) return *this;
        padt_val += y;
        if (!this->empty()) {
            string newlines(y, '\n');
            size_t start_pos = getInnerStartPos();
            this->insert(start_pos, newlines);
        }
        return *this;
    }

    $& padb(int y) {
        if (y <= 0) return *this;
        padb_val += y;
        if (!this->empty()) {
            string newlines(y, '\n');
            size_t end_pos = getInnerEndPos();
            this->insert(end_pos, newlines);
        }
        return *this;
    }

    $& pady(int y) {
        if (y <= 0) return *this;
        padt(y);
        padb(y);
        return *this;
    }

    $& width(int x) {
        size_t innerStart = getInnerStartPos();
        size_t innerEnd = getInnerEndPos();
        int content_len = static_cast<int>(innerEnd - innerStart);
        if (x > content_len) {
            padr(x - content_len);
        }
        return *this;
    }

    $& widthl(int x) {
        size_t innerStart = getInnerStartPos();
        size_t innerEnd = getInnerEndPos();
        int content_len = static_cast<int>(innerEnd - innerStart);
        if (x > content_len) {
            padl(x - content_len);
        }
        return *this;
    }

    $& center(int x) {
        size_t innerStart = getInnerStartPos();
        size_t innerEnd = getInnerEndPos();
        int content_len = static_cast<int>(innerEnd - innerStart);
        if (x > content_len) {
            int diff = x - content_len;
            int right = (diff + 1) / 2;
            int left = diff - right;
            padl(left);
            padr(right);
        }
        return *this;
    }

    $& textc(int r, int g, int b) {
        text_color_seq = "\033[38;2;" + intToStr(r) + ";" + intToStr(g) + ";" + intToStr(b) + "m";
        applyColor();
        return *this;
    }

    $& bgc(int r, int g, int b) {
        bg_color_seq = "\033[48;2;" + intToStr(r) + ";" + intToStr(g) + ";" + intToStr(b) + "m";
        applyColor();
        return *this;
    }

    $& red() {
        color_mode = RED_COLOR;
        text_color_seq = RED;
        applyColor();
        return *this;
    }

    $& green() {
        color_mode = GREEN_COLOR;
        text_color_seq = GREEN;
        applyColor();
        return *this;
    }

    $& print() {
        ::print(*this);
        return *this;
    }

#define MAKE_STYLE_CALL_TYPENAME(N) typename T##N
#define MAKE_STYLE_CALL_ARGUMENT(N) T##N const &t##N

#define MAKE_STYLE_CALL_OPERATOR(N) \
    template <FE(MAKE_STYLE_CALL_TYPENAME, MAKE_##N(INCREMENT, 0))> \
    $& operator()(FE(MAKE_STYLE_CALL_ARGUMENT, MAKE_##N(INCREMENT, 0))) { \
        $ item(FE(PRINT_VAR, MAKE_##N(INCREMENT, 0))); \
        if (color_mode == RED_COLOR) item.red(); \
        else if (color_mode == GREEN_COLOR) item.green(); \
        if (!text_color_seq.empty()) item.text_color_seq = text_color_seq; \
        if (!bg_color_seq.empty()) item.bg_color_seq = bg_color_seq; \
        if (!item.text_color_seq.empty() || !item.bg_color_seq.empty()) item.applyColor(); \
        item.padl(padl_val).padr(padr_val).padt(padt_val).padb(padb_val); \
        this->append(item); \
        return *this; \
    }

    FEX(MAKE_STYLE_CALL_OPERATOR, MAKE_30(INCREMENT, 0))

#undef MAKE_STYLE_CALL_TYPENAME
#undef MAKE_STYLE_CALL_ARGUMENT
#undef MAKE_STYLE_CALL_OPERATOR

private:
    void applyColor() {
        if (this->empty()) return;
        size_t startPos = getInnerStartPos();
        size_t endPos = getInnerEndPos();
        string content = this->substr(startPos, endPos - startPos);
        string prefix = text_color_seq + bg_color_seq;
        string resetStr = RESET;
        this->assign(prefix + content + resetStr);
    }

    size_t getInnerStartPos() const {
        if (!text_color_seq.empty() || !bg_color_seq.empty()) {
            string prefix = text_color_seq + bg_color_seq;
            if (this->rfind(prefix, 0) == 0) return prefix.length();
        }
        if (this->rfind(RED, 0) == 0) {
            return string(RED).length();
        } else if (this->rfind(GREEN, 0) == 0) {
            return string(GREEN).length();
        }
        return 0;
    }

    size_t getInnerEndPos() const {
        size_t end_pos = this->length();
        string resetStr(RESET);
        if (this->length() >= resetStr.length() &&
            this->compare(this->length() - resetStr.length(), resetStr.length(), resetStr) == 0) {
            end_pos -= resetStr.length();
        }
        return end_pos;
    }
};

struct Color {
    static string text(int r, int g, int b) {
        std::ostringstream ss;
        ss << "\033[38;2;" << r << ";" << g << ";" << b << "m";
        return ss.str();
    }
    static string bg(int r, int g, int b) {
        std::ostringstream ss;
        ss << "\033[48;2;" << r << ";" << g << ";" << b << "m";
        return ss.str();
    }
};

typedef $ Style;

#endif