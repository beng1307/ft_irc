#ifndef ITERATOR_HPP
#define ITERATOR_HPP

#include <iterator>


template <typename IteratorT>
class Iterator : public std::iterator<
    typename std::iterator_traits<IteratorT>::iterator_category,  // e.g. std::forward_iterator_tag
    typename std::iterator_traits<IteratorT>::value_type,         // the element type
    typename std::iterator_traits<IteratorT>::difference_type,    // usually ptrdiff_t
    typename std::iterator_traits<IteratorT>::pointer,            // T*
    typename std::iterator_traits<IteratorT>::reference           // T&
> {
private:
    IteratorT _current;
    bool      _ok;

public:
    // --- Orthodox Canonical Form ---
    Iterator() : _current(), _ok(false) {}
    Iterator(const Iterator& other) : _current(other._current), _ok(other._ok) {}
    Iterator& operator=(const Iterator& other) {
        if (this != &other) {
            _current = other._current;
            _ok = other._ok;
        }
        return *this;
    }
    ~Iterator() {}

    // --- Construction ---
    explicit Iterator(const IteratorT& it) : _current(it), _ok(true) {}

    // --- Your requested API ---
    operator bool() const { return _ok; }       // if (it) { ... }
    Iterator& ok() { _ok = true; return *this; } // it.ok() enables the iterator

    // --- Optional: manually invalidate ---
    Iterator& notok() { _ok = false; return *this; }

    // --- Access the underlying iterator ---
    IteratorT base() const { return _current; }

    // --- Forward iterator operations ---
    Iterator& operator++() { ++_current; return *this; }
    Iterator  operator++(int) { Iterator tmp(*this); ++_current; return tmp; }
    Iterator& operator--() { --_current; return *this; }
    Iterator  operator--(int) { Iterator tmp(*this); --_current; return tmp; }

    // --- Dereference ---
    typename std::iterator_traits<IteratorT>::reference operator*()  const { return *_current; }
    typename std::iterator_traits<IteratorT>::pointer   operator->() const { return &(*_current); }

    // --- value() accessor (alias for operator*) ---
    typename std::iterator_traits<IteratorT>::reference value() const { return *_current; }

    // --- Comparison (Iterator vs Iterator) ---
    bool operator==(const Iterator& other) const { return _current == other._current; }
    bool operator!=(const Iterator& other) const { return _current != other._current; }

    // --- Cross-type comparison (Iterator vs raw iterator) ---
    bool operator==(const IteratorT& raw) const { return _current == raw; }
    bool operator!=(const IteratorT& raw) const { return _current != raw; }

    // --- Random access iterator operations ---
    typename std::iterator_traits<IteratorT>::difference_type
    operator-(const Iterator& other) const { return _current - other._current; }

    template <typename N>
    Iterator operator+(N n) const {
        Iterator tmp(*this); tmp._current += static_cast<
            typename std::iterator_traits<IteratorT>::difference_type>(n); return tmp;
    }
    template <typename N>
    Iterator operator-(N n) const {
        Iterator tmp(*this); tmp._current -= static_cast<
            typename std::iterator_traits<IteratorT>::difference_type>(n); return tmp;
    }
    template <typename N>
    Iterator& operator+=(N n) { _current += static_cast<
            typename std::iterator_traits<IteratorT>::difference_type>(n); return *this; }
    template <typename N>
    Iterator& operator-=(N n) { _current -= static_cast<
            typename std::iterator_traits<IteratorT>::difference_type>(n); return *this; }

    typename std::iterator_traits<IteratorT>::reference
    operator[](typename std::iterator_traits<IteratorT>::difference_type n) const { return _current[n]; }

    bool operator<(const Iterator& other) const { return _current < other._current; }
    bool operator>(const Iterator& other) const { return _current > other._current; }
    bool operator<=(const Iterator& other) const { return _current <= other._current; }
    bool operator>=(const Iterator& other) const { return _current >= other._current; }
};

// --- Free-function cross-type comparison (raw iterator vs Iterator) ---
template <typename IterT>
bool operator==(const IterT& raw, const Iterator<IterT>& it) { return it.base() == raw; }

template <typename IterT>
bool operator!=(const IterT& raw, const Iterator<IterT>& it) { return it.base() != raw; }

// --- Free-function n + it (commutative addition) ---
template <typename IterT, typename N>
Iterator<IterT> operator+(N n, const Iterator<IterT>& it) {
    return Iterator<IterT>(it.base() + static_cast<
        typename std::iterator_traits<IterT>::difference_type>(n));
}

#endif // ITERATOR_HPP