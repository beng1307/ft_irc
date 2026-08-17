#ifndef ABO_HPP
#define ABO_HPP

#include "macrogod.hpp"
#include "arithmatic.hpp"

#define APPLY_ABO(N) << t##N
#define ABO_TYPENAME(N) typename T##N
#define MAKE_ABO_ARGUMENT(N) T##N const &t##N


#define MAKE_ABO_FN(N) \
template <typename T0, FE(ABO_TYPENAME, MAKE_##N(INCREMENT, 0))> \
inline T0 &abo(T0 &t0,FE(MAKE_ABO_ARGUMENT, MAKE_##N(INCREMENT, 0))) { \
  return t0 DEARG(FE(APPLY_ABO, MAKE_##N(INCREMENT, 0))); \
} \
\


//  MAKE_ABO_FN(1)
// MAKE_ABO_FN(2)
// MAKE_ABO_FN(3)
// MAKE_ABO_FN(4)
// MAKE_ABO_FN(5)
// MAKE_ABO_FN(6)
// MAKE_ABO_FN(7)  
// MAKE_ABO_FN(8)
// MAKE_ABO_FN(9)
// MAKE_ABO_FN(10)
// MAKE_ABO_FN(11)
// MAKE_ABO_FN(12)
// MAKE_ABO_FN(13)
// MAKE_ABO_FN(14)
// MAKE_ABO_FN(15)
// MAKE_ABO_FN(16)
// MAKE_ABO_FN(17)
// MAKE_ABO_FN(18)
// MAKE_ABO_FN(19)
// MAKE_ABO_FN(20)
// MAKE_ABO_FN(21)
// MAKE_ABO_FN(22)
// MAKE_ABO_FN(23)
// MAKE_ABO_FN(24)
// MAKE_ABO_FN(25)
// MAKE_ABO_FN(26)
// MAKE_ABO_FN(27)
// MAKE_ABO_FN(28)
// MAKE_ABO_FN(29)
// MAKE_ABO_FN(30)

FEX(MAKE_ABO_FN, MAKE_30(INCREMENT, 0))

#endif