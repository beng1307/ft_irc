#ifndef MACROGOD_HPP

#define FOR_EACH_1(M, x)  M(x)
#define FOR_EACH_2(M, x, ...)  M(x), FOR_EACH_1(M, __VA_ARGS__)
#define FOR_EACH_3(M, x, ...)  M(x), FOR_EACH_2(M, __VA_ARGS__)
#define FOR_EACH_4(M, x, ...)  M(x), FOR_EACH_3(M, __VA_ARGS__)
#define FOR_EACH(M, ...)  FOR_EACH_4(M, __VA_ARGS__)


#define FOR_EACH_5 FOR_EACH_4


#define FOR_EACH_1(M, x)  M(x)
#define _FOR_TUPLE(FN, x, ...)  FN(x) , FOR_EACH_1(FN, __VA_ARGS__)
#define FOR_TUPLE(FN, ...)  _FOR_TUPLE(FN, __VA_ARGS__)

#define XPND(...) __VA_ARGS__

#define TUPLE(A, B) A , B


#define PREFIX(A, B) A##B

#define CURRY(FN, PARAM) FN(PARAM,
#define CURRY_SUFFIX(SECOND) PREFIX


#define PP_ARG_N(                              \
    _1, _2, _3, _4, _5, _6, _7, _8, _9, _10,  \
    _11, _12, _13, _14, _15, _16, _17, _18, _19, _20, _21, _22, _23, _24, _25, _26, _27, _28, _29, _30,  \
    N, ...) N

#define COUNT_ARGS(...)  \
    PP_ARG_N(__VA_ARGS__,                             \
             30,29,28,27,26,25,24,23,22,21,20, 19, 18, 17, 16, 15, 14, 13,          \
             12, 11, 10, 9, 8, 7, 6, 5,               \
             4, 3, 2, 1)


             
#define IDENTITY(X) X##$
#define _FOR_EACH_COUNT(COUNT) FE_##COUNT
#define FOR_EACH_COUNT(COUNT) _FOR_EACH_COUNT(COUNT)

#define FOR_EACH_NARG(M,...) \
        FOR_EACH_COUNT(COUNT_ARGS(__VA_ARGS__))(M, __VA_ARGS__)

#define _CAT(a, b) a##b
#define CAT(a, b) _CAT(a, b)

// For each loop with the function taking 1 parameter from list of arguments
#define FE_1(M,x) M(x)
#define FE_2(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_3(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_4(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_5(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_6(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_7(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_8(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_9(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_10(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_11(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_12(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_13(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_14(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_15(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_16(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_17(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_18(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_19(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_20(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_21(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_22(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_23(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_24(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_25(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_26(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_27(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_28(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_29(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE_30(M,x,...) M(x), CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)






#define _FE(M,...) CAT(FE_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FE(...) _FE(__VA_ARGS__)

// For each loop with the function taking 2 parameters from list of arguments
#define FED_2(M,a,b) M(a, b)
#define FED_3(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_4(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_5(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_6(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_7(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_8(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_9(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_10(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_11(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED_12(M,a,b,...) M(a, b), CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define _FED(M,...) CAT(FED_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FED(...) _FED(__VA_ARGS__)

#define FEX_1(M,a)      M(a)
#define FEX_2(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_3(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_4(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_5(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_6(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_7(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_8(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_9(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_10(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_11(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_12(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_13(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_14(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_15(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_16(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_17(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_18(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_19(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_20(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_21(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_22(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_23(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_24(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_25(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_26(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_27(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_28(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_29(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX_30(M,a,...) M(a) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)

#define _FEX(M,...) CAT(FEX_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FEX(...) _FEX(__VA_ARGS__)


