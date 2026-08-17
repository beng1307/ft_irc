#ifndef FORMATTED_HPP
#define FORMATTED_HPP

#include <sstream>
#include <string>
#include "print.hpp"

struct Formatted {
  std::string content;
  int _width;
  const char *_color;
  int _precision;
  bool _set_precision;
  bool _fixed;
  bool _fp;
  bool _floatfield;
  bool _restorewidth;
  int _cachedwidth;
  bool _restorecolor;
  const char* _cachedcolor;
  bool _is_bold;
  bool _is_right_aligned;
  bool _center;
  int _length;
  char _pad_spaces; // 0=none, 'L'=pad-left, 'R'=pad-right, 'C'=center (whitespace-based)
  std::string _prefix_str; // for storing prefix content
  std::string _suffix_str; // for storing suffix content
  int _pad_top; // for storing top padding
  int _pad_bot; // for storing bottom padding
  int _repeat;
  // Default Constructor: Allows PadR(10) to create an empty formatted object
  // string defaults to "" (safe to print)
  Formatted()
      : _width(0), _color(0), _precision(0), _set_precision(false),
        _fixed(false), _fp(false), _floatfield(false), _restorewidth(false),
        _cachedwidth(0), _restorecolor(false), _cachedcolor(0), _is_bold(false),
        _is_right_aligned(false), _center(false), _length(-1), _pad_spaces(0), _pad_top(0), _pad_bot(0), _repeat(1)  {}

  // Generic Constructor: "Erase" the type by printing it to a string
  // immediately
  template <typename T>
  Formatted(const T &val)
      : _width(0), _color(0), _precision(0), _set_precision(false),
        _fixed(false), _fp(false), _floatfield(false), _restorewidth(false),
        _cachedwidth(0), _restorecolor(false), _cachedcolor(0), _is_bold(false),
        _is_right_aligned(false), _center(false), _length(-1), _pad_spaces(0), _pad_top(0), _pad_bot(0), _repeat(1) {
    std::ostringstream ss;
    ss << val;
    content = ss.str();
  }

  template <typename T, typename T2>
  Formatted(const T &val, const T2 &val2)
      : _width(0), _color(0), _precision(0), _set_precision(false),
        _fixed(false), _fp(false), _floatfield(false), _restorewidth(false),
        _cachedwidth(0), _restorecolor(false), _cachedcolor(0), _is_bold(false),
        _is_right_aligned(false), _center(false), _length(-1), _pad_spaces(0), _pad_top(0), _pad_bot(0), _repeat(1) {
    std::ostringstream ss;
    ss << val << val2;
    content = ss.str();
  }

  template <typename T>
  Formatted &val(const T &v) {
    std::ostringstream ss;
    if (_fixed) ss << std::fixed;
    if (_set_precision) ss << std::setprecision(_precision);
    if (_fp) ss << std::fixed << std::setprecision(_precision);
    if(_color && USE_COLORS) ss << _color;
    // only apply setw in val() when NOT using whitespace-based padding
    if(!_pad_spaces && _width) ss << std::setw(_width) << std::left;
    if(!_pad_spaces && _is_right_aligned) ss << std::right;
    if(!_prefix_str.empty()) ss << _prefix_str;
    ss << v;
    if(!_suffix_str.empty()) ss << _suffix_str;
    if(_color && USE_COLORS) ss << RESET;
    content += ss.str();
    
    if(_restorewidth) {
      _width = _cachedwidth;
      _restorewidth = false;
    }
    if(_restorecolor) {
      _color = _cachedcolor;
      _restorecolor = false;
      _is_bold = false; 
    }
    // if(_fp || _floatfield) ss.unsetf(std::ios_base::floatfield);
    return *this;
  }

    // Overload operator() to work exactly like .val()
  template <typename T>
  Formatted &operator()(const T &v) {
    return val(v);
  }

  // Chainable setters
  Formatted &width(int n) {
    _width = n;
    _pad_spaces = 0;
    return *this;
  } 
  int length() const {
    return static_cast<int>(content.length());
  } 
  Formatted &repeat(int n) {
    _repeat = n;
    return *this;
  }
  Formatted &prefix(std::string s) {
    _prefix_str = s;
    return *this;
  }
  Formatted &suffix(std::string s) {
    _suffix_str = s;
    return *this;
  }
  Formatted &len(int n) {
    _length = n;
    return *this;
  }
  Formatted &padr(int w) {
    _width = w;
    _pad_spaces = 'R';
    _center = false;
    _is_right_aligned = false;
    return *this;
  }
  Formatted &padl(int w) {
    _width = w;
    _pad_spaces = 'L';
    _center = false;
    _is_right_aligned = false;
    return *this;
  }
  Formatted &padt(int h) {
    _pad_top = h;
    return *this;
  }
  Formatted &padb(int h) {
    _pad_bot = h;
    return *this;
  }
  Formatted &pady(int h) {
    _pad_top = h;
    _pad_bot = h;
    return *this;
  }
  Formatted &pady(int top, int bot) {
    _pad_top = top;
    _pad_bot = bot;
    return *this;
  }
  template <typename T>
  Formatted &padr(int w, const T &v) {
    return padr(w).val(v);
  }
  template <typename T>
  Formatted &padl(int w, const T &v) {
    return padl(w).val(v);
  }
  Formatted &n() {
    val('\n');
    return *this;
  }
  Formatted &width_(int n) {
    _cachedwidth = _width; // cache current width
    _width = n;
    _restorewidth = true; // flag to restore width after next val() call
    return *this;
  }
  Formatted &color(const char *c) {
    _color = c;
    if(_restorecolor) bold_();
    return *this;
  }
  Formatted &fixed() {
    _fixed = true;
    return *this;
  }
  Formatted &precision(int p) {
    _set_precision = true;
    _precision = p;
    return *this;
  }
  Formatted &fp(int p) {
    _fp = true;
    _set_precision = true;
    _precision = p;
    return *this;
  }
  Formatted &unfixed() {
    _floatfield = true;
    return *this;
  }
  Formatted &green() {
    _color = GREEN;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  template <typename T>
  Formatted &green(const T &v) {
    const char *original_color = _color;
    green();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    return *this;
  };
  Formatted &red() {
    _color = RED;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  template <typename T>
  Formatted &red(const T &v) {
    const char *original_color = _color;
    red();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    return *this;
  };
  Formatted &blue() {
    _color = BLUE;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    if(_is_bold) bold();
    return *this;
  };
  template <typename T>
  Formatted &blue(const T &v) {
    const char *original_color = _color;
    blue();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    return *this;
  };
  Formatted &cyan() {
    _color = CYAN;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  template <typename T>
  Formatted &cyan(const T &v) {
    const char *original_color = _color;
    cyan();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    return *this;
  };
  Formatted &magenta() {
    _color = MAGENTA;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  template <typename T>
  Formatted &magenta(const T &v) {
    const char *original_color = _color;
    magenta();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    return *this;
  };
  Formatted &faint() {
    _color = FAINT;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  template <typename T>
  Formatted &faint(const T &v) {
    const char *original_color = _color;
    faint();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    return *this;
  };
  Formatted &yellow() {
    _color = YELLOW;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &white() {
    _color = WHITE;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &bwhite() {
    _color = BWHITE;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &bblue() {
    _color = BBLUE;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &bred() {
    _color = BRED;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  template <typename T>
  Formatted &bred(const T &v) {
    const char *original_color = _color;
    bred();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    if(_restorecolor) bold_();
    return *this;
  };
  Formatted &bgreen() {
    _color = BGREEN;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
    template <typename T>
  Formatted &bgreen(const T &v) {
    const char *original_color = _color;
    bgreen();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    if(_restorecolor) bold_();
    return *this;
  };
  template <typename T>
  Formatted &byellow(const T &v) {
    const char *original_color = _color;
    byellow();       // call the no-arg version to set state
    val(v);
    _color = original_color;
    if(_restorecolor) bold_();
    return *this;
  };
  Formatted &byellow() {
    _color = BYELLOW;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &bmagenta() {
    _color = BMAGENTA;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &bcyan() {
    _color = BCYAN;
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &brown() {
    _color = BROWN;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &reset() {
    _color = RESET;
    if(_restorecolor) bold_();
    if(_is_bold) {
      bold();
      _is_bold = false;
    };
    return *this;
  };
  Formatted &print() {
    ::print(*this);
    return *this;
  };
  Formatted &printx() {
    ::printx(*this);
    return *this;
  };
  template <typename T>
  Formatted &print(const T &v) {
    ::print(*this, v);
    return *this;
  };
    template <typename T>
  Formatted &printx(const T &v) {
    ::printx(*this, v);
    return *this;
  };
  Formatted &printErr() {
    ::printErr(*this);
    return *this;
  };
    template <typename T>
  Formatted &printErr(const T &v) {
    ::printErr(*this, v);
    return *this;
  };
  Formatted &left() {
    _is_right_aligned = false;
    _pad_spaces = 0;
    return *this;
  }
  Formatted &right() {
    _is_right_aligned = true;
    _pad_spaces = 0;
    return *this;
  };
  // setw-based center (old behavior, renamed)
  Formatted &center(int n = 80) {
    _width = _width ? _width : n; // if width already set, use it; otherwise use n
    _center = true;
    _pad_spaces = 0;
    return *this;
  }

  // whitespace-based center (new)
  Formatted &padx(int n = 80) {
    _width = _width ? _width : n;
    _pad_spaces = 'C';
    _center = false;
    _is_right_aligned = false;
    return *this;
  }
  Formatted &bold() {
    _is_bold = true;
    if (!_color) return *this;
    std::string c(_color);
    if (c == RED) _color = BRED;
    else if (c == GREEN) _color = BGREEN;
    else if (c == YELLOW) _color = BYELLOW;
    else if (c == BLUE) _color = BBLUE;
    else if (c == MAGENTA) _color = BMAGENTA;
    else if (c == CYAN) _color = BCYAN;
    else if (c == WHITE) _color = BWHITE;
    return *this;
  }
  template <typename T>
  Formatted &bold(const T &v) {
    const char *original_color = _color;
    bold();
    val(v);
    _color = original_color;
    if(_restorecolor) bold_();
    return *this;
  }
  Formatted &bold_() {
    _cachedcolor = _color;
    _restorecolor = true;
    return bold(); 
  }

  Formatted &thin() {
    if (!_color) return *this;
    std::string c(_color);
    if (c == BRED) _color = RED;
    else if (c == BGREEN) _color = GREEN;
    else if (c == BYELLOW) _color = YELLOW;
    else if (c == BBLUE) _color = BLUE;
    else if (c == BMAGENTA) _color = MAGENTA;
    else if (c == BCYAN) _color = CYAN;
    else if (c == BWHITE) _color = WHITE;
    return *this;
  }
  template <typename T>
  Formatted &thin(const T &v) {
    const char *original_color = _color;
    thin();
    val(v);
    _color = original_color;
    if(_restorecolor) bold_();
    return *this;
  }
};

inline ostream &operator<<(ostream &os, const Formatted &f) {
  if(f._pad_top > 0) {
    os << std::string(f._pad_top, '\n');
  }
  if (f._fixed)
    os << std::fixed;
  if (f._floatfield)
    os.unsetf(std::ios_base::floatfield);
  if (f._set_precision)
    os << std::setprecision(f._precision);
  if (f._fp)
    os << std::fixed << std::setprecision(f._precision);
  if (f._color && USE_COLORS)
    os << f._color;

  // --- whitespace-based padding (padr/padl/new center) ---
  std::string display = f.content;
  if (f._pad_spaces && f._width) {
    int len = f._length != -1 ? f._length : f.content.length();
    // ::print("are we here", len, " " ,f._width);
    if (len < f._width) {
      int padding = f._width - len;
      if (f._pad_spaces == 'R') {
        display += std::string(padding, ' ');
      } else if (f._pad_spaces == 'L') {
        // ::print("Padding left: ", padding);
        display = std::string(padding, ' ') + display;
      } else if (f._pad_spaces == 'C') {
        int left = padding / 2;
        int right = padding - left;
        display = std::string(left, ' ') + display + std::string(right, ' ');
      }
    }
  }

  // --- setw-based width (centerw / .width() / .left() / .right()) ---
  if (!f._pad_spaces && f._width) {
    if (f._center) {
      int len = f._length != -1 ? f._length : f.content.length();
      int color_offset = (f._color && USE_COLORS) ? std::strlen(f._color) - 1 : 0;
      if (len < f._width) {
        int leftHalf = (f._width - len) / 2;
        os << std::right << std::setw(leftHalf + len + color_offset);
      }
    } else {
      os << (f._is_right_aligned ? std::right : std::left) << std::setw(f._width);
    }
  }
  if(f._repeat >= 1)
    os << display;
  if(f._repeat > 1) {
    for(int i = 1; i < f._repeat; i++) {
      os << display;
    }
  }

  // --- setw-based center right-padding (centerw only) ---
  if (!f._pad_spaces && f._width && f._center) {
    int len = f._length != -1 ? f._length : f.content.length();
    int color_offset = (f._color && USE_COLORS) ? std::strlen(f._color) : 0;
    if (len < f._width) {
      int leftHalf = ((f._width - len) / 2);
      int remaining = f._width - (leftHalf + len);
      os << std::left << std::setw(remaining + color_offset) << "";
    }
  }

  if (f._color && USE_COLORS)
    os << DEF;
  if (f._width || f._is_right_aligned || f._center)
    os << std::left << std::setw(0);
  if (f._fp || f._floatfield) {
    os.unsetf(std::ios_base::floatfield);
  }
  if(f._pad_bot > 0) {
    os << std::string(f._pad_bot, '\n');
  }
  return os;
}

// --- HELPER FUNCTIONS ---

inline int get_w(int col_width, int width_needed) {
  int w = col_width;
  while (w < width_needed + 1)
    w += col_width;
  return w - 1;
}

inline int num_digits(int n) {
  int count = 0;
  for (; n > 0; n /= 10)
    count++;
  return count == 0 ? 1 : count;
}


// Overload for whitespace-based padding without content
inline Formatted PadR(int n) { return Formatted().padr(n); }
inline Formatted PadL(int n) { return Formatted().padl(n); }
inline Formatted PadC(int n) { return Formatted().center(n); }
inline Formatted PadT(int n) { return Formatted().padt(n); }
inline Formatted PadB(int n) { return Formatted().padb(n); }
inline Formatted pady(int n) { return Formatted().pady(n); }
inline Formatted pady(int top, int bot) { return Formatted().pady(top, bot); }

// Overload for raw value
template <typename T> Formatted PadR(int n, const T &val) {
  return Formatted(val).padr(n);
}
template <typename T> Formatted PadL(int n, const T &val) {
  return Formatted(val).padl(n);
}
template <typename T> Formatted PadC(int n, const T &val) {
  return Formatted(val).center(n);
}
template <typename T> Formatted PadT(int n, const T &val) {
  return Formatted(val).padt(n);
}
template <typename T> Formatted PadB(int n, const T &val) {
  return Formatted(val).padb(n);
}
template <typename T> Formatted pady(int n, const T &val) {
  return Formatted(val).pady(n);
}
template <typename T> Formatted pady(int top, int bot, const T &val) {
  return Formatted(val).pady(top, bot);
}

template <typename T> Formatted Width(int n, const T &val) {
  return Formatted().width_(n)(val); // reset width after use to avoid affecting subsequent calls
}

// Overload for already Formatted object to prevent nested stringification
inline Formatted PadR(int n, Formatted val) { return val.padr(n); }
inline Formatted PadL(int n, Formatted val) { return val.padl(n); }
inline Formatted PadX(int n, Formatted val) { return val.padx(n); }
inline Formatted PadT(int n, Formatted val) { return val.padt(n); }
inline Formatted PadB(int n, Formatted val) { return val.padb(n); }
inline Formatted PadY(int n, Formatted val) { return val.pady(n); }
inline Formatted PadY(int top, int bot, Formatted val) { return val.pady(top, bot); }

// Color Helpers

#define COLOR_FUNC(NAME, CODE)                                                 \
  inline Formatted NAME() { return Formatted().color(CODE); }                  \
  template <typename T> Formatted NAME(const T &val) {                         \
    return Formatted().color(CODE)(val).color(DEF);                                         \
  }                                                                            \
  inline Formatted NAME(Formatted val) { return val.color(CODE); }

COLOR_FUNC(Red, RED)
COLOR_FUNC(Green, GREEN)
COLOR_FUNC(Yellow, YELLOW)
COLOR_FUNC(Blue, BLUE)
COLOR_FUNC(Magenta, MAGENTA)
COLOR_FUNC(Cyan, CYAN)
COLOR_FUNC(White, WHITE)
COLOR_FUNC(Brown, BROWN)
COLOR_FUNC(Faint, FAINT)
COLOR_FUNC(BRed, BRED)
COLOR_FUNC(BGreen, BGREEN)
COLOR_FUNC(BYellow, BYELLOW)
COLOR_FUNC(BBlue, BBLUE)
COLOR_FUNC(BMagenta, BMAGENTA)
COLOR_FUNC(BCyan, BCYAN)
COLOR_FUNC(BWhite, BWHITE)

// compound formatting example
template <typename T> Formatted Grade(const T &val) {
  return Cyan(PadR(3, val));
}


#endif