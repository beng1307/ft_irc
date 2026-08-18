#ifndef SET_HPP
#define SET_HPP

#include "Iterator.hpp"
#include "templategod.hpp"
#include "SharedBehavior.hpp"
#include <set>
#include <algorithm>
#include <iterator>

template <typename Key>
class Set : public std::set<Key> {
private:
    typedef std::set<Key>                         _set;
    typedef typename _set::iterator               _RawIter;
    typedef typename _set::const_iterator         _RawCIter;
    typedef typename _set::reverse_iterator       _RawRIter;
    typedef typename _set::const_reverse_iterator _RawCRIter;

public:
    typedef Iterator<_RawIter>          iterator;
    typedef Iterator<_RawCIter>         const_iterator;
    typedef Iterator<_RawRIter>         reverse_iterator;
    typedef Iterator<_RawCRIter>        const_reverse_iterator;

    OK_CHECK(Set)

    // --- Orthodox Canonical Form (Rule of Three - C++98) ---
    Set() : _ok(false) {}
    ~Set() {}

    // Copy from other Set
    Set(const Set& other) : _set(other), _ok(other._ok) {}
    Set& operator=(const Set& other) { _set::operator=(other); _ok = other._ok; return *this; }

    // Converting from std::set (copy only)
    Set(const _set& other) : _set(other), _ok(true) {}
    Set& operator=(const _set& other) { _set::operator=(other); _ok = true; return *this; }

    // Single key constructor
    explicit Set(const Key& key) : _ok(true) { add(key); }

    // --- Set from container + function ---
    template <typename CONTAINER, typename FN>
    Set(const CONTAINER& container, FN fn) : _ok(true) {
        typedef typename fn_return_type<FN>::type result_type;
        if (container.size() == 0) { _ok = false; return; }
        for (size_t i = 0; i < container.size(); ++i) {
            result_type content = fn(container[i]);
            if (content) {
                add(content);
            }
        }
    }

    // --- Iterators (wrapping raw → Iterator) ---
    iterator begin()                      { return iterator(_set::begin()); }
    iterator end()                        { return iterator(_set::end()).notok(); }
    const_iterator begin() const          { return const_iterator(_set::begin()); }
    const_iterator end() const            { return const_iterator(_set::end()).notok(); }
    reverse_iterator rbegin()             { return reverse_iterator(_set::rbegin()); }
    reverse_iterator rend()               { return reverse_iterator(_set::rend()).notok(); }
    const_reverse_iterator rbegin() const { return const_reverse_iterator(_set::rbegin()); }
    const_reverse_iterator rend() const   { return const_reverse_iterator(_set::rend()).notok(); }

    // --- FIND: returns Iterator with _ok flag ---
    iterator find(const Key& key) {
        _RawIter it = _set::find(key);
        if (it != _set::end())
            return iterator(it);
        return this->end();
    }

    const_iterator find(const Key& key) const {
        _RawCIter it = _set::find(key);
        if (it != _set::end())
            return const_iterator(it);
        return this->end();
    }

    // --- LOWER_BOUND / UPPER_BOUND ---
    iterator lower_bound(const Key& key) {
        _RawIter it = _set::lower_bound(key);
        if (it != _set::end())
            return iterator(it);
        return this->end();
    }

    const_iterator lower_bound(const Key& key) const {
        _RawCIter it = _set::lower_bound(key);
        if (it != _set::end())
            return const_iterator(it);
        return this->end();
    }

    iterator upper_bound(const Key& key) {
        _RawIter it = _set::upper_bound(key);
        if (it != _set::end())
            return iterator(it);
        return this->end();
    }

    const_iterator upper_bound(const Key& key) const {
        _RawCIter it = _set::upper_bound(key);
        if (it != _set::end())
            return const_iterator(it);
        return this->end();
    }

    void erase(iterator pos) {
        this->_set::erase(pos.base());
    }
    void erase(iterator first, iterator last) {
        this->_set::erase(first.base(), last.base());
    }
    size_t erase(const Key& key) {
        return this->_set::erase(key);
    }

    Set& add(const Key& key) {
        _set::insert(key);
        return *this;
    }

    Set add(const Set& b) const {
        Set result;
        std::set_union(this->_set::begin(), this->_set::end(),
                       b._set::begin(), b._set::end(),
                       std::inserter(static_cast<_set&>(result), static_cast<_set&>(result).end()));
        return result.ok();
    }
    Set add(const Set& b) {
        return static_cast<const Set*>(this)->add(b);
    }

