#ifndef PRINT_HPP
#define PRINT_HPP

#include "abo.hpp"
#include <iomanip>
#include <iostream>
#include <cstdlib>
#include <cstring>

// inline bool check_use_colors() {
//   const char* env = std::getenv("USE_COLORS");
//   if (env && std::strcmp(env, "false") == 0) {
//     return false;
//   }
//   return true;
// }

#define BLACK "\e[38;2;0;0;0m"
#define USE_COLORS true
#define RED "\033[31m"
#define GREEN "\033[0;32m"
#define YELLOW "\033[0;93m"
#define BLUE "\033[0;34m"
#define MAGENTA "\033[0;35m"
#define CYAN "\033[0;36m"
#define WHITE "\033[0;37m"
#define BRED "\033[1;31m"
#define BGREEN "\033[1;32m"
#define BYELLOW "\033[1;93m"
#define BBLUE "\033[1;34m"
#define BMAGENTA "\033[1;35m"
#define BCYAN "\033[1;36m"
#define BWHITE "\033[1;37m"
#define RESET "\033[0;0m"
#define BRESET "\033[0;1m"
#define BOLD "\033[1m"
#define NOBOLD "\033[22m"
#define NOMOD "\033[0m"
#define FAINT "\033[2m"
#define BROWN "\033[0;33m"
#define BBROWN "\033[1;33m"
#define NRED "\033[0;91m"
#define OLINE "\033[53m"
#define OLINE_OFF "\033[55m"
#define DULINE "\033[21m"
#define STRIKE "\033[9m"
#define INVIS "\033[8m"
#define ULINE "\033[4m"
#define ULINE_OFF "\033[24m"
#define CURSIVE "\033[3m"
#define BGGREEN "\033[42m"
#define BGRED "\e[41m"
#define BGYELLOW "\e[43m"
#define DEF "\e[38;2;171;178;191m"

using std::cerr;
using std::cout;
using std::left;
using std::ostream;
using std::setw;

// macro for generating a print-like function (newline controlled by NL)
#define PRINT_TYPENAME(N) typename T##N
#define MAKE_PRINT_ARGUMENT(N) T##N const &t##N
#define PRINT_VAR(N) t##N

#define MAKE_PRINT_FN_3(N, FNAME, NL, STREAM) \
template <FE(PRINT_TYPENAME, MAKE_##N(INCREMENT, 0))> \
inline ostream &FNAME(FE(MAKE_PRINT_ARGUMENT, MAKE_##N(INCREMENT, 0))) { \
  abo(STREAM, FE(PRINT_VAR, MAKE_##N(INCREMENT, 0))); \
  if (NL) \
    STREAM << '\n'; \
  return STREAM; \
}

#define MAKE_PRINT_FN_PRINT(N) MAKE_PRINT_FN_3(N, print, true, cout)
#define MAKE_PRINT_FN_PRINTX(N) MAKE_PRINT_FN_3(N, printx, false, cout)
#define MAKE_PRINT_FN_PRINTERR(N) MAKE_PRINT_FN_3(N, printErr, true, cerr)
#define MAKE_PRINT_FN_PRINTERRX(N) MAKE_PRINT_FN_3(N, printErrx, false, cerr)

inline ostream &print(void) { cout << '\n'; return cout; }
FEX(MAKE_PRINT_FN_PRINT, MAKE_30(INCREMENT, 0))

inline ostream &printx(void) { return cout; }
FEX(MAKE_PRINT_FN_PRINTX, MAKE_30(INCREMENT, 0))

inline ostream &printErr(void) { cerr << '\n'; return cerr; }
FEX(MAKE_PRINT_FN_PRINTERR, MAKE_30(INCREMENT, 0))

inline ostream &printErrx(void) { return cerr; }
FEX(MAKE_PRINT_FN_PRINTERRX, MAKE_30(INCREMENT, 0))

#undef MAKE_PRINT_FN_3
#undef MAKE_PRINT_FN_PRINT
#undef MAKE_PRINT_FN_PRINTX
#undef MAKE_PRINT_FN_PRINTERR
#undef MAKE_PRINT_FN_PRINTERRX
#undef PRINT_TYPENAME
#undef MAKE_PRINT_ARGUMENT
#undef APPLY_PRINT

#endif
