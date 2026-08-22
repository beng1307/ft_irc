#ifndef INT_HPP
#define INT_HPP

#include <iostream>
#include "SharedBehavior.hpp"

class Wire;

#define MAKE_VAL_TYPE(NAME, INNER)                                              \
struct NAME {                                                                    \
    INNER val;                                                                   \
    OK_CHECK(NAME);                                                              \
                                                                                 \
    NAME() : val(0) { _ok = false; }                                            \
    NAME(const NAME& other) : val(other.val) { _ok = other._ok; }                \
    NAME& operator=(const NAME& other) {                                         \
        if (this != &other) { val = other.val; _ok = other._ok; }                \
        return *this;                                                            \
    }                                                                            \
    ~NAME() {}                                                                   \
    NAME(INNER v) : val(v) { _ok = true; }                                       \
                                                                                 \
    bool isZero() { return val == INNER(0); }                                    \
    /* implemented in Wire due to include order */                               \
    Wire toStr() const;                                                          \
                                                                                 \
    /* implicit conversion to INNER and numeric types */                         \
    operator INNER() const { return val; }                                       \
    operator unsigned int() const { return static_cast<unsigned int>(val); }     \
    operator long() const { return static_cast<long>(val); }                     \
    operator unsigned long() const { return static_cast<unsigned long>(val); }   \
                                                                                 \
    /* arithmetic: returns NAME, propagates _ok */                               \
    NAME operator+(const NAME& rhs) const {                                      \
        if (!_ok || !rhs._ok) return NAME();                                     \
        return NAME(val + rhs.val);                                              \
    }                                                                            \
    NAME operator-(const NAME& rhs) const {                                      \
        if (!_ok || !rhs._ok) return NAME();                                     \
        return NAME(val - rhs.val);                                              \
    }                                                                            \
    NAME operator*(const NAME& rhs) const {                                      \
        if (!_ok || !rhs._ok) return NAME();                                     \
        return NAME(val * rhs.val);                                              \
    }                                                                            \
    NAME operator/(const NAME& rhs) const {                                      \
        if (!_ok || !rhs._ok || rhs.val == 0) return NAME();                     \
        return NAME(val / rhs.val);                                              \
    }                                                                            \
                                                                                 \
    /* raw INNER arithmetic */                                                   \
    NAME operator+(INNER rhs) const { return *this + NAME(rhs); }                \
    NAME operator-(INNER rhs) const { return *this - NAME(rhs); }                \
    NAME operator*(INNER rhs) const { return *this * NAME(rhs); }                \
    NAME operator/(INNER rhs) const { return *this / NAME(rhs); }                \
                                                                                 \
    /* compound assignment */                                                    \
    NAME& operator+=(const NAME& rhs) { *this = *this + rhs; return *this; }     \
    NAME& operator-=(const NAME& rhs) { *this = *this - rhs; return *this; }     \
    NAME& operator*=(const NAME& rhs) { *this = *this * rhs; return *this; }     \
    NAME& operator/=(const NAME& rhs) { *this = *this / rhs; return *this; }     \
                                                                                 \
    /* increment / decrement */                                                  \
    NAME& operator++() { if (_ok) ++val; return *this; }                         \
    NAME& operator--() { if (_ok) --val; return *this; }                         \
    NAME operator++(int) { NAME temp(*this); if (_ok) ++val; return temp; }      \
    NAME operator--(int) { NAME temp(*this); if (_ok) --val; return temp; }      \
                                                                                 \
    /* comparison with NAME */                                                   \
    bool operator==(const NAME& rhs) const { return _ok && rhs._ok && val == rhs.val; } \
    bool operator!=(const NAME& rhs) const { return !(*this == rhs); }           \
    bool operator<(const NAME& rhs)  const { return _ok && rhs._ok && val < rhs.val; }  \
    bool operator>(const NAME& rhs)  const { return _ok && rhs._ok && val > rhs.val; }  \
    bool operator<=(const NAME& rhs) const { return !(*this > rhs); }            \
    bool operator>=(const NAME& rhs) const { return !(*this < rhs); }            \
    /* comparison with raw INNER */                                             \
    bool operator==(INNER rhs) const { return _ok && val == rhs; }               \
    bool operator!=(INNER rhs) const { return !(*this == rhs); }                 \
    bool operator<(INNER rhs)  const { return _ok && val < rhs; }                \
    bool operator>(INNER rhs)  const { return _ok && val > rhs; }                \
    bool operator<=(INNER rhs) const { return !(*this > rhs); }                  \
    bool operator>=(INNER rhs) const { return !(*this < rhs); }                  \
                                                                                 \
    /* stream */                                                                 \
    friend std::ostream& operator<<(std::ostream& os, const NAME& v) {           \
        if (v._ok) os << v.val; else os << "NaN";                                \
        return os;                                                               \
    }                                                                            \
};                                                                               \
inline NAME operator+(INNER lhs, const NAME& rhs) { return NAME(lhs) + rhs; }    \
inline NAME operator-(INNER lhs, const NAME& rhs) { return NAME(lhs) - rhs; }    \
inline NAME operator*(INNER lhs, const NAME& rhs) { return NAME(lhs) * rhs; }    \
inline NAME operator/(INNER lhs, const NAME& rhs) { return NAME(lhs) / rhs; }    \
inline bool operator==(INNER lhs, const NAME& rhs) { return rhs == lhs; }        \
inline bool operator!=(INNER lhs, const NAME& rhs) { return rhs != lhs; }        \
inline bool operator<(INNER lhs, const NAME& rhs)  { return rhs > lhs; }         \
inline bool operator>(INNER lhs, const NAME& rhs)  { return rhs < lhs; }         \
inline bool operator<=(INNER lhs, const NAME& rhs) { return rhs >= lhs; }        \
inline bool operator>=(INNER lhs, const NAME& rhs) { return rhs <= lhs; }        \


MAKE_VAL_TYPE(Int, int)

/* modulo: integer-only, can't be in the macro (float has no %) */
inline Int operator%(const Int& lhs, const Int& rhs) {
    if (!lhs || !rhs || rhs.val == 0) return Int();
    return Int(lhs.val % rhs.val);
}

MAKE_VAL_TYPE(Float, float)

#endif // INT_HPP
