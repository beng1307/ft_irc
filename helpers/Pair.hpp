#ifndef PAIR_HPP
#define PAIR_HPP

#include <utility>
#include "SharedBehavior.hpp"

template <typename A, typename B>
struct Pair {
    typedef A first_type;
    typedef B second_type;
    A first;
    B second;
    Pair() : first(), second(), _ok(false) {}
    Pair(const Pair& other) : first(other.first), second(other.second), _ok(other._ok) {}
    Pair& operator=(const Pair& other) {
        if (this != &other) {
            first = other.first;
            second = other.second;
            _ok = other._ok;
        }
        return *this;
    }
    ~Pair() {}
    Pair(const A& f, const B& s) : first(f), second(s), _ok(true) {}
    OK_CHECK(Pair)
    operator std::pair<const A, B>() const {
        return std::pair<const A, B>(first, second);
    }
};

#endif // PAIR_HPP