    Set merge(const Set& b) const {
        return add(b);
    }
    Set merge(const Set& b) {
        return add(b);
    }

    Set& operator()(const Key& key) {
        add(key);
        return *this;
    }

    Set subtract(const Set& b) const {
        Set result;
        std::set_difference(this->_set::begin(), this->_set::end(),
                            b._set::begin(), b._set::end(),
                            std::inserter(static_cast<_set&>(result), static_cast<_set&>(result).end()));
        return result.ok();
    }
    Set subtract(const Set& b) {
        return static_cast<const Set*>(this)->subtract(b);
    }

    Set subtract(const Key& key) const {
        Set result(*this);
        result.erase(key);
        return result.ok();
    }
    Set subtract(const Key& key) {
        return static_cast<const Set*>(this)->subtract(key);
    }

    Set difference(const Set& b) const {
        Set result;
        std::set_symmetric_difference(this->_set::begin(), this->_set::end(),
                                      b._set::begin(), b._set::end(),
                                      std::inserter(static_cast<_set&>(result), static_cast<_set&>(result).end()));
        return result.ok();
    }
    Set difference(const Set& b) {
        return static_cast<const Set*>(this)->difference(b);
    }

    Set operator+(const Set& b) const {
        return add(b);
    }

    Set operator+(const Key& key) const {
        Set result(*this);
        result.add(key);
        return result.ok();
    }

    Set operator-(const Set& b) const {
        return subtract(b);
    }

    Set operator-(const Key& key) const {
        return subtract(key);
    }

    Set& operator+=(const Set& b) {
        *this = add(b);
        return *this;
    }

    Set& operator+=(const Key& key) {
        add(key);
        return *this;
    }

    Set& operator-=(const Set& b) {
        *this = subtract(b);
        return *this;
    }

    Set& operator-=(const Key& key) {
        erase(key);
        return *this;
    }

    // --- forEach ---
    template <typename FN>
    Set &forEach(FN fn) {
        for (_RawIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it);
        }
        return *this;
    }
    template <typename FN>
    const Set &forEach(FN fn) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it);
        }
        return *this;
    }

    template <typename FN, typename A1>
    Set &forEach(FN fn, A1 a1) {
        for (_RawIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it, a1);
        }
        return *this;
    }
    template <typename FN, typename A1>
    const Set &forEach(FN fn, A1 a1) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it, a1);
        }
        return *this;
    }

    template <typename FN, typename A1, typename A2>
    Set &forEach(FN fn, A1 a1, A2 a2) {
        for (_RawIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it, a1, a2);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2>
    const Set &forEach(FN fn, A1 a1, A2 a2) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it, a1, a2);
        }
        return *this;
    }

    template <typename FN, typename A1, typename A2, typename A3>
    Set &forEach(FN fn, A1 a1, A2 a2, A3 a3) {
        for (_RawIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it, a1, a2, a3);
        }
        return *this;
    }
    template <typename FN, typename A1, typename A2, typename A3>
    const Set &forEach(FN fn, A1 a1, A2 a3, A3 a4) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            fn(*it, a1, a3, a4);
        }
        return *this;
    }

    // --- reduce ---
    template <typename FN>
    typename fn_return_type<FN>::type reduce(FN fn) const {
        typedef typename fn_return_type<FN>::type Acc;
        Acc acc = Acc();
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            acc = fn(acc, *it);
            if (detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    template <typename Acc, typename FN>
    Acc reduce(FN fn, Acc acc) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            acc = fn(acc, *it);
            if (detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    template <typename Acc, typename FN, typename A1>
    Acc reduce(FN fn, Acc acc, A1 a1) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            acc = fn(acc, *it, a1);
            if (detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }

    template <typename Acc, typename FN, typename A1, typename A2>
    Acc reduce(FN fn, Acc acc, A1 a1, A2 a2) const {
        for (_RawCIter it = this->_set::begin(); it != this->_set::end(); ++it) {
            acc = fn(acc, *it, a1, a2);
            if (detail::break_if_falsy<detail::is_boolable<Acc>::value, Acc>::check(acc)) break;
        }
        return acc;
    }
};

#endif // SET_HPP
