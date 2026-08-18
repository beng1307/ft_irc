#ifndef TEMPLATEGOD_HPP
#define TEMPLATEGOD_HPP

template <typename FN>
struct fn_return_type;

template <typename R, typename Arg>
struct fn_return_type<R (*)(Arg)> {
    typedef R type;
};

template <typename R, typename A1, typename A2>
struct fn_return_type<R (*)(A1, A2)> {
    typedef R type;
};

template <typename R, typename A1, typename A2, typename A3>
struct fn_return_type<R (*)(A1, A2, A3)> {
    typedef R type;
};

template <typename R, typename A1, typename A2, typename A3, typename A4>
struct fn_return_type<R (*)(A1, A2, A3, A4)> {
    typedef R type;
};

template <typename R, typename A1, typename A2, typename A3, typename A4, typename A5>
struct fn_return_type<R (*)(A1, A2, A3, A4, A5)> {
    typedef R type;
};

template <typename FN>
struct fn_traits;

template <typename R, typename Arg>
struct fn_traits<R (*)(Arg)> {
    typedef R return_type;
    enum { arity = 1 };
};

template <typename R, typename A1, typename A2>
struct fn_traits<R (*)(A1, A2)> {
    typedef R return_type;
    enum { arity = 2 };
};

template <typename R, typename A1, typename A2, typename A3>
struct fn_traits<R (*)(A1, A2, A3)> {
    typedef R return_type;
    enum { arity = 3 };
};

template <typename R, typename A1, typename A2, typename A3, typename A4>
struct fn_traits<R (*)(A1, A2, A3, A4)> {
    typedef R return_type;
    enum { arity = 4 };
};

template <typename R, typename A1, typename A2, typename A3, typename A4, typename A5>
struct fn_traits<R (*)(A1, A2, A3, A4, A5)> {
    typedef R return_type;
    enum { arity = 5 };
};

namespace detail {
    template <typename T>
    struct has_ok_member {
    private:
        typedef char yes[1];
        typedef char no[2];

        template <typename U>
        static yes& test(bool U::*);

        template <typename U>
        static no& test(...);

    public:
        enum { value = (sizeof(test<T>(&T::_ok)) == sizeof(yes)) };
    };

    template <bool HasOk, typename T>
    struct check_valid_value {
        static bool check(const T& val) { return val; }
    };

    template <typename T>
    struct check_valid_value<false, T> {
        static bool check(const T&) { return true; }
    };
}

template <typename T>
bool is_valid_value(const T& val) {
    return detail::check_valid_value<detail::has_ok_member<T>::value, T>::check(val);
}

namespace detail {

    template <typename T>
    struct is_boolable {
    private:
        template <typename U>
        static char (&test(char (*)[sizeof(U() ? 1 : 0)]))[1];

        template <typename>
        static char (&test(...))[2];

    public:
        enum { value = sizeof(test<T>(0)) == 1 };
    };

    template <bool Boolable, typename T>
    struct break_if_falsy {
        static bool check(const T&) { return false; }
    };

    template <typename T>
    struct break_if_falsy<true, T> {
        static bool check(const T& val) { return !val; }
    };

    template <typename FN1, typename A1, typename Entry>
    struct find_if_helper {
    private:
        typedef char yes[1];
        typedef char no[2];

        template <typename F, typename A, typename E>
        static yes& test_two(char (*)[sizeof( (*(F*)0)(*(E*)0, *(A*)0) )]);
        template <typename F, typename A, typename E>
        static no& test_two(...);

        template <typename F, typename A, typename E>
        static yes& test_fn2(char (*)[sizeof( (*(A*)0)((*(F*)0)(*(E*)0)) )]);
        template <typename F, typename A, typename E>
        static no& test_fn2(...);

    public:
        enum {
            can_call_2 = (sizeof(test_two<FN1, A1, Entry>(0)) == sizeof(yes)),
            is_fn2     = (sizeof(test_fn2<FN1, A1, Entry>(0)) == sizeof(yes))
        };
    };

    template <bool CanCall2, bool IsFn2>
    struct exec_find_if_2_dispatch {
        template <typename FN1, typename A1, typename Entry>
        static bool exec(FN1 fn1, A1 a1, const Entry& entry) {
            return fn1(entry, a1);
        }
    };

    template <>
    struct exec_find_if_2_dispatch<false, true> {
        template <typename FN1, typename A1, typename Entry>
        static bool exec(FN1 fn1, A1 a1, const Entry& entry) {
            return a1(fn1(entry));
        }
    };

    template <>
    struct exec_find_if_2_dispatch<false, false> {
        template <typename FN1, typename A1, typename Entry>
        static bool exec(FN1 fn1, A1 a1, const Entry& entry) {
            return fn1(entry) == a1;
        }
    };
}

// --- Tag structs for container dispatch ---
struct StackTag {};
struct VectorTag {};
struct ListTag {};
struct DequeTag {};

#endif