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

    void add(const Key& key) {
        _set::insert(key);
    }

    Set add(const Set& b) const {
        Set result;
        std::set_union(this->_set::begin(), this->_set::end(),
                       b._set::begin(), b._set::end(),
                       std::inserter(static_cast<_set&>(result), static_cast<_set&>(result).end()));
        return result.ok();
    }

    Set merge(const Set& b) const {
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

    Set subtract(const Key& key) const {
        Set result(*this);
        result.erase(key);
        return result.ok();
    }

    Set difference(const Set& b) const {
        Set result;
        std::set_symmetric_difference(this->_set::begin(), this->_set::end(),
                                      b._set::begin(), b._set::end(),
                                      std::inserter(static_cast<_set&>(result), static_cast<_set&>(result).end()));
        return result.ok();
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
};

#endif // SET_HPP
