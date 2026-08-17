#ifndef SHARED_BEHAVIOR_HPP
#define SHARED_BEHAVIOR_HPP

#include <iostream>
#include <string>

namespace detail {
    template <typename T>
    struct has_empty_method {
    private:
        typedef char yes[1];
        typedef char no[2];

        template <typename U>
        static yes& test(char (*)[sizeof(((U*)0)->empty())]);

        template <typename U>
        static no& test(...);

    public:
        enum { value = (sizeof(test<T>(0)) == sizeof(yes)) };
    };

    template <bool HasEmpty, typename T>
    struct log_empty_helper {
        static void log(const T& obj, const std::string& msg, const char* class_name) {
            if (obj.empty()) {
                if (msg.empty())
                    std::cerr << class_name << " is empty." << std::endl;
                else
                    std::cerr << msg << std::endl;
            }
        }
    };

    template <typename T>
    struct log_empty_helper<false, T> {
        static void log(const T&, const std::string&, const char*) {}
    };
}

#define LOG_DIAGNOSTICS(CLASSNAME) \
    CLASSNAME& logError(std::string message = "") { \
        if (!this->_ok) { \
            if (message.empty()) \
                std::cerr << #CLASSNAME " error." << std::endl; \
            else \
                std::cerr << message << std::endl; \
        } \
        return *this; \
    } \
    CLASSNAME& logEmpty(std::string message = "") { \
        ::detail::log_empty_helper< ::detail::has_empty_method<CLASSNAME>::value, CLASSNAME>::log(*this, message, #CLASSNAME); \
        return *this; \
    }

#define OK_CHECK(CLASSNAME) \
    bool _ok;\
    operator bool() const { return _ok; }; \
    CLASSNAME& ok() { _ok = true; return *this; }; \
    CLASSNAME& notok() { _ok = false; return *this; }; \
    CLASSNAME& setok(bool val) { _ok = val; return *this; }; \
    CLASSNAME& setok(CLASSNAME val) { _ok = val._ok; return *this; }; \
    CLASSNAME copy() const { return CLASSNAME(*this).ok(); }; \
    LOG_DIAGNOSTICS(CLASSNAME)

#endif // SHARED_BEHAVIOR_HPP