// For each loop with the function taking 3 parameters from list of arguments
#define FET_3(M,a,b,c,...) M(a, b, c)
#define FET_4(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_5(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_6(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_7(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_8(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_9(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_10(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_11(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_12(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_13(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_15(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_18(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_21(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET_24(M,a,b,c,...) M(a, b, c), CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define _FET(M,...) CAT(FET_, COUNT_ARGS(__VA_ARGS__))(M,__VA_ARGS__)
#define FET(...) _FET(__VA_ARGS__)

#define DEARG_1(a) a 
#define DEARG_2(a,b) a b
#define DEARG_3(a,b,c) a b c
#define DEARG_4(a,b,c,d) a b c d
#define DEARG_5(a,...)  a DEARG_4(__VA_ARGS__)
#define DEARG_6(a ,...) a DEARG_5(__VA_ARGS__)
#define DEARG_7(a ,...) a DEARG_6(__VA_ARGS__)
#define DEARG_8(a ,...) a DEARG_7(__VA_ARGS__)
#define DEARG_9(a ,...) a DEARG_8(__VA_ARGS__)
#define DEARG_10(a,...) a DEARG_9(__VA_ARGS__)
#define DEARG_11(a,...) a DEARG_10(__VA_ARGS__)
#define DEARG_12(a,...) a DEARG_11(__VA_ARGS__)
#define DEARG_13(a,...) a DEARG_12(__VA_ARGS__)
#define DEARG_14(a,...) a DEARG_13(__VA_ARGS__)
#define DEARG_15(a,...) a DEARG_14(__VA_ARGS__)
#define DEARG_16(a,...) a DEARG_15(__VA_ARGS__)
#define DEARG_17(a,...) a DEARG_16(__VA_ARGS__)
#define DEARG_18(a,...) a DEARG_17(__VA_ARGS__)
#define DEARG_19(a,...) a DEARG_18(__VA_ARGS__)
#define DEARG_20(a,...) a DEARG_19(__VA_ARGS__)
#define DEARG_21(a,...) a DEARG_20(__VA_ARGS__)
#define DEARG_22(a,...) a DEARG_21(__VA_ARGS__)
#define DEARG_23(a,...) a DEARG_22(__VA_ARGS__)
#define DEARG_24(a,...) a DEARG_23(__VA_ARGS__)
#define DEARG_25(a,...) a DEARG_24(__VA_ARGS__)
#define DEARG_26(a,...) a DEARG_25(__VA_ARGS__)
#define DEARG_27(a,...) a DEARG_26(__VA_ARGS__)
#define DEARG_28(a,...) a DEARG_27(__VA_ARGS__)
#define DEARG_29(a,...) a DEARG_28(__VA_ARGS__)
#define DEARG_30(a,...) a DEARG_29(__VA_ARGS__)
#define _DEARG(...) CAT(DEARG_, COUNT_ARGS(__VA_ARGS__))(__VA_ARGS__)
#define DEARG(...) _DEARG(__VA_ARGS__)

#define EMPTY


#define MAKE_1(GENERATOR, VAL)  GENERATOR(VAL)
#define MAKE_2(GENERATOR, VAL)  GENERATOR(VAL), MAKE_1 (GENERATOR, GENERATOR(VAL))
#define MAKE_3(GENERATOR, VAL)  GENERATOR(VAL), MAKE_2 (GENERATOR, GENERATOR(VAL))
#define MAKE_4(GENERATOR, VAL)  GENERATOR(VAL), MAKE_3 (GENERATOR, GENERATOR(VAL))
#define MAKE_5(GENERATOR, VAL)  GENERATOR(VAL), MAKE_4 (GENERATOR, GENERATOR(VAL))
#define MAKE_6(GENERATOR, VAL)  GENERATOR(VAL), MAKE_5 (GENERATOR, GENERATOR(VAL))
#define MAKE_7(GENERATOR, VAL)  GENERATOR(VAL), MAKE_6 (GENERATOR, GENERATOR(VAL))
#define MAKE_8(GENERATOR, VAL)  GENERATOR(VAL), MAKE_7 (GENERATOR, GENERATOR(VAL))
#define MAKE_9(GENERATOR, VAL)  GENERATOR(VAL), MAKE_8 (GENERATOR, GENERATOR(VAL))
#define MAKE_10(GENERATOR, VAL)  GENERATOR(VAL), MAKE_9 (GENERATOR, GENERATOR(VAL))
#define MAKE_11(GENERATOR, VAL)  GENERATOR(VAL), MAKE_10 (GENERATOR, GENERATOR(VAL))
#define MAKE_12(GENERATOR, VAL)  GENERATOR(VAL), MAKE_11 (GENERATOR, GENERATOR(VAL))
#define MAKE_13(GENERATOR, VAL)  GENERATOR(VAL), MAKE_12 (GENERATOR, GENERATOR(VAL))
#define MAKE_14(GENERATOR, VAL)  GENERATOR(VAL), MAKE_13 (GENERATOR, GENERATOR(VAL))
#define MAKE_15(GENERATOR, VAL)  GENERATOR(VAL), MAKE_14 (GENERATOR, GENERATOR(VAL))
#define MAKE_16(GENERATOR, VAL)  GENERATOR(VAL), MAKE_15 (GENERATOR, GENERATOR(VAL))
#define MAKE_17(GENERATOR, VAL)  GENERATOR(VAL), MAKE_16 (GENERATOR, GENERATOR(VAL))
#define MAKE_18(GENERATOR, VAL)  GENERATOR(VAL), MAKE_17 (GENERATOR, GENERATOR(VAL))
#define MAKE_19(GENERATOR, VAL)  GENERATOR(VAL), MAKE_18 (GENERATOR, GENERATOR(VAL))
#define MAKE_20(GENERATOR, VAL)  GENERATOR(VAL), MAKE_19 (GENERATOR, GENERATOR(VAL))
#define MAKE_21(GENERATOR, VAL)  GENERATOR(VAL), MAKE_20 (GENERATOR, GENERATOR(VAL))
#define MAKE_22(GENERATOR, VAL)  GENERATOR(VAL), MAKE_21 (GENERATOR, GENERATOR(VAL))
#define MAKE_23(GENERATOR, VAL)  GENERATOR(VAL), MAKE_22 (GENERATOR, GENERATOR(VAL))
#define MAKE_24(GENERATOR, VAL)  GENERATOR(VAL), MAKE_23 (GENERATOR, GENERATOR(VAL))
#define MAKE_25(GENERATOR, VAL)  GENERATOR(VAL), MAKE_24 (GENERATOR, GENERATOR(VAL))
#define MAKE_26(GENERATOR, VAL)  GENERATOR(VAL), MAKE_25 (GENERATOR, GENERATOR(VAL))
#define MAKE_27(GENERATOR, VAL)  GENERATOR(VAL), MAKE_26 (GENERATOR, GENERATOR(VAL))
#define MAKE_28(GENERATOR, VAL)  GENERATOR(VAL), MAKE_27 (GENERATOR, GENERATOR(VAL))
#define MAKE_29(GENERATOR, VAL)  GENERATOR(VAL), MAKE_28 (GENERATOR, GENERATOR(VAL))
#define MAKE_30(GENERATOR, VAL)  GENERATOR(VAL), MAKE_29 (GENERATOR, GENERATOR(VAL))

#define DECLARE_METHOD(ITER_TYPE, METHOD, IS_CONST) \
     ITER_TYPE METHOD() IS_CONST;

#define COLLECT_FIRST_ARG(ARG, ...) ARG
#define COLLECT_SECOND_ARG(ARG, ARG2, ...) ARG2
#define COLLECT_THIRD_ARG(ARG, ARG2, ARG3, ...) ARG3

#define COLLECT_ONE_ARG(ARG, ...) ARG
#define COLLECT_TWO_ARGS(ARG, ARG2, ...) ARG, ARG2
#define COLLECT_THREE_ARGS(ARG, ARG2, ARG3, ...) ARG, ARG2

#endif